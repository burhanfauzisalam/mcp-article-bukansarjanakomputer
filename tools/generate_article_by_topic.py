from services.article_api import publish_article
from services.article_generator import generate_article
from services.category_service import select_category_for_topic
from services.web_research import research_references


def execute(topic: str):
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("Topic is required.")

    category = select_category_for_topic(normalized_topic)
    research = research_references(category, normalized_topic)
    article = generate_article(category, normalized_topic, references=research.get("references", []))
    result = publish_article(article)

    return {
        "status": "success",
        "article": article.get("title"),
        "category": article.get("category"),
        "requested_topic": normalized_topic,
        "selected_category": category,
        "published_at": article.get("published_at"),
        "web_research": research,
        "response": result,
    }
