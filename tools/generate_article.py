from services.article_api import get_latest_article
from services.category_service import get_next_category
from services.article_generator import generate_article

def execute():
    latest = get_latest_article()
    next_category = get_next_category(latest.get("category"))
    return generate_article(next_category)
