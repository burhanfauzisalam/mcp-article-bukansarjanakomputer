from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging
import os

from config.logging_config import setup_logging
from tools.get_last_article import execute as get_last
from tools.generate_article import execute as generate
from tools.generate_article_by_topic import execute as generate_by_topic
from tools.publish_article import execute as publish

setup_logging()
logger = logging.getLogger("article_generator.server")

SERVER_NAME = "bukansarjanakomputer-blog"
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("PORT", os.getenv("MCP_PORT", "3000")))
MCP_ENDPOINT = os.getenv("MCP_ENDPOINT", "/")
HEALTH_PATH = os.getenv("HEALTH_PATH", "/healthz")
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")

mcp = FastMCP(
    SERVER_NAME,
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_ENDPOINT,
    log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    stateless_http=os.getenv("MCP_STATELESS_HTTP", "true").lower() in {"1", "true", "yes"},
)


@mcp.custom_route(HEALTH_PATH, methods=["GET"])
async def health_check(_request: Request):
    return JSONResponse({
        "ok": True,
        "service": SERVER_NAME,
        "mcpEndpoint": MCP_ENDPOINT,
    })

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
        logger.info(
            "Tool generate_next_article completed: article=%s category=%s status=%s",
            result.get("article"),
            result.get("category"),
            result.get("status"),
        )
        return result
    except Exception:
        logger.exception("Tool generate_next_article failed")
        raise

@mcp.tool()
def generate_article_by_topic(topic: str):
    logger.info("Tool generate_article_by_topic started: topic=%s", topic)
    try:
        result = generate_by_topic(topic)
        logger.info(
            "Tool generate_article_by_topic completed: topic=%s article=%s category=%s status=%s",
            topic,
            result.get("article"),
            result.get("category"),
            result.get("status"),
        )
        return result
    except Exception:
        logger.exception("Tool generate_article_by_topic failed: topic=%s", topic)
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
    logger.info(
        "Starting MCP server: name=%s transport=%s host=%s port=%s endpoint=%s health_path=%s",
        SERVER_NAME,
        MCP_TRANSPORT,
        MCP_HOST,
        MCP_PORT,
        MCP_ENDPOINT,
        HEALTH_PATH,
    )
    mcp.run(transport=MCP_TRANSPORT)
