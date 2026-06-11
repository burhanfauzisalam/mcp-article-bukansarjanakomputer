from datetime import date
import json
import logging
import time

import requests
from config.settings import (
    GEMINI_API_KEYS,
    GEMINI_BASE_URL,
    GEMINI_MAX_ATTEMPTS_PER_KEY,
    GEMINI_MAX_RETRY_DELAY_SECONDS,
    GEMINI_RETRY_DELAY_SECONDS,
    GEMINI_TIMEOUT,
)

logger = logging.getLogger("article_generator.article_generator")
RETRYABLE_GEMINI_STATUS_CODES = {429, 500, 502, 503, 504}


def _extract_text_from_response(payload: dict) -> str:
    candidates = payload.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini response does not contain candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if not text_parts:
        raise RuntimeError("Gemini response does not contain text.")

    return "".join(text_parts)


def _response_error_summary(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text[:300].replace("\n", " ")
        return f"status_code={response.status_code} body={text}"

    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    message = error.get("message") or response.text[:300].replace("\n", " ")
    status = error.get("status")

    parts = [f"status_code={response.status_code}"]
    if status:
        parts.append(f"gemini_status={status}")
    if message:
        parts.append(f"message={message}")

    return " ".join(parts)


def _retry_delay(attempt: int) -> float:
    delay = GEMINI_RETRY_DELAY_SECONDS * (2 ** max(0, attempt - 1))
    return min(delay, GEMINI_MAX_RETRY_DELAY_SECONDS)


def _generate_content_with_failover(prompt: str) -> str:
    if not GEMINI_API_KEYS:
        raise RuntimeError("No Gemini API keys configured. Set GEMINI_API_KEY or GEMINI_API_KEY1..4 in .env.")

    last_error = "No Gemini request was sent."
    for index, api_key in enumerate(GEMINI_API_KEYS, start=1):
        for attempt in range(1, GEMINI_MAX_ATTEMPTS_PER_KEY + 1):
            logger.info(
                "Calling Gemini REST API: api_key_index=%s attempt=%s/%s",
                index,
                attempt,
                GEMINI_MAX_ATTEMPTS_PER_KEY,
            )
            try:
                response = requests.post(
                    GEMINI_BASE_URL,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key,
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {"text": prompt}
                                ]
                            }
                        ],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.7,
                            "maxOutputTokens": 8192,
                            "thinkingConfig": {
                                "thinkingBudget": 0
                            },
                        },
                    },
                    timeout=GEMINI_TIMEOUT,
                )
            except requests.RequestException as exc:
                last_error = f"request_error={exc}"
                logger.warning(
                    "Gemini REST API request error: api_key_index=%s attempt=%s/%s error=%s",
                    index,
                    attempt,
                    GEMINI_MAX_ATTEMPTS_PER_KEY,
                    exc,
                )
            else:
                if response.status_code in RETRYABLE_GEMINI_STATUS_CODES:
                    last_error = _response_error_summary(response)
                    logger.warning(
                        "Gemini REST API returned retryable status: api_key_index=%s attempt=%s/%s %s",
                        index,
                        attempt,
                        GEMINI_MAX_ATTEMPTS_PER_KEY,
                        last_error,
                    )
                else:
                    try:
                        response.raise_for_status()
                    except requests.HTTPError as exc:
                        last_error = _response_error_summary(response)
                        logger.error(
                            "Gemini REST API request failed: api_key_index=%s %s",
                            index,
                            last_error,
                        )
                        raise RuntimeError(f"Gemini REST API request failed: {last_error}") from exc

                    return _extract_text_from_response(response.json())

            if attempt < GEMINI_MAX_ATTEMPTS_PER_KEY:
                delay = _retry_delay(attempt)
                logger.info("Retrying Gemini request after %.1f seconds", delay)
                time.sleep(delay)

        if index < len(GEMINI_API_KEYS):
            logger.warning("Trying next Gemini API key after failure: api_key_index=%s", index)

    logger.error("All Gemini API keys failed: %s", last_error)
    raise RuntimeError(
        "All Gemini API keys failed. Last Gemini error: "
        f"{last_error}. If this is status_code=429, the keys are rate limited or quota exhausted."
    )

def _format_references_for_prompt(references: list[dict] | None) -> str:
    if not references:
        return "Tidak ada referensi web yang tersedia. Buat artikel berdasarkan pengetahuan umum yang relevan."

    lines = [
        "Gunakan referensi web terbaru berikut sebagai konteks fakta dan tren.",
        "Jangan menyalin kalimat dari referensi. Tulis artikel baru dengan struktur dan gaya original.",
    ]
    for index, reference in enumerate(references, start=1):
        lines.extend(
            [
                f"{index}. Judul: {reference.get('title') or '-'}",
                f"   URL: {reference.get('url') or '-'}",
                f"   Ringkasan: {reference.get('summary') or '-'}",
            ]
        )

    return "\n".join(lines)


def generate_article(category: str, topic: str | None = None, references: list[dict] | None = None):
    logger.info("Generating article with Gemini: category=%s topic=%s", category, topic)
    current_year = date.today().year
    topic_instruction = f"Topik utama: {topic}" if topic else "Topik utama: tentukan berdasarkan kategori."
    reference_instruction = _format_references_for_prompt(references)
    prompt = f'''
Buat artikel blog teknologi profesional.
Kategori: {category}
{topic_instruction}
Tahun saat ini: {current_year}
Referensi:
{reference_instruction}

Persyaratan:
- Bahasa Indonesia
- Minimal 700 kata
- SEO Friendly
- HTML Full
- Gunakan tag h2 dan h3
- Jangan gunakan markdown
- Jangan gunakan tahun lama pada judul atau isi artikel kecuali sedang membahas sejarah
- Judul, excerpt, dan isi harus fokus pada topik utama
- Utamakan fakta dari referensi terbaru jika tersedia
- Jangan membuat klaim sumber palsu atau URL palsu
- Jika menyebut data/fakta spesifik dari referensi, sebutkan nama sumbernya secara natural di isi artikel

Output HARUS JSON valid:
{{
  "title": "",
  "category": "{category}",
  "excerpt": "",
  "content": ""
}}
'''
    response_text = _generate_content_with_failover(prompt)

    text = response_text.replace("```json", "").replace("```", "").strip()
    article = json.loads(text)
    article["published_at"] = str(date.today())
    logger.info(
        "Article generated: title=%s category=%s published_at=%s",
        article.get("title"),
        article.get("category"),
        article.get("published_at"),
    )
    return article
