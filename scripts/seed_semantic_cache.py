"""
Fills the semantic cache with answers to 15 questions about popular places (Goa, Bali, Paris, New York and more),
so there is something to find. Each answer has the place cards that came with it, from Google Maps.
Safe to run again: it empties the cache first, then adds these answers. That includes any answer the cache kept
by itself (exercise 7).

    uv run python scripts/seed_semantic_cache.py

The answers are in scripts/cache_seed_data.json. They were written by this agent, for a traveler with no memories,
so they are the same for everyone.
"""

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# So that `backend` can be imported when this file is run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv()

from backend.modules.ai.semantic_cache.public_cache import CACHE_NAME, cache  # noqa: E402


async def main() -> int:
    entries = json.loads((Path(__file__).parent / "cache_seed_data.json").read_text())

    await cache.aclear()
    for entry in entries:
        await cache.astore(prompt=entry["question"], response=entry["answer"], metadata={"attachments": entry["attachments"]})
        print(f"✓ {entry['question']} ({len(entry['attachments'])} cards)")

    print(f"Added {len(entries)} answers to {CACHE_NAME}.")
    return 0


sys.exit(asyncio.run(main()))
