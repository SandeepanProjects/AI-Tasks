import hashlib
import math
from typing import Protocol
from app.core.config import settings

class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...

class DeterministicEmbeddingProvider:
    """Local deterministic adapter for development/testing; not a semantic model."""
    async def embed(self, text: str) -> list[float]:
        dim=settings.embedding_dimensions
        raw=hashlib.sha256(text.encode()).digest()
        values=[((raw[i % len(raw)] / 255.0)*2)-1 for i in range(dim)]
        norm=math.sqrt(sum(x*x for x in values)) or 1
        return [x/norm for x in values]
