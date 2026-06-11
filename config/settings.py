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
