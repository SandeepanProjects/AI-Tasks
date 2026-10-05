from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass(frozen=True)
class LLMRequest:
    system: str
    user: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0

class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        ...
