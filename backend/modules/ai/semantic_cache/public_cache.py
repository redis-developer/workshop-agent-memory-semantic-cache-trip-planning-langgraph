# %% [markdown]
# # Where answers are kept for reuse
#
# The semantic cache in Redis. It keeps a question with the answer it got, and finds that answer again when a
# question with a similar meaning comes in, even if the words are different.
#
# - **Exercise 6A:** look a question up in the cache.
# - **Exercise 7A:** store a question with its answer.
#
# Steps B are in `ai/agent_workflow/nodes.py` and `graph.py`.


# %%
from typing import TypedDict

from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize import OpenAITextVectorizer

from backend.config import config
from backend.lib.log import log
from backend.modules.ai.types import Attachment

# The name of the cache. It is also the name of its index in Redis.
CACHE_NAME = "public_cache"

# How close two questions must be to count as the same. It is a distance: the lower it is, the stricter the match.
DISTANCE_THRESHOLD = 0.3

# The semantic cache, shared by all travelers. Creating it connects to Redis and creates its index if it is not there
# yet, so the app does not start without Redis. Questions are turned into vectors with OpenAI, the same key the agent uses.
cache = SemanticCache(
    name=CACHE_NAME,
    redis_url=config.redis_url,
    distance_threshold=DISTANCE_THRESHOLD,
    vectorizer=OpenAITextVectorizer(model="text-embedding-3-small", api_config={"api_key": config.openai_api_key}),
)


class CachedAnswer(TypedDict):
    text: str  # the reply
    attachments: list[Attachment]  # the place and weather cards that came with it


# %% [markdown]
# ## Exercise 6A: find an answer for a question
#
# **What to do:** find the answer of a question with the same meaning, with `cache.acheck`.
#
# - Ask for the fields `prompt`, `response`, `metadata` and `vector_distance`. The closest entry comes first.
#
# The cache compares the meaning of the question with the questions it holds. If one is close enough
# (`DISTANCE_THRESHOLD`, above), its answer comes back. The cards of the answer were stored in
# `metadata`.


# %%
async def find_cached_answer(question: str) -> CachedAnswer | None:
    """The answer to a question with the same meaning as this one, or None if the cache holds no such question."""

    # TODO start (Exercise 6A): look the question up with `cache.acheck(prompt=question, return_fields=[...])`.
    # If nothing is close enough, return None. Otherwise return the closest answer: its text and its cards (stored in `metadata`).
    # Until you write this, nothing is ever found.

    return None

    # TODO end (Exercise 6A)


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# async def find_cached_answer(question: str) -> CachedAnswer | None:
#     """The answer to a question with the same meaning as this one, or None if the cache holds no such question."""
#
#     hits = await cache.acheck(prompt=question, return_fields=["prompt", "response", "metadata", "vector_distance"])
#     if not hits:
#         log(f'💾 Cache: no similar question for "{question[:50]}"')
#         return None
#     hit = hits[0]
#     log(f'💾 Cache: "{hit["prompt"][:50]}" is close to "{question[:50]}" (distance {float(hit["vector_distance"]):.3f})')
#     return {"text": hit["response"], "attachments": (hit.get("metadata") or {}).get("attachments", [])}
# ```
#
# </details>


# %% [markdown]
# ## Exercise 7A: store an answer
#
# **What to do:** store a question with its answer, and the cards that came with it, with `cache.astore`.
#
# - Put the cards in the entry's `metadata`, as `{"attachments": [...]}`.


# %%
async def save_answer(question: str, answer: CachedAnswer) -> str:
    """Keep this question with its answer, and the cards that came with it. Returns the key the cache gave the entry."""

    # TODO start (Exercise 7A): store the question with its answer using `cache.astore(prompt=..., response=..., metadata={...})`.
    # The cards go in `metadata`. Return the key the cache gave the entry.
    # Until you write this, nothing is stored.

    return ""

    # TODO end (Exercise 7A)


# %% [markdown]
# <details>
# <summary>Show solution</summary>
#
# ```python
# async def save_answer(question: str, answer: CachedAnswer) -> str:
#     """Keep this question with its answer, and the cards that came with it. Returns the key the cache gave the entry."""
#
#     key = await cache.astore(prompt=question, response=answer["text"], metadata={"attachments": answer["attachments"]})
#     log(f'💾 Cache: stored the answer to "{question[:50]}" with {len(answer["attachments"])} cards')
#     return key
# ```
#
# </details>
