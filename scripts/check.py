"""
Checks that everything the workshop needs is reachable, before you start.

    uv run python scripts/check.py
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv
from redis_iris.agent_memory import AgentMemory

load_dotenv()

names = ["IRIS_AGENT_MEMORY_URL", "IRIS_AGENT_MEMORY_STORE_ID", "IRIS_AGENT_MEMORY_API_KEY", "OPENAI_API_KEY", "GOOGLE_MAPS_API_KEY"]
missing = [name for name in names if not os.environ.get(name)]
if missing:
    print(f"✗ Missing settings: {', '.join(missing)}. Copy .env.example to .env and fill it in, or set them as Codespaces secrets.")
    sys.exit(1)


async def check(label: str, run) -> bool:
    try:
        await run()
        print(f"✓ {label}")
        return True
    except Exception as error:
        print(f"✗ {label}: {error}")
        return False


agent_memory = AgentMemory.from_env().client


async def check_openai() -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})
    if not response.is_success:
        raise RuntimeError(f"status {response.status_code}")


async def check_google_maps() -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://mapstools.googleapis.com/mcp",
            headers={"content-type": "application/json", "accept": "application/json", "X-Goog-Api-Key": os.environ["GOOGLE_MAPS_API_KEY"]},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "search_places", "arguments": {"text_query": "Lisbon", "page_size": 1}}},
        )
    body = response.json()
    if body.get("result", {}).get("isError"):
        raise RuntimeError(body["result"].get("content", [{}])[0].get("text", f"status {response.status_code}"))


async def main() -> int:
    results = [
        await check("Redis Agent Memory is reachable", lambda: agent_memory.store_health_async()),
        await check("OpenAI key works", check_openai),
        await check("Google Maps key works", check_google_maps),
    ]
    return 0 if all(results) else 1


sys.exit(asyncio.run(main()))
