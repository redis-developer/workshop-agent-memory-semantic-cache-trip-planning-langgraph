# %% [markdown]
# # Where what we know about a traveler is kept
#
# Long-term memory in Redis Agent Memory. Every entry has an owner (`owner_id`), and a search can say whose entries
# it may look in.
#
# - **Exercise 3A (solved):** create a long-term memory.
# - **Exercise 4A (solved):** search long-term memory.
#
# Steps B are in `ai/agent_workflow/tools/memory_tools.py`.


# %%
from typing import Literal, TypedDict
from uuid import uuid4

from redis_iris.agent_memory import models

from backend.modules.ai.agent_memory.client import agent_memory
from backend.lib.log import log

# What kind of thing an entry is:
#   - semantic: a lasting fact or preference ("vegetarian", "prefers mid-range hotels");
#   - episodic: something that happened ("visited London in spring 2025 and stayed near the center").
MemoryType = Literal["semantic", "episodic"]


class ProfileEntry(TypedDict):
    # The keys are the JSON the page reads, which is why `memoryType` is in camelCase.
    id: str
    text: str
    memoryType: MemoryType
    topics: list[str]


# How many entries a search returns when it is not told
ENTRIES_PER_SEARCH = 5


# %% [markdown]
# ## Exercise 3A (solved): create a long-term memory


# %%
async def create_long_term_memory(*, user_id: str, text: str, memory_type: MemoryType, topics: list[str] | None = None) -> models.BulkCreateLongTermMemoriesResponseContent:
    """Add one entry to a traveler's profile. Returns what Agent Memory answered: the ids it created, and any errors."""

    topics = topics or []
    response = await agent_memory.client.bulk_create_long_term_memories_async(
        memories=[{"memory_id": str(uuid4()), "text": text, "owner_id": user_id, "memory_type": memory_type, **({"topics": topics} if topics else {})}]
    )
    log(f"💾 {memory_type} memory saved for {user_id}")
    return response


# %% [markdown]
# ## Exercise 4A (solved): search long-term memory
#
# Entries are found by meaning, not by keyword. The search only looks in that traveler's entries. With a `memory_type`
# it only looks at that type of entry.


# %%
async def search_long_term_memory(*, query: str, user_id: str, memory_type: MemoryType | None = None, limit: int = ENTRIES_PER_SEARCH) -> list[ProfileEntry]:
    """
    Search a traveler's long-term memories by meaning. With a `memory_type` it only looks at that type.
    It returns the closest entries, at most `limit`.
    """

    recall = await agent_memory.arecall(query, owner=user_id, types=[memory_type] if memory_type else [], limit=limit)
    entries: list[ProfileEntry] = [
        {"id": memory.id, "text": memory.text, "memoryType": memory.memory_type or "semantic", "topics": list(memory.topics)}
        for memory in recall.memories
    ]
    log(f'🔍 Long-term memory "{query[:50]}": {len(entries)} found')
    return entries


# %% [markdown]
# ## Reading a traveler's entries, for the Memory tab


# %%
async def find_long_term_memories_by_user_id(user_id: str) -> list[ProfileEntry]:
    """A traveler's entries, for display. A search, so it returns the closest ones rather than every one."""

    return await search_long_term_memory(user_id=user_id, query="what the traveler likes and wants", limit=50)
