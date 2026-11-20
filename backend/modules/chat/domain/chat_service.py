# %% [markdown]
# # The conversation
#
# What was said so far in this chat, and one turn of the agent.
#
# **Exercise 2B** is in this file. Step A is in `data/conversation_repository.py`.
#
# A conversation is kept for as long as the session lasts. Once it gets long, the service replaces the older
# messages with a summary, so the older part of the conversation is only available as that summary.


# %%
from typing import Callable, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage

from backend.lib.log import log
from backend.modules.ai.agent_workflow.index import TurnEvent, stream_agent_turn
from backend.modules.chat.data.conversation_repository import (
    delete_conversation_by_session_id,
    find_conversation_by_session_id,
    save_message,
)


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class Conversation(TypedDict):
    messages: list[Message]
    # What the service wrote about the older part of the conversation. None until there is one...
    summary: str | None


# %% [markdown]
# ## Exercise 2B: remember the conversation
#
# **What to do:** load the conversation from the session, and save each turn to it. Use the calls you wrote in
# step A (`data/conversation_repository.py`).
#
# A session is one conversation. These two functions load it and save it, using the calls you wrote in step A
# (`data/conversation_repository.py`). Try it:
#
# - Ask "I'm going to Tokyo", then "which city did I just ask about?". Then press New session and ask again.
# - Save the turn after the model call, not before: the question must not be in the history twice.


# %%
async def get_conversation(session_id: str) -> Conversation:
    """The conversation of this session: what was said so far, and the summary of the older part."""
    log("get_conversation")
    # TODO (Exercise 2B): return the conversation of this session, with `find_conversation_by_session_id`.
    # Until you write this, the agent never sees what was said before. Remove the line below when you have.
    return {"messages": [], "summary": None}


# %%
async def save_turn(session_id: str, user_id: str, messages: list[Message]) -> None:
    """Add this turn's messages to the conversation."""
    log(f"save_turn: {len(messages)} messages")
    # TODO (Exercise 2B): save each message to the session, with `save_message(session_id, user_id, message)`.


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# async def get_conversation(session_id: str) -> Conversation:
#     """The conversation of this session: what was said so far, and the summary of the older part."""
#     log("get_conversation")
#     return await find_conversation_by_session_id(session_id)
#
#
# async def save_turn(session_id: str, user_id: str, messages: list[Message]) -> None:
#     """Add this turn's messages to the conversation."""
#     log(f"save_turn: {len(messages)} messages")
#     for message in messages:
#         await save_message(session_id, user_id, message)
# ```
#
# </details>


# %% [markdown]
# ## Exercise 2B, stretch: how much of the conversation does the agent see?
#
# `get_conversation` returns everything the service still has. `history_for_prompt` decides what the model is given.
# Try changing it and watch what the agent forgets:
#
# - set `MAX_MESSAGES_IN_PROMPT` to 2, then ask "what city did I just say?"
# - give the model only the summary, or only the latest message
# - keep the first message as well as the last ones


# %%
MAX_MESSAGES_IN_PROMPT = 10


def history_for_prompt(conversation: Conversation) -> list[Message]:
    """What the model is given: the latest messages of the conversation."""
    return conversation["messages"][-MAX_MESSAGES_IN_PROMPT:]


# %% [markdown]
# ## Clearing the conversation (you can leave this as it is)


# %%
async def clear_conversation(session_id: str) -> None:
    """Delete the conversation of this session."""
    log("clear_conversation")
    await delete_conversation_by_session_id(session_id)


# %% [markdown]
# ## One turn (exercise 2B)


# %%
async def run_turn(*, user_id: str, session_id: str, message: str, send: Callable[[TurnEvent], None]) -> None:
    """One turn: load the conversation, run the agent, and save what was said."""
    conversation = await get_conversation(session_id)
    history = [
        HumanMessage(entry["content"]) if entry["role"] == "user" else AIMessage(entry["content"])
        for entry in history_for_prompt(conversation)
    ]

    reply = await stream_agent_turn(
        user_id=user_id, session_id=session_id, message=message, history=history, summary=conversation["summary"], send=send
    )

    if reply:
        await save_turn(
            session_id,
            user_id,
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply},
            ],
        )
    send({"type": "done", "reply": reply})
