from services.article_api import get_latest_article, publish_article
from services.category_service import get_next_category
from services.article_generator import generate_article

def execute():
    latest = get_latest_article()
    next_category = get_next_category(latest.get("category"))
    article = generate_article(next_category)
    result = publish_article(article)

    return {
        "status": "success",
        "article": article["title"],
        "response": result
    }
