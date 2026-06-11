import requests
from config.settings import BASE_URL, API_KEY

HEADERS = {"X-API-KEY": API_KEY}

def get_latest_article():
    response = requests.get(
        f"{BASE_URL}/api/articles/latest",
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def publish_article(article):
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
    return response.json()
