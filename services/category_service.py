import logging


logger = logging.getLogger("article_generator.category_service")

CATEGORIES = [
    "Web Development",
    "SEO",
    "IoT",
    "DevOps",
    "Automation",
]

def get_next_category(last_category: str):
    try:
        idx = CATEGORIES.index(last_category)
        next_category = CATEGORIES[(idx + 1) % len(CATEGORIES)]
    except ValueError:
        next_category = CATEGORIES[0]

    logger.info("Next category selected: last=%s next=%s", last_category, next_category)
    return next_category
