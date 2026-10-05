from .models import Chunk, Evidence

class InMemoryRetriever:
    """Reference adapter. Production can implement pgvector/Qdrant here."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks

    async def retrieve(self, query: str, top_k: int = 5) -> list[Evidence]:
        terms = set(query.lower().split())
        scored = []
        for chunk in self.chunks:
            overlap = len(terms.intersection(set(chunk.text.lower().split())))
            if overlap:
                scored.append(Evidence(
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=float(overlap),
                    metadata=chunk.metadata,
                ))
        return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]
