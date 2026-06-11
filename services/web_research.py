import logging
from datetime import date

import requests

from config.settings import (
    TAVILY_API_KEY,
    WEB_RESEARCH_ENABLED,
    WEB_RESEARCH_COUNTRY,
    WEB_RESEARCH_EXCLUDE_DOMAINS,
    WEB_RESEARCH_MAX_RESULTS,
    WEB_RESEARCH_PROVIDER,
    WEB_RESEARCH_REQUIRED,
    WEB_RESEARCH_SEARCH_DEPTH,
    WEB_RESEARCH_TIMEOUT,
    WEB_RESEARCH_TIME_RANGE,
)


logger = logging.getLogger("article_generator.web_research")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def _normalize_text(value: str | None, max_length: int = 900) -> str:
    if not value:
        return ""

    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized

    return normalized[:max_length].rsplit(" ", 1)[0].strip() + "..."


def _build_query(category: str, topic: str | None = None) -> str:
    current_year = date.today().year
    if topic:
        return f"{topic} {category} latest article blog guide best practices {current_year}"

    return f"latest {category} technology article blog trends best practices {current_year}"


def _search_tavily(query: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if TAVILY_API_KEY:
        headers["Authorization"] = f"Bearer {TAVILY_API_KEY}"
    else:
        headers["X-Tavily-Access-Mode"] = "keyless"

    payload = {
        "query": query,
        "topic": "general",
        "search_depth": WEB_RESEARCH_SEARCH_DEPTH,
        "time_range": WEB_RESEARCH_TIME_RANGE,
        "max_results": WEB_RESEARCH_MAX_RESULTS,
        "include_answer": False,
        "include_raw_content": False,
        "include_images": False,
    }
    if WEB_RESEARCH_COUNTRY:
        payload["country"] = WEB_RESEARCH_COUNTRY
    if WEB_RESEARCH_EXCLUDE_DOMAINS:
        payload["exclude_domains"] = WEB_RESEARCH_EXCLUDE_DOMAINS

    response = requests.post(
        TAVILY_SEARCH_URL,
        headers=headers,
        json=payload,
        timeout=WEB_RESEARCH_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _normalize_tavily_results(payload: dict) -> list[dict]:
    references = []
    seen_urls = set()

    for item in payload.get("results", []):
        url = item.get("url")
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        references.append(
            {
                "title": _normalize_text(item.get("title"), 180),
                "url": url,
                "summary": _normalize_text(item.get("content"), 900),
                "score": item.get("score"),
            }
        )

    return references


def research_references(category: str, topic: str | None = None) -> dict:
    if not WEB_RESEARCH_ENABLED:
        logger.info("Web research skipped because WEB_RESEARCH_ENABLED=false")
        return {
            "status": "disabled",
            "provider": WEB_RESEARCH_PROVIDER,
            "query": None,
            "references": [],
        }

    query = _build_query(category, topic)
    logger.info(
        "Starting web research: provider=%s category=%s topic=%s query=%s",
        WEB_RESEARCH_PROVIDER,
        category,
        topic,
        query,
    )

    try:
        if WEB_RESEARCH_PROVIDER != "tavily":
            raise ValueError(f"Unsupported WEB_RESEARCH_PROVIDER: {WEB_RESEARCH_PROVIDER}")

        payload = _search_tavily(query)
        references = _normalize_tavily_results(payload)
    except Exception as exc:
        logger.exception("Web research failed: query=%s", query)
        if WEB_RESEARCH_REQUIRED:
            raise

        return {
            "status": "failed",
            "provider": WEB_RESEARCH_PROVIDER,
            "query": query,
            "error": str(exc),
            "references": [],
        }

    logger.info("Web research completed: query=%s references=%s", query, len(references))
    return {
        "status": "success",
        "provider": WEB_RESEARCH_PROVIDER,
        "query": query,
        "references": references,
    }
