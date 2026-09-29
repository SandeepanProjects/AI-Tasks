from typing import Protocol
from sqlalchemy import select, or_
from app.db.models import Policy


class Embedder(Protocol):
    async def embed_query(self, text: str) -> list[float]: ...
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
class RetrievalStrategy(Protocol):
    async def retrieve(
        self, db, tenant_id: str, query: str, limit: int
    ) -> list[Policy]: ...
class KeywordStrategy:
    async def retrieve(self, db, tenant_id, query, limit):
        terms = [x for x in query.lower().split() if len(x) > 2][:10]
        stmt = select(Policy).where(
            Policy.tenant_id == tenant_id, Policy.active.is_(True)
        )
        if terms:
            stmt = stmt.where(
                or_(
                    *[
                        Policy.text.ilike(f"%{t}%") | Policy.title.ilike(f"%{t}%")
                        for t in terms
                    ]
                )
            )
        return list((await db.scalars(stmt.limit(limit))).all())


class VectorStrategy:
    def __init__(self, embedder):
        self.embedder = embedder

    async def retrieve(self, db, tenant_id, query, limit):
        vector = await self.embedder.embed_query(query)
        stmt = (
            select(Policy)
            .where(
                Policy.tenant_id == tenant_id,
                Policy.active.is_(True),
                Policy.embedding.is_not(None),
            )
            .order_by(Policy.embedding.cosine_distance(vector))
            .limit(limit)
        )
        return list((await db.scalars(stmt)).all())


class FallbackStrategy:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback

    async def retrieve(self, db, tenant_id, query, limit):
        try:
            rows = await self.primary.retrieve(db, tenant_id, query, limit)
            return (
                rows
                if rows
                else await self.fallback.retrieve(db, tenant_id, query, limit)
            )
        except Exception:
            return await self.fallback.retrieve(db, tenant_id, query, limit)
