from mcp.server.fastmcp import FastMCP

from tools.get_last_article import execute as get_last
from tools.generate_article import execute as generate
from tools.publish_article import execute as publish

mcp = FastMCP("bukansarjanakomputer-blog")

@mcp.tool()
def get_last_article():
    return get_last()

@mcp.tool()
def generate_next_article():
    return generate()

@mcp.tool()
def publish_next_article():
    return publish()

if __name__ == "__main__":
    mcp.run()
