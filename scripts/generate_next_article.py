import json
import logging
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.logging_config import setup_logging
from tools.generate_article import execute


setup_logging()
logger = logging.getLogger("article_generator.cron")


def main() -> int:
    logger.info("Cron generate_next_article started")
    try:
        result = execute()
    except Exception:
        logger.exception("Cron generate_next_article failed")
        return 1

    logger.info(
        "Cron generate_next_article completed: article=%s category=%s status=%s",
        result.get("article"),
        result.get("category"),
        result.get("status"),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
