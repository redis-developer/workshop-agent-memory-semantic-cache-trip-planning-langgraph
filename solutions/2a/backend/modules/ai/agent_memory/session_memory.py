# %% [markdown]
# # Where a conversation is kept
#
# A conversation is a session in Redis Agent Memory. The service stores each message as an event, in order, and
# writes a summary of the older messages once the conversation gets long (you set when, in the Redis Cloud console).
#
# **Exercise 2A (solved)** is the two functions that read the session and add messages to it. Step B is in
# `ai/agent_workflow/index.py`.


# %%
from datetime import datetime, timezone
from typing import Literal, TypedDict

from redis_agent_memory.errors import NotFoundErrorResponseContent
from redis_agent_memory.models import MessageRole

from backend.modules.ai.agent_memory.client import agent_memory
from backend.lib.log import log


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class Conversation(TypedDict):
    messages: list[Message]
    # What the service wrote about the older part of the conversation. None until there is one...
    summary: str | None


# Who the assistant's messages are from. The traveler's own messages are from the traveler.
ASSISTANT_ACTOR_ID = "travel-agent"


# %% [markdown]
# ## Exercise 2A (solved): read the session back


# %%
async def find_conversation_by_session_id(session_id: str) -> Conversation:
    """
    Everything the service still holds for this session: its messages, in order, and a summary of the older ones once
    the conversation got long. A session that does not exist yet is the normal first-turn case, so it gives an empty
    conversation.
    """
    try:
        session = await agent_memory.get_session_memory_async(session_id=session_id)
        conversation: Conversation = {
            "messages": [
                {
                    "role": "assistant" if event.role == MessageRole.ASSISTANT else "user",
                    "content": "".join(part.text for part in event.content),
                }
                for event in session.events
            ],
            "summary": session.summary.text if session.summary else None,
        }
        log(f"📥 Session {session_id}: {len(conversation['messages'])} messages")
        if conversation["summary"]:
            log(f"📝 Summary: {conversation['summary'][:100]}...")
        return conversation
    except Exception as error:
        # Not finding the session is expected on the first turn, so only report other errors.
        if not isinstance(error, NotFoundErrorResponseContent):
            print(f"Could not read the session: {error}")
        return {"messages": [], "summary": None}


# %% [markdown]
# ## Exercise 2A (solved): add a message to the session
#
# Every message says who it is from (`actor_id`). The first message sets the session's owner, so it must be the
# traveler's. The assistant's replies are from the assistant: if they were labeled with the traveler's ID, the
# service would read "Here are some places I recommend" as something the traveler said.


# %%
async def save_message(session_id: str, user_id: str, message: Message) -> None:
    """
    Add one message to the session. The service extracts long-term memories from the session afterwards.
    `actor_id` says who the message is from: the traveler's ID for their messages, and ASSISTANT_ACTOR_ID for the assistant's.
    """
    is_assistant = message["role"] == "assistant"
    await agent_memory.add_session_event_async(
        session_id=session_id,
        actor_id=ASSISTANT_ACTOR_ID if is_assistant else user_id,
        role=MessageRole.ASSISTANT if is_assistant else MessageRole.USER,
        content=[{"text": message["content"]}],
        created_at=datetime.now(timezone.utc),
    )
    log(f"💾 {message['role']} message saved to session {session_id}")


# %% [markdown]
# ## Deleting a session (you can leave this as it is)


# %%
async def delete_conversation_by_session_id(session_id: str) -> None:
    """Delete this session, with everything in it."""
    await agent_memory.delete_session_memory_async(session_id=session_id)
    log(f"🗑️ Session {session_id} deleted")
