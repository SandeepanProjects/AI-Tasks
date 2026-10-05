import os
from .mock import MockLLM

def create_llm():
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return MockLLM()
    raise RuntimeError(
        f"Provider {provider!r} is not included in this reference implementation. "
        "Add an OpenAI/Bedrock/Anthropic adapter behind LLMProvider."
    )
