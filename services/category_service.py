import logging


logger = logging.getLogger("article_generator.category_service")

CATEGORIES = [
    "Web Development",
    "SEO",
    "IoT",
    "DevOps",
    "Automation",
]


CATEGORY_KEYWORDS = {
    "Web Development": [
        "api",
        "backend",
        "css",
        "frontend",
        "html",
        "javascript",
        "laravel",
        "nextjs",
        "php",
        "react",
        "tailwind",
        "typescript",
        "vue",
        "web",
        "website",
    ],
    "SEO": [
        "backlink",
        "blog",
        "content",
        "google search",
        "keyword",
        "meta",
        "ranking",
        "search engine",
        "seo",
        "serp",
        "traffic",
    ],
    "IoT": [
        "arduino",
        "device",
        "embedded",
        "esp32",
        "iot",
        "microcontroller",
        "mqtt",
        "raspberry",
        "sensor",
        "smart home",
    ],
    "DevOps": [
        "ci/cd",
        "container",
        "deploy",
        "deployment",
        "devops",
        "docker",
        "github actions",
        "kubernetes",
        "monitoring",
        "nginx",
        "pipeline",
        "server",
        "traefik",
    ],
    "Automation": [
        "automasi",
        "automation",
        "bot",
        "cron",
        "integrasi",
        "no-code",
        "rpa",
        "script",
        "task",
        "workflow",
        "zapier",
    ],
}


def get_next_category(last_category: str):
    try:
        idx = CATEGORIES.index(last_category)
        next_category = CATEGORIES[(idx + 1) % len(CATEGORIES)]
    except ValueError:
        next_category = CATEGORIES[0]

    logger.info("Next category selected: last=%s next=%s", last_category, next_category)
    return next_category


def select_category_for_topic(topic: str) -> str:
    normalized_topic = topic.lower()
    scores = {
        category: sum(1 for keyword in keywords if keyword in normalized_topic)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }

    selected_category = max(CATEGORIES, key=lambda category: scores.get(category, 0))
    if scores.get(selected_category, 0) == 0:
        selected_category = CATEGORIES[0]

    logger.info(
        "Category selected for topic: topic=%s category=%s scores=%s",
        topic,
        selected_category,
        scores,
    )
    return selected_category
