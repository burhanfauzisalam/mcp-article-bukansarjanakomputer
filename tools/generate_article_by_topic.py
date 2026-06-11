from services.article_api import publish_article
from services.article_generator import generate_article
from services.category_service import select_category_for_topic


def execute(topic: str):
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("Topic is required.")

    category = select_category_for_topic(normalized_topic)
    article = generate_article(category, normalized_topic)
    result = publish_article(article)

    return {
        "status": "success",
        "article": article.get("title"),
        "category": article.get("category"),
        "requested_topic": normalized_topic,
        "selected_category": category,
        "published_at": article.get("published_at"),
        "response": result,
    }
