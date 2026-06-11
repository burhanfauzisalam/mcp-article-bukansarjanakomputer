import logging

import requests
from config.settings import BASE_URL, API_KEY

HEADERS = {"X-API-KEY": API_KEY}
logger = logging.getLogger("article_generator.article_api")


def _unwrap_data_response(payload):
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]

    return payload


def get_latest_article():
    logger.info("Fetching latest article from API")
    response = requests.get(
        f"{BASE_URL}/api/articles/latest",
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    article = _unwrap_data_response(response.json())
    logger.info(
        "Latest article fetched: status_code=%s title=%s category=%s",
        response.status_code,
        article.get("title"),
        article.get("category"),
    )
    return article

def publish_article(article):
    logger.info("Publishing article: title=%s category=%s", article.get("title"), article.get("category"))
    response = requests.post(
        f"{BASE_URL}/api/articles",
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": API_KEY
        },
        json=article,
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    logger.info("Article published: status_code=%s", response.status_code)
    return result
