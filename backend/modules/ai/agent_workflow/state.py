import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from backend.modules.chat.domain.attachments import Attachment


class AgentState(TypedDict):
    """What the agent carries through one turn."""

    user_id: str
    session_id: str
    # The conversation: what was said before (from the session), then this turn's messages.
    messages: Annotated[list[AnyMessage], add_messages]
    # What the service wrote about the older part of the conversation, if it has written something.
    conversation_summary: str | None
    # The long-term memories found for this message.
    long_term_memories: list[dict]
    # The places and weather the tools found this turn, as cards for the page. Each tool call returns only its own
    # cards, and `operator.add` joins them to the list, so the cards of one call do not replace those of another.
    attachments: Annotated[list[Attachment], operator.add]
