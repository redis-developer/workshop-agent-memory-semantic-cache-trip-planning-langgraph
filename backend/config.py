"""The settings the app reads from the environment (see .env.example)."""

import os

from dotenv import load_dotenv

load_dotenv()


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill it in, or set it as a Codespaces secret.")
    return value


class Config:
    port = int(os.environ.get("PORT", 3000))
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    openai_api_key = required("OPENAI_API_KEY")
    google_maps_api_key = required("GOOGLE_MAPS_API_KEY")
    agent_memory_url = required("IRIS_AGENT_MEMORY_URL")
    agent_memory_store_id = required("IRIS_AGENT_MEMORY_STORE_ID")
    agent_memory_api_key = required("IRIS_AGENT_MEMORY_API_KEY")
    redis_url = required("REDIS_URL")


config = Config()
