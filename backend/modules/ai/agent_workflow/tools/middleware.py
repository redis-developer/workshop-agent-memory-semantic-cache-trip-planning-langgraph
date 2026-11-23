"""
What happens around every tool call of the tools node: the tool runs, then what it returned is turned into cards for
the page and into a one-line note about what it did.
This is boilerplate. You do not need to change anything here.
"""

from langgraph.config import get_stream_writer
from langgraph.types import Command

from backend.modules.ai.agent_workflow.utils import maps_attachments, memories_info, read_tool_result


def tool_info(message, cards: list) -> str:
    """One line for the page on what a tool call did, such as "Found 5 places"."""
    if message.status == "error":
        return "The tool failed"
    result = read_tool_result(message)
    if message.name == "search_places":
        return f"Found {len(cards)} places" if cards else "No places found"
    if message.name == "lookup_weather":
        return f"{cards[0]['data']['condition']}, {cards[0]['data']['temperature']}" if cards else "No weather found"
    if message.name == "search_memories":
        return memories_info(len(result))
    if message.name == "save_memory":
        return "Saved to long-term memory" if result.get("created") else "Not saved"
    return ""


async def process_tool_call(request, execute):
    """
    Wraps each tool call of the tools node (`ToolNode(tools, awrap_tool_call=process_tool_call)`). The tool runs as
    usual (`execute`), and what the call returns is also turned into cards, which are added to `state["attachments"]`.
    Only the Google Maps tools make cards: for the other tools the list is empty.
    It also tells the page what the call did: the key says which call, so two tools running together do not mix.
    """
    result = await execute(request)
    cards = maps_attachments([result])
    get_stream_writer()({"key": request.tool_call["id"], "info": tool_info(result, cards)})
    return Command(update={"messages": [result], "attachments": cards})
