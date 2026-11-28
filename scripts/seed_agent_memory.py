"""
Gives the three travelers (ashwin, bhavana, kyle) some long-term memories, so there is something to find.
Each name is the name to log in with: the traveler's ID is the name typed on the login screen.
Safe to run again: each memory has a fixed id, and the service skips ids that already exist, so a second run
does not add copies. It never changes a memory that is already there.

    uv run python scripts/seed_agent_memory.py           # add what is missing
    uv run python scripts/seed_agent_memory.py --reset   # delete ALL of these travelers' memories first, then add them again

`--reset` deletes every long-term memory of ashwin, bhavana and kyle, including the ones the service made from their
conversations and the ones the agent saved. It does not touch anyone else's memories.
"""

import asyncio
import sys

from dotenv import load_dotenv
from redis_iris.agent_memory import AgentMemory

load_dotenv()

travelers = {
    "ashwin": [
        {"text": "The traveler's name is Ashwin.", "topics": ["profile"], "memory_type": "semantic"},
        {"text": "Enjoys visiting places of interest: landmarks, museums and historic sites.", "topics": ["landmarks", "culture"], "memory_type": "semantic"},
        {"text": "Prefers cold weather and cooler destinations.", "topics": ["weather"], "memory_type": "semantic"},
        {"text": "Enjoys cycling and likes destinations where it is easy to ride.", "topics": ["cycling", "outdoors"], "memory_type": "semantic"},
        {"text": "Visited Manali, Himachal Pradesh in December 2020.", "topics": ["trip"], "memory_type": "episodic"},
        {"text": "Visited Madrid and Barcelona in February 2026.", "topics": ["trip"], "memory_type": "episodic"},
        {"text": "Visited Kochi in April 2026.", "topics": ["trip"], "memory_type": "episodic"},
        {"text": "Visited New York City in September 2026.", "topics": ["trip"], "memory_type": "episodic"},
    ],
    "bhavana": [
        {"text": "The traveler's name is Bhavana.", "topics": ["profile"], "memory_type": "semantic"},
        {"text": "Travels with family: partner and two young kids (ages 6 and 9). Prefers famous landmarks, outdoor parks, and family-friendly restaurants everyone can enjoy.", "topics": ["family", "outdoors"], "memory_type": "semantic"},
        {"text": "Comfortable with mid-range family budgets: hotels with pools, sit-down restaurants, taxis over public transit when there are kids in tow.", "topics": ["budget"], "memory_type": "semantic"},
        {"text": "Visited Delhi in December 2025.", "topics": ["trip"], "memory_type": "episodic"},
        {"text": "Visited Singapore in August 2026.", "topics": ["trip"], "memory_type": "episodic"},
        {"text": "Visited Mumbai in October 2026.", "topics": ["trip"], "memory_type": "episodic"},
    ],
    "kyle": [
        {"text": "The traveler's name is Kyle.", "topics": ["profile"], "memory_type": "semantic"},
        {"text": "Travels as a couple. Loves rooftop bars, live jazz, contemporary art, and upscale food. Prefers urban destinations.", "topics": ["nightlife", "culture"], "memory_type": "semantic"},
        {"text": "Comfortable spending high on luxury experiences: fine dining, premium cocktails, boutique hotels.", "topics": ["budget"], "memory_type": "semantic"},
        {"text": "Spent a long weekend in New York as a couple: rooftop bars, a late jazz set in Greenwich Village and a tasting menu in Midtown.", "topics": ["trip", "nightlife"], "memory_type": "episodic"},
    ],
}

# The longest to wait for the service when writing the memories
TIMEOUT_MS = 60_000

agent_memory = AgentMemory.from_env()

memories = [
    {"memory_id": f"{user_id}-seed-{index}", "text": fact["text"], "owner_id": user_id, "memory_type": fact["memory_type"], "topics": fact["topics"]}
    for user_id, facts in travelers.items()
    for index, fact in enumerate(facts)
]


async def delete_all_memories(user_id: str) -> int:
    """Delete every long-term memory this traveler owns. Returns how many were deleted."""
    total = 0
    while True:
        # No query: this lists the traveler's memories instead of searching for the closest ones. Ten at a time:
        # the service refuses to delete many in one request, and the loop asks again until none are left.
        found = await agent_memory.client.search_long_term_memory_async(
            request={"limit": 10, "sort_by": "createdAt", "filter_": {"owner_id": {"eq": user_id}, "op": "ALL"}},
            timeout_ms=TIMEOUT_MS,
        )
        if not found.items:
            return total
        removed = await agent_memory.client.bulk_delete_long_term_memories_async(
            memory_ids=[record.memory_id for record in found.items], timeout_ms=TIMEOUT_MS
        )
        for error in removed.errors or []:
            print(f"✗ {error.memory_id}: {error.detail or error.title}")
        if not removed.deleted:
            print(f"✗ Found {len(found.items)} memories of {user_id} but none could be deleted.")
            return total  # stop instead of asking again
        total += len(removed.deleted)


async def main() -> int:
    if "--reset" in sys.argv:
        for user_id in travelers:
            print(f"Deleted {await delete_all_memories(user_id)} memories of {user_id}.")

    result = await agent_memory.client.bulk_create_long_term_memories_async(memories=memories, timeout_ms=TIMEOUT_MS)
    errors = result.errors or []
    already_there = [error for error in errors if error.status == 409]
    failed = [error for error in errors if error.status != 409]

    print(f"Created {len(result.created)} memories for {', '.join(travelers)}. {len(already_there)} were already there.")
    print(f"Log in with one of these names to use them: {', '.join(travelers)}.")
    for error in failed:
        print(f"✗ {error.memory_id}: {error.detail or error.title}")
    return 1 if failed else 0


sys.exit(asyncio.run(main()))
