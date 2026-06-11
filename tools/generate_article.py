from services.article_api import get_latest_article, publish_article
from services.category_service import get_next_category
from services.article_generator import generate_article


def _publish_result(article: dict, response: dict):
    return {
        "status": "success",
        "article": article.get("title"),
        "category": article.get("category"),
        "published_at": article.get("published_at"),
        "response": response,
    }


def execute():
    latest = get_latest_article()
    next_category = get_next_category(latest.get("category"))
    article = generate_article(next_category)
    result = publish_article(article)
    return _publish_result(article, result)
