from datetime import date
import json
import logging

import requests
from config.settings import GEMINI_API_KEYS, GEMINI_BASE_URL

logger = logging.getLogger("article_generator.article_generator")
GEMINI_TIMEOUT = 120
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


def _generate_content_with_failover(prompt: str) -> str:
    if not GEMINI_API_KEYS:
        raise RuntimeError("No Gemini API keys configured. Set GEMINI_API_KEY or GEMINI_API_KEY1..4 in .env.")

    last_response = None
    for index, api_key in enumerate(GEMINI_API_KEYS, start=1):
        logger.info("Calling Gemini REST API: api_key_index=%s", index)
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

        if response.status_code in RETRYABLE_GEMINI_STATUS_CODES:
            last_response = response
            if index < len(GEMINI_API_KEYS):
                logger.warning(
                    "Gemini REST API returned retryable status, trying next key: status_code=%s api_key_index=%s",
                    response.status_code,
                    index,
                )
            else:
                logger.error(
                    "All Gemini API keys failed with retryable Gemini status: status_code=%s",
                    response.status_code,
                )
            continue

        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.exception("Gemini REST API request failed: status_code=%s api_key_index=%s", response.status_code, index)
            raise

        return _extract_text_from_response(response.json())

    if last_response is not None:
        last_response.raise_for_status()

    raise RuntimeError("Gemini generation failed before any request was sent.")

def generate_article(category: str):
    logger.info("Generating article with Gemini: category=%s", category)
    current_year = date.today().year
    prompt = f'''
Buat artikel blog teknologi profesional.
Kategori: {category}
Tahun saat ini: {current_year}
Persyaratan:
- Bahasa Indonesia
- Minimal 700 kata
- SEO Friendly
- HTML Full
- Gunakan tag h2 dan h3
- Jangan gunakan markdown
- Jangan gunakan tahun lama pada judul atau isi artikel kecuali sedang membahas sejarah

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
