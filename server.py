from mcp.server.fastmcp import FastMCP
import logging

from config.logging_config import setup_logging
from tools.get_last_article import execute as get_last
from tools.generate_article import execute as generate
from tools.publish_article import execute as publish

setup_logging()
logger = logging.getLogger("article_generator.server")

mcp = FastMCP("bukansarjanakomputer-blog")

@mcp.tool()
def get_last_article():
    logger.info("Tool get_last_article started")
    try:
        result = get_last()
        logger.info("Tool get_last_article completed: title=%s category=%s", result.get("title"), result.get("category"))
        return result
    except Exception:
        logger.exception("Tool get_last_article failed")
        raise

@mcp.tool()
def generate_next_article():
    logger.info("Tool generate_next_article started")
    try:
        result = generate()
        logger.info("Tool generate_next_article completed: title=%s category=%s", result.get("title"), result.get("category"))
        return result
    except Exception:
        logger.exception("Tool generate_next_article failed")
        raise

@mcp.tool()
def publish_next_article():
    logger.info("Tool publish_next_article started")
    try:
        result = publish()
        logger.info("Tool publish_next_article completed: article=%s status=%s", result.get("article"), result.get("status"))
        return result
    except Exception:
        logger.exception("Tool publish_next_article failed")
        raise

if __name__ == "__main__":
    logger.info("Starting MCP server: bukansarjanakomputer-blog")
    mcp.run()
