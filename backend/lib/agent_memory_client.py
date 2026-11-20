from redis_agent_memory import AgentMemory

from backend.config import config

_client: AgentMemory | None = None


def get_agent_memory() -> AgentMemory:
    """The Redis Agent Memory client. One per process. It talks to your service over HTTP."""
    global _client
    if _client is None:
        _client = AgentMemory(
            server_url=config.agent_memory_url,
            store_id=config.agent_memory_store_id,
            api_key=config.agent_memory_api_key,
        )
    return _client
