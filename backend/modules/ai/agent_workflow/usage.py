from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult


class UsageCallbackHandler(AsyncCallbackHandler):
    """
    Adds up the token usage of every model call in a run, including the ones made inside tools and other nodes.
    Create one for each turn and pass it in the run's config: `{"callbacks": [usage_handler]}`. Then read the
    totals from `usage_handler.usage`.
    """

    def __init__(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.input_token_details: dict[str, int] = {}
        self.output_token_details: dict[str, int] = {}

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        for batch in response.generations:
            for generation in batch:
                usage_metadata = getattr(getattr(generation, "message", None), "usage_metadata", None)
                if not usage_metadata:
                    continue
                self.input_tokens += usage_metadata.get("input_tokens", 0)
                self.output_tokens += usage_metadata.get("output_tokens", 0)
                self.total_tokens += usage_metadata.get("total_tokens", 0)
                add_counts(self.input_token_details, usage_metadata.get("input_token_details"))
                add_counts(self.output_token_details, usage_metadata.get("output_token_details"))

    @property
    def usage(self) -> dict:
        """The totals, in the names the page reads."""

        return {
            "inputTokens": self.input_tokens,
            "outputTokens": self.output_tokens,
            "totalTokens": self.total_tokens,
            "inputTokenDetails": self.input_token_details,
            "outputTokenDetails": self.output_token_details,
        }


def add_counts(totals: dict[str, int], counts: dict[str, int] | None) -> None:
    """Add each count in `counts`, such as cache_read or reasoning tokens, onto `totals`."""

    for name, value in (counts or {}).items():
        totals[name] = totals.get(name, 0) + value
