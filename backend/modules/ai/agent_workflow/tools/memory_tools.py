# %% [markdown]
# # The memory tools
#
# The tools the model calls to save and look up what it knows about the traveler. The model decides when.
#
# - **Exercise 3B:** the `save_memory` tool. Step A is `create_long_term_memory` in `agent_memory/long_term_memory.py`.
# - **Exercise 4B:** the `search_memories` tool. Step A is `search_long_term_memory` in the same file.


# %%
from typing import Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from backend.lib.log import log
from backend.modules.ai.agent_memory.long_term_memory import create_long_term_memory, search_long_term_memory


# %% [markdown]
# ## Exercise 3B: the `save_memory` tool
#
# **What to do:** make `save_memory_tool` a tool the model can call, and give it to the agent.
#
# The description is what tells the model when to use it. Try it: say "I'm vegetarian", then open the **Memory** tab.


# %%
class SaveMemoryInput(BaseModel):
    fact: str = Field(description="What to remember, written so it makes sense on its own")
    memory_type: Literal["semantic", "episodic"] = Field(
        description="'semantic' for a lasting preference, 'episodic' for something that happened on a past trip"
    )
    topics: list[str] | None = Field(default=None, description="Short labels, for example ['food', 'budget']")


# TODO start (Exercise 3B): turn this function into a tool.
#   1. Add the `@tool(...)` decorator above it, with the name "save_memory", `args_schema=SaveMemoryInput` and a `description`.
#      The description tells the model when to save: a lasting preference, or something that happened on a past trip.
#   2. Save with `create_long_term_memory(user_id=..., text=..., memory_type=..., topics=...)` and return what it answers.
#   3. Add the tool to the `memory_tools` list at the bottom of this file.
# TODO end (Exercise 3B)

async def save_memory_tool(fact: str, memory_type: str, topics: list[str] | None = None, *, config: RunnableConfig):
    """Save a lasting fact about the traveler as a long-term memory, so the agent knows it in later conversations."""

    user_id = config["configurable"]["user_id"]
    log(f'save_memory: "{fact}" ({memory_type})')

    # TODO: save here, and return what the service answered.
    return {}


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# class SaveMemoryInput(BaseModel):
#     fact: str = Field(description="What to remember, written so it makes sense on its own")
#     memory_type: Literal["semantic", "episodic"] = Field(
#         description="'semantic' for a lasting preference, 'episodic' for something that happened on a past trip"
#     )
#     topics: list[str] | None = Field(default=None, description="Short labels, for example ['food', 'budget']")
#
#
# @tool(
#     "save_memory",
#     args_schema=SaveMemoryInput,
#     description=(
#         "Save something about the traveler for future conversations. Use memory_type 'semantic' for a lasting preference, "
#         "such as a diet, a budget or who they travel with. Use 'episodic' for something that happened on a past trip, such "
#         "as where they went and where they stayed. Do not save one-off requests such as this trip's dates."
#     ),
# )
# async def save_memory_tool(fact: str, memory_type: str, topics: list[str] | None = None, *, config: RunnableConfig):
#     """Save a lasting fact about the traveler as a long-term memory, so the agent knows it in later conversations."""
#
#     user_id = config["configurable"]["user_id"]
#     log(f'save_memory: "{fact}" ({memory_type})')
#     response = await create_long_term_memory(user_id=user_id, text=fact, memory_type=memory_type, topics=topics)
#     return response.model_dump()
# ```
#
# </details>


# %% [markdown]
# ## Exercise 4B: the `search_memories` tool
#
# **What to do:** make `search_memories_tool` a tool the model can call, and give it to the agent.
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


# TODO start (Exercise 4B): turn this function into a tool.
#   1. Add the `@tool(...)` decorator above it, with the name "search_memories", `args_schema=SearchMemoriesInput` and a `description`.
#      The description tells the model when to look: when a recommendation depends on what the traveler said before.
#   2. Search with `search_long_term_memory(user_id=..., query=..., memory_type=...)` and return what it finds.
#   3. Add the tool to the `memory_tools` list at the bottom of this file.
# TODO end (Exercise 4B)

async def search_memories_tool(query: str, memory_type: str | None = None, *, config: RunnableConfig):
    """Look up what the traveler told us before, by meaning, in their long-term memories."""

    user_id = config["configurable"]["user_id"]
    log(f'search_memories: "{query}"{f" ({memory_type})" if memory_type else ""}')

    # TODO: search here, and return the entries.
    return []


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# class SearchMemoriesInput(BaseModel):
#     query: str = Field(description="What to look for, for example 'dietary requirements' or 'trips to London'")
#     memory_type: Literal["semantic", "episodic"] | None = Field(
#         default=None,
#         description="Only look at preferences (semantic) or only at past trips (episodic). Leave out to look at both.",
#     )
#
#
# @tool(
#     "search_memories",
#     args_schema=SearchMemoriesInput,
#     description=(
#         "Search what the traveler has told you before, across earlier conversations: diet, budget, who they travel with, "
#         "what they enjoy, and trips they have taken. Use it when a recommendation depends on their preferences or history."
#     ),
# )
# async def search_memories_tool(query: str, memory_type: str | None = None, *, config: RunnableConfig):
#     """Look up what the traveler told us before, by meaning, in their long-term memories."""
#
#     user_id = config["configurable"]["user_id"]
#     log(f'search_memories: "{query}"{f" ({memory_type})" if memory_type else ""}')
#     return await search_long_term_memory(user_id=user_id, query=query, memory_type=memory_type)
# ```
#
# </details>


# %% [markdown]
# ## The tools the agent gets
#
# The agent uses the tools in this list, and the Google Maps tools that are added when the app starts. The list starts
# empty, so the model cannot save or search memories until you add a tool here.


# %%
memory_tools = []

# TODO (Exercise 3B): add `save_memory_tool` here when it is a tool.
# TODO (Exercise 4B): add `search_memories_tool` here when it is a tool.
