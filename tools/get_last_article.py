from services.article_api import get_latest_article

def execute():
    article = get_latest_article()
    return {
        "title": article.get("title"),
        "category": article.get("category")
    }
