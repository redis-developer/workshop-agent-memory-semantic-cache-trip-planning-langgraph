import time
from typing import Callable

from langchain_core.messages import AIMessage, HumanMessage

from backend.modules.ai.agent_memory.session_memory import Conversation, Message, find_conversation_by_session_id, save_message
from backend.modules.ai.agent_workflow.graph import build_graph
from backend.modules.ai.agent_workflow.nodes import tools
from backend.modules.ai.agent_workflow.tools.maps_tools import load_maps_tools
from backend.modules.ai.agent_workflow.stream_events import STREAM_MODES, TurnEvent, read_run
from backend.modules.ai.agent_workflow.usage import UsageCallbackHandler
from backend.lib.log import log

__all__ = ["TurnEvent", "start_agent", "stream_agent_turn"]

graph = None


async def start_agent() -> None:
    """Build the agent. It is built when the app starts, because Google's tools are loaded from its server."""

    global graph
    # Google's tools come from its server, so they are added to the agent's tools before the graph is built
    tools.extend(await load_maps_tools())
    graph = build_graph()


# %% [markdown]
# ## Exercise 2B (solved): remember the conversation
#
# A session is one conversation. `stream_agent_turn` loads it before the agent runs, and saves the turn after,
# using the calls you wrote in step A (`agent_memory/session_memory.py`). Try it:
#
# - Ask "I'm going to Tokyo", then "which city did I just ask about?". Then press New session and ask again.
# - Save the turn after the model call, not before: the question must not be in the history twice.
#
# Stretch: how much of the conversation does the agent see? `find_conversation_by_session_id` returns everything the
# service still has, and `history_for_prompt` decides what the model is given. Try changing it and watch what the
# agent forgets:
#
# - set `MAX_MESSAGES_IN_PROMPT` to 2, then ask "what city did I just say?"
# - give the model only the summary, or only the latest message
# - keep the first message as well as the last ones


# %%
MAX_MESSAGES_IN_PROMPT = 10


def history_for_prompt(conversation: Conversation) -> list[HumanMessage | AIMessage]:
    """What the model is given: the latest messages of the conversation."""

    return [
        HumanMessage(entry["content"]) if entry["role"] == "user" else AIMessage(entry["content"])
        for entry in conversation["messages"][-MAX_MESSAGES_IN_PROMPT:]
    ]


async def save_turn(session_id: str, user_id: str, messages: list[Message]) -> None:
    """Add this turn's messages to the conversation."""

    log(f"save_turn: {len(messages)} messages")
    for message in messages:
        await save_message(session_id, user_id, message)


async def stream_agent_turn(*, user_id: str, session_id: str, message: str, send: Callable[[TurnEvent], None]) -> str:
    """
    One turn: load the conversation, run the agent for one message and stream what it does to `send`, then save what
    was said. Returns the finished reply.
    """

    conversation = await find_conversation_by_session_id(session_id)

    usage_handler = UsageCallbackHandler()
    started_at = time.perf_counter()
    stream = graph.astream(
        {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [*history_for_prompt(conversation), HumanMessage(message)],
            "conversation_summary": conversation["summary"],
            "long_term_memories": [],
            "attachments": [],
            "is_cache_hit": False,
        },
        # `configurable` is how the tools learn who is asking. The handler adds up the tokens of every model call.
        {"configurable": {"user_id": user_id, "session_id": session_id}, "recursion_limit": 12, "callbacks": [usage_handler]},
        stream_mode=STREAM_MODES,
        version="v2",
    )
    final_state = await read_run(stream, send)
    send({"type": "usage", "usage": usage_handler.usage, "responseTime": time.perf_counter() - started_at, "isCacheHit": final_state.get("is_cache_hit", False)})

    # The last message of the finished run is the reply.
    reply = final_state["messages"][-1].text
    if reply:
        await save_turn(session_id, user_id, [{"role": "user", "content": message}, {"role": "assistant", "content": reply}])
    return reply
