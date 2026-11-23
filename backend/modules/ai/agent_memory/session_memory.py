# %% [markdown]
# # Where a conversation is kept
#
# A conversation is a session in Redis Agent Memory. The service stores each message as an event, in order, and
# writes a summary of the older messages once the conversation gets long (you set when, in the Redis Cloud console).
#
# **Exercise 2A** is the two functions that read the session and add messages to it. Step B is in
# `ai/agent_workflow/index.py`.


# %%
from typing import Literal, TypedDict

from redis_iris.agent_memory import errors

from backend.modules.ai.agent_memory.client import agent_memory
from backend.lib.log import log


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class Conversation(TypedDict):
    messages: list[Message]
    # What the service wrote about the older part of the conversation. None until there is one...
    summary: str | None


# %% [markdown]
# ## Exercise 2A: read the session back
#
# **What to do:** read the session with `conversation.atranscript()`, and return its messages and its summary.
#
# - `agent_memory.conversation(owner=user_id, session_id=session_id)` is this traveler's conversation in this session.
# - `transcript.turns` are the messages, in order. Each is a pair: the role (`"user"` or `"assistant"`) and the text.
# - `transcript.summary` is what the service wrote about the older messages, once the conversation got long. It is not always there.
# - A session that does not exist yet is the normal first-turn case. The `except` below already handles it: it has no messages and no summary.


# %%
async def find_conversation_by_session_id(user_id: str, session_id: str) -> Conversation:
    """
    Everything the service still holds for this session: its messages, in order, and a summary of the older ones once
    the conversation got long. A session that does not exist yet is the normal first-turn case, so it gives an empty
    conversation.
    """

    try:

        # TODO start (Exercise 2A): read the session with `await agent_memory.conversation(owner=user_id, session_id=session_id).atranscript()`.
        # Return its turns as messages, and its summary.
        # Until you write this, the agent has no memory of the conversation.

        return {"messages": [], "summary": None}

        # TODO end (Exercise 2A)

    except Exception as error:
        # Not finding the session is expected on the first turn, so only report other errors.
        if not isinstance(error, errors.NotFoundErrorResponseContent):
            print(f"Could not read the session: {error}")
        return {"messages": [], "summary": None}


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# async def find_conversation_by_session_id(user_id: str, session_id: str) -> Conversation:
#     """
#     Everything the service still holds for this session: its messages, in order, and a summary of the older ones once
#     the conversation got long. A session that does not exist yet is the normal first-turn case, so it gives an empty
#     conversation.
#     """
#
#     try:
#         transcript = await agent_memory.conversation(owner=user_id, session_id=session_id).atranscript()
#         conversation: Conversation = {
#             "messages": [{"role": role, "content": text} for role, text in transcript.turns],
#             "summary": transcript.summary,
#         }
#         log(f"📥 Session {session_id}: {len(conversation['messages'])} messages")
#         if conversation["summary"]:
#             log(f"📝 Summary: {conversation['summary'][:100]}...")
#         return conversation
#     except Exception as error:
#         # Not finding the session is expected on the first turn, so only report other errors.
#         if not isinstance(error, errors.NotFoundErrorResponseContent):
#             print(f"Could not read the session: {error}")
#         return {"messages": [], "summary": None}
# ```
#
# </details>


# %% [markdown]
# ## Exercise 2A: add a message to the session
#
# **What to do:** add one message to the session with `conversation.auser(text)` for the traveler's message, or
# `conversation.aassistant(text)` for the assistant's.
#
# Every message says who it is from. The first message sets the session's owner, so it must be the traveler's.
# `auser` labels a message with the traveler, and `aassistant` with the assistant (`travel-agent`, set in
# `agent_memory/client.py`). If the assistant's replies were labeled with the traveler's ID, the service would read
# "Here are some places I recommend" as something the traveler said.


# %%
async def save_message(session_id: str, user_id: str, message: Message) -> None:
    """
    Add one message to the session. The service extracts long-term memories from the session afterwards.
    The traveler's messages are from the traveler, and the assistant's are from the assistant.
    """

    # TODO start (Exercise 2A): add the message to the session with `conversation.auser(...)` or `conversation.aassistant(...)`.
    # Until you write this, nothing is stored.

    return None

    # TODO end (Exercise 2A)


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# async def save_message(session_id: str, user_id: str, message: Message) -> None:
#     """
#     Add one message to the session. The service extracts long-term memories from the session afterwards.
#     The traveler's messages are from the traveler, and the assistant's are from the assistant.
#     """
#
#     conversation = agent_memory.conversation(owner=user_id, session_id=session_id)
#     if message["role"] == "assistant":
#         await conversation.aassistant(message["content"])
#     else:
#         await conversation.auser(message["content"])
#     log(f"💾 {message['role']} message saved to session {session_id}")
# ```
#
# </details>


# %% [markdown]
# ## Deleting a session


# %%
async def delete_conversation_by_session_id(session_id: str) -> None:
    """Delete this session, with everything in it."""

    await agent_memory.client.delete_session_memory_async(session_id=session_id)
    log(f"🗑️ Session {session_id} deleted")
