import structlog
from typing import Protocol
from sqlalchemy import select, or_
from app.db.models import Policy

log = structlog.get_logger(__name__)

class Embedder(Protocol):
    async def embed_query(self, text: str) -> list[float]: ...
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
class RetrievalStrategy(Protocol):
    async def retrieve(self, db, tenant_id: str, query: str, limit: int) -> list[Policy]: ...

class KeywordStrategy:
    async def retrieve(self, db, tenant_id, query, limit):
        terms = [term for term in query.lower().split() if len(term) > 2][:10]
        stmt = select(Policy).where(Policy.tenant_id == tenant_id, Policy.active.is_(True))
        if terms:
            stmt = stmt.where(or_(*[Policy.text.ilike(f"%{term}%") | Policy.title.ilike(f"%{term}%") for term in terms]))
        return list((await db.scalars(stmt.limit(limit))).all())

class VectorStrategy:
    def __init__(self, embedder): self.embedder = embedder
    async def retrieve(self, db, tenant_id, query, limit):
        vector = await self.embedder.embed_query(query)
        stmt = select(Policy).where(Policy.tenant_id == tenant_id, Policy.active.is_(True), Policy.embedding.is_not(None)).order_by(Policy.embedding.cosine_distance(vector)).limit(limit)
        return list((await db.scalars(stmt)).all())

class HybridStrategy:
    """Reciprocal-rank fusion of vector and lexical retrieval."""
    def __init__(self, vector, keyword, rrf_k=60): self.vector, self.keyword, self.rrf_k = vector, keyword, rrf_k
    async def retrieve(self, db, tenant_id, query, limit):
        try:
            vector_rows = await self.vector.retrieve(db, tenant_id, query, limit * 2)
        except Exception as exc:
            log.warning("vector_retrieval_failed_using_keyword", error_type=type(exc).__name__)
            return await self.keyword.retrieve(db, tenant_id, query, limit)
        lexical_rows = await self.keyword.retrieve(db, tenant_id, query, limit * 2)
        scores = {}
        rows = {}
        for ranked in (vector_rows, lexical_rows):
            for rank, row in enumerate(ranked, start=1):
                rows[row.id] = row
                scores[row.id] = scores.get(row.id, 0.0) + 1.0 / (self.rrf_k + rank)
        return [rows[key] for key in sorted(scores, key=scores.get, reverse=True)[:limit]]

class FallbackStrategy:
    def __init__(self, primary, fallback): self.primary, self.fallback = primary, fallback
    async def retrieve(self, db, tenant_id, query, limit):
        try:
            rows = await self.primary.retrieve(db, tenant_id, query, limit)
            return rows if rows else await self.fallback.retrieve(db, tenant_id, query, limit)
        except Exception as exc:
            log.warning("primary_retrieval_failed", error_type=type(exc).__name__)
            return await self.fallback.retrieve(db, tenant_id, query, limit)
