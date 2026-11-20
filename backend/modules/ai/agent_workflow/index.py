import time
from typing import Callable

from langchain_core.messages import AIMessage, HumanMessage

from backend.modules.ai.agent_workflow.graph import build_graph
from backend.modules.ai.agent_workflow.nodes import tools
from backend.modules.ai.agent_workflow.tools.maps_tools import load_maps_tools
from backend.modules.ai.agent_workflow.stream_events import STREAM_MODES, TurnEvent, read_run
from backend.modules.ai.agent_workflow.usage import UsageCallbackHandler

__all__ = ["TurnEvent", "start_agent", "stream_agent_turn"]

graph = None


async def start_agent() -> None:
    """Build the agent. It is built when the app starts, because Google's tools are loaded from its server."""
    global graph
    # Google's tools come from its server, so they are added to the agent's tools before the graph is built
    tools.extend(await load_maps_tools())
    graph = build_graph()


async def stream_agent_turn(
    *,
    user_id: str,
    session_id: str,
    message: str,
    history: list[HumanMessage | AIMessage],
    summary: str | None,
    send: Callable[[TurnEvent], None],
) -> str:
    """
    Run the agent for one message and stream what it does to `send`. Returns the finished reply.
    `history` is what the model is given of the conversation so far, and `summary` is what the service wrote about the older part.
    """
    usage_handler = UsageCallbackHandler()
    started_at = time.perf_counter()
    stream = graph.astream(
        {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [*history, HumanMessage(message)],
            "conversation_summary": summary,
            "long_term_memories": [],
            "attachments": [],
        },
        # `configurable` is how the tools learn who is asking. The handler adds up the tokens of every model call.
        {"configurable": {"user_id": user_id, "session_id": session_id}, "recursion_limit": 12, "callbacks": [usage_handler]},
        stream_mode=STREAM_MODES,
        version="v2",
    )
    final_state = await read_run(stream, send)
    send({"type": "usage", "usage": usage_handler.usage, "responseTime": time.perf_counter() - started_at, "cached": False})

    # The last message of the finished run is the reply.
    return final_state["messages"][-1].text
