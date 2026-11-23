from redis_iris.agent_memory import AgentMemory, AgentMemorySettings

from backend.config import config

# The Redis Agent Memory client. It talks to your service over HTTP. The assistant's messages in a session are from "travel-agent".
agent_memory = AgentMemory(
    AgentMemorySettings(
        url=config.agent_memory_url,
        store_id=config.agent_memory_store_id,
        api_key=config.agent_memory_api_key,
    ),
    assistant_id="travel-agent",
)
