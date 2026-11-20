# %% [markdown]
# # The memory tools
#
# The tools the model calls to save and look up what it knows about the traveler. The model decides when.
#
# - **Exercise 3B (solved):** the `save_memory` tool. Step A is `create_long_term_memory` in `user/data/profile_repository.py`.
# - **Exercise 4B (solved):** the `search_memories` tool. Step A is `search_long_term_memory` in the same file.


# %%
from typing import Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from backend.lib.log import log
from backend.modules.user.data.profile_repository import create_long_term_memory, search_long_term_memory


# %% [markdown]
# ## Exercise 3B (solved): the `save_memory` tool
#
# The description is what tells the model when to use it. Try it: say "I'm vegetarian", then open the **Memory** tab.


# %%
class SaveMemoryInput(BaseModel):
    fact: str = Field(description="What to remember, written so it makes sense on its own")
    memory_type: Literal["semantic", "episodic"] = Field(
        description="'semantic' for a lasting preference, 'episodic' for something that happened on a past trip"
    )
    topics: list[str] | None = Field(default=None, description="Short labels, for example ['food', 'budget']")


@tool(
    "save_memory",
    args_schema=SaveMemoryInput,
    description=(
        "Save something about the traveler for future conversations. Use memory_type 'semantic' for a lasting preference, "
        "such as a diet, a budget or who they travel with. Use 'episodic' for something that happened on a past trip, such "
        "as where they went and where they stayed. Do not save one-off requests such as this trip's dates."
    ),
)
async def save_memory_tool(fact: str, memory_type: str, topics: list[str] | None = None, *, config: RunnableConfig):
    """Save a lasting fact about the traveler as a long-term memory, so the agent knows it in later conversations."""
    user_id = config["configurable"]["user_id"]
    log(f'save_memory: "{fact}" ({memory_type})')
    await create_long_term_memory(user_id=user_id, text=fact, memory_type=memory_type, topics=topics)
    return {"success": True, "message": "Saved. You will remember this in future conversations."}


# %% [markdown]
# ## Exercise 4B (solved): the `search_memories` tool
#
# Try it: start a new session and ask for something in different words, such as "any food restrictions I should
# remember?". The search is by meaning, not by keyword.


# %%
class SearchMemoriesInput(BaseModel):
    query: str = Field(description="What to look for, for example 'dietary requirements' or 'trips to London'")
    memory_type: Literal["semantic", "episodic"] | None = Field(
        default=None,
        description="Only look at preferences (semantic) or only at past trips (episodic). Leave out to look at both.",
    )


@tool(
    "search_memories",
    args_schema=SearchMemoriesInput,
    description=(
        "Search what the traveler has told you before, across earlier conversations: diet, budget, who they travel with, "
        "what they enjoy, and trips they have taken. Use it when a recommendation depends on their preferences or history."
    ),
)
async def search_memories_tool(query: str, memory_type: str | None = None, *, config: RunnableConfig):
    """Look up what the traveler told us before, by meaning, in their long-term memories."""
    user_id = config["configurable"]["user_id"]
    log(f'search_memories: "{query}"{f" ({memory_type})" if memory_type else ""}')
    entries = await search_long_term_memory(user_id=user_id, query=query, memory_type=memory_type)
    if entries:
        return {"found": True, "memories": [{"fact": entry["text"], "memoryType": entry["memoryType"], "topics": entry["topics"]} for entry in entries]}
    return {"found": False, "message": "No relevant memories found."}


# %% [markdown]
# ## The tools the agent gets


# %%
memory_tools = [search_memories_tool, save_memory_tool]
