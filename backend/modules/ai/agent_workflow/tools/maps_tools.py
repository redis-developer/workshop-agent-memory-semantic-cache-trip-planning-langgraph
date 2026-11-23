"""
Places and weather, from Google Maps. Google runs an MCP server that describes its own tools (their names, what
they do and what they take), so there is nothing to write here: we connect, ask for the tools and give them to the
agent. This is boilerplate. You do not need to change anything here.

The functions that turn what Google returns into the cards the page shows are in `../utils.py`.
"""

import json

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from backend.config import config
from backend.lib.log import log


# The Maps tools the agent may use. The server has more, such as routes.
MAPS_TOOLS = ["search_places", "lookup_weather"]


async def log_tool_call(request: MCPToolCallRequest, handler):
    """One log line for every Google Maps tool call"""

    log(f"{request.name}: {json.dumps(request.args)}")
    return await handler(request)


async def load_maps_tools() -> list:
    """Connect to Google's server and ask for its tools. Keeps Google's own tool names, such as `search_places`."""

    client = MultiServerMCPClient(
        {
            "maps": {
                "transport": "streamable_http",
                "url": "https://mapstools.googleapis.com/mcp",
                "headers": {"X-Goog-Api-Key": config.google_maps_api_key},
            }
        },
        tool_interceptors=[log_tool_call],
    )
    return [tool for tool in await client.get_tools() if tool.name in MAPS_TOOLS]
