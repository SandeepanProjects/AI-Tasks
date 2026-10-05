from typing import Protocol, Sequence
from .models import Evidence

class Embedder(Protocol):
    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        ...

class Retriever(Protocol):
    async def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        ...

class Reranker(Protocol):
    async def rerank(self, query: str, evidence: list[Evidence]) -> list[Evidence]:
        ...
