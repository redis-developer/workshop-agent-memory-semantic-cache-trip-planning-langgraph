import time
from typing import Any, AsyncIterator, Callable, Literal, TypedDict

from langchain_core.messages import AIMessageChunk

from backend.modules.ai.types import Attachment


# What the server tells the page while a turn runs. One per line of the response.
class StepEvent(TypedDict):
    type: Literal["step"]
    key: str  # tells one run of a step from another: the agent step runs again after each pass of the tools
    step: str  # the name of the node or tool
    label: str  # what the page shows for it
    status: Literal["started", "finished", "failed"]  # "failed": a tool call that raised
    input: Any  # what a tool was called with, sent when it starts
    durationMs: int  # how long the step took, sent when it finishes


class InfoEvent(TypedDict):
    type: Literal["info"]
    key: str  # the step it is about
    info: str  # what the step says about what it did, such as "Found 5 places"


class MemoriesEvent(TypedDict):
    type: Literal["memories"]
    memories: list[dict]


class TokenEvent(TypedDict):
    type: Literal["token"]
    text: str


class UsageEvent(TypedDict):
    type: Literal["usage"]
    usage: dict  # the tokens used by every model call in the turn
    responseTime: float  # seconds
    isCacheHit: bool  # the reply came from the semantic cache


class AttachmentsEvent(TypedDict):
    type: Literal["attachments"]
    attachments: list[Attachment]


class DoneEvent(TypedDict):
    type: Literal["done"]
    reply: str


class ErrorEvent(TypedDict):
    type: Literal["error"]
    message: str


TurnEvent = StepEvent | InfoEvent | MemoriesEvent | TokenEvent | AttachmentsEvent | UsageEvent | DoneEvent | ErrorEvent

# What the page shows for each step, by the name of the node or tool. A name that is not here is shown as it is.
STEP_LABELS = {
    "check_cache": "Checking if a similar question was answered",
    "retrieve_memories": "Looking up what I remember about you",
    "agent": "Thinking",
    "store_in_cache": "Deciding if this answer can be reused",
    "search_memories": "Searching your memories",
    "save_memory": "Saving a memory",
    "search_places": "Searching Google Maps for places",
    "lookup_weather": "Checking the weather",
}

# What to ask the graph to stream. "tools" is accepted by LangGraph but is not in its documented list of modes.
STREAM_MODES = ["values", "updates", "tasks", "tools", "messages", "custom"]


async def read_run(stream: AsyncIterator[dict], send: Callable[[TurnEvent], None]) -> dict:
    """
    Turn what the graph reports into events for the page.
    The stream says when each node and each tool starts and ends, each piece of the reply as it is written,
    and what each step returned as soon as it is done.
    Returns the final state of the run, which holds the reply.
    @param stream: The stream returned by the graph's `astream`
    @param send: Called with each event for the page
    """
    final_state: dict = {}
    # The cards the tools found so far this turn. Every pass of the tools adds to them.
    attachments: list[Attachment] = []
    # A tool's name comes with its start, and its end only has the call ID
    tool_names: dict[str, str] = {}
    # When each step started, to say how long it took when it finishes
    started_at: dict[str, float] = {}
    # The node that is running. A node writes its info without saying who it is, and the nodes run one at a time.
    running_node: str | None = None

    def report_step(key: str, step: str, status: str, **extra) -> None:
        label = STEP_LABELS.get(step, step)
        if status == "started":
            started_at[key] = time.perf_counter()
            send({"type": "step", "key": key, "step": step, "label": label, "status": "started", **extra})
        else:
            duration_ms = round((time.perf_counter() - started_at.pop(key, time.perf_counter())) * 1000)
            send({"type": "step", "key": key, "step": step, "label": label, "status": status, "durationMs": duration_ms})

    async for part in stream:
        kind, data = part["type"], part["data"]

        if kind == "values":
            final_state = data
        elif kind == "messages":
            # Only the agent's own reply is shown as it is written. The other model calls in the graph are not the reply.
            chunk, metadata = data
            if metadata.get("langgraph_node") == "agent" and isinstance(chunk, AIMessageChunk) and chunk.text:
                send({"type": "token", "text": chunk.text})
        elif kind == "updates":
            # What a step returned, known as soon as it is done
            for node, values in data.items():
                values = values or {}
                if node == "retrieve_memories":
                    send({"type": "memories", "memories": values.get("long_term_memories", [])})
                # A reply from the cache is complete when the step is done: its cards and its text go to the page together.
                if node == "check_cache" and values.get("is_cache_hit"):
                    if values["attachments"]:
                        send({"type": "attachments", "attachments": values["attachments"]})
                    send({"type": "token", "text": values["messages"][0].text})
                # The tools node returns one update for each tool call, with the cards it found. They are known as soon
                # as the tools are done, so they are on the page before the reply is written.
                if node == "tools":
                    found = [card for update in (values if isinstance(values, list) else [values]) for card in update.get("attachments", [])]
                    if found:
                        attachments.extend(found)
                        send({"type": "attachments", "attachments": attachments})
        elif kind == "tasks":
            # Every node of the graph starts a task and finishes it, the node name tells which. The "tools" node is
            # reported through its tool calls instead.
            if data["name"] == "tools":
                continue
            running_node = None if "result" in data else data["id"]
            report_step(data["id"], data["name"], "finished" if "result" in data else "started")
        elif kind == "custom":
            # What a step wrote with `get_stream_writer()`. A tool says which call it is about, a node does not.
            send({"type": "info", "key": data.get("key", running_node), "info": data["info"]})
        elif kind == "tools":
            if data["event"] == "tool-started":
                tool_names[data["tool_call_id"]] = data["tool_name"]
                report_step(data["tool_call_id"], data["tool_name"], "started", input=data.get("input"))
            elif data["event"] == "tool-finished":
                report_step(data["tool_call_id"], tool_names.get(data["tool_call_id"], ""), "finished")
            elif data["event"] == "tool-error":
                report_step(data["tool_call_id"], tool_names.get(data["tool_call_id"], ""), "failed")

    return final_state
