# %% [markdown]
# # The conversation
#
# What the chat routes use: one turn of the agent, reading the conversation and clearing it.
#
# **Exercise 2B (solved)** is in `ai/agent_workflow/index.py`, in `stream_agent_turn`. Step A is in
# `agent_memory/session_memory.py`.
#
# A conversation is kept for as long as the session lasts. Once it gets long, the service replaces the older
# messages with a summary, so the older part of the conversation is only available as that summary.


# %%
from typing import Callable

from backend.lib.log import log
from backend.modules.ai import (
    Conversation,
    TurnEvent,
    delete_conversation_by_session_id,
    find_conversation_by_session_id,
    stream_agent_turn,
)


async def get_conversation(session_id: str) -> Conversation:
    """The conversation of this session: what was said so far, and the summary of the older part."""

    log("get_conversation")
    return await find_conversation_by_session_id(session_id)


async def clear_conversation(session_id: str) -> None:
    """Delete the conversation of this session."""

    log("clear_conversation")
    await delete_conversation_by_session_id(session_id)


async def run_turn(*, user_id: str, session_id: str, message: str, send: Callable[[TurnEvent], None]) -> None:
    """One turn: the agent loads the conversation, answers and saves it. Then tell the page it is done."""

    reply = await stream_agent_turn(user_id=user_id, session_id=session_id, message=message, send=send)
    send({"type": "done", "reply": reply})
