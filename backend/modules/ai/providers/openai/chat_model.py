from langchain_openai import ChatOpenAI

from backend.config import config

_models: dict[bool, ChatOpenAI] = {}


def get_chat_model(disable_streaming: bool = False) -> ChatOpenAI:
    """
    The chat model. One for the agent, which streams its reply to the page as it is written, and one for
    small background calls whose output the traveler never reads (`disable_streaming`), so their text
    does not mix into the reply.
    """

    if disable_streaming not in _models:
        _models[disable_streaming] = ChatOpenAI(
            api_key=config.openai_api_key,
            model=config.model_name,
            temperature=0.2,
            disable_streaming=disable_streaming,
        )
    return _models[disable_streaming]
