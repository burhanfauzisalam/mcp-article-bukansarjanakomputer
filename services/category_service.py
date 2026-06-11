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
        return CATEGORIES[(idx + 1) % len(CATEGORIES)]
    except ValueError:
        return CATEGORIES[0]
