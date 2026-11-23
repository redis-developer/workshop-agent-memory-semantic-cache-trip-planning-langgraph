from redis_agent_memory import AgentMemory

from backend.config import config

# The Redis Agent Memory client. It talks to your service over HTTP.
agent_memory = AgentMemory(
    server_url=config.agent_memory_url,
    store_id=config.agent_memory_store_id,
    api_key=config.agent_memory_api_key,
)
