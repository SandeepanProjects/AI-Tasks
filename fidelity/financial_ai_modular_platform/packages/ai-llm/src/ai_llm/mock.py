import json
from .ports import LLMRequest, LLMResponse

class MockLLM:
    """Deterministic local/test provider."""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=json.dumps({
                "summary": f"Generated analysis for: {request.user[:120]}",
                "risk": "medium",
            }),
            model="mock",
            input_tokens=20,
            output_tokens=30,
        )
