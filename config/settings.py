from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
)
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "120"))
GEMINI_MAX_ATTEMPTS_PER_KEY = int(os.getenv("GEMINI_MAX_ATTEMPTS_PER_KEY", "1"))
GEMINI_RETRY_DELAY_SECONDS = float(os.getenv("GEMINI_RETRY_DELAY_SECONDS", "2"))
GEMINI_MAX_RETRY_DELAY_SECONDS = float(os.getenv("GEMINI_MAX_RETRY_DELAY_SECONDS", "15"))

WEB_RESEARCH_ENABLED = os.getenv("WEB_RESEARCH_ENABLED", "true").lower() in {"1", "true", "yes"}
WEB_RESEARCH_REQUIRED = os.getenv("WEB_RESEARCH_REQUIRED", "false").lower() in {"1", "true", "yes"}
WEB_RESEARCH_PROVIDER = os.getenv("WEB_RESEARCH_PROVIDER", "tavily").lower()
WEB_RESEARCH_MAX_RESULTS = int(os.getenv("WEB_RESEARCH_MAX_RESULTS", "5"))
WEB_RESEARCH_TIME_RANGE = os.getenv("WEB_RESEARCH_TIME_RANGE", "year")
WEB_RESEARCH_SEARCH_DEPTH = os.getenv("WEB_RESEARCH_SEARCH_DEPTH", "basic")
WEB_RESEARCH_TIMEOUT = int(os.getenv("WEB_RESEARCH_TIMEOUT", "30"))
WEB_RESEARCH_COUNTRY = os.getenv("WEB_RESEARCH_COUNTRY", "").strip().lower()
WEB_RESEARCH_EXCLUDE_DOMAINS = [
    domain.strip()
    for domain in os.getenv(
        "WEB_RESEARCH_EXCLUDE_DOMAINS",
        "threads.com,x.com,twitter.com,facebook.com,instagram.com,tiktok.com,pinterest.com,linkedin.com,stackoverflow.com,stackexchange.com",
    ).split(",")
    if domain.strip()
]
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def _add_unique_api_key(keys: list[str], api_key: str | None) -> None:
    if api_key and api_key not in keys:
        keys.append(api_key)


def _load_gemini_api_keys() -> list[str]:
    keys: list[str] = []

    _add_unique_api_key(keys, os.getenv("GEMINI_API_KEY"))

    for index in range(1, 5):
        _add_unique_api_key(keys, os.getenv(f"GEMINI_API_KEY_{index}"))
        _add_unique_api_key(keys, os.getenv(f"GEMINI_API_KEY{index}"))

    bulk_keys = os.getenv("GEMINI_API_KEYS", "")
    for api_key in bulk_keys.replace(";", ",").split(","):
        _add_unique_api_key(keys, api_key.strip())

    return keys


GEMINI_API_KEYS = _load_gemini_api_keys()
