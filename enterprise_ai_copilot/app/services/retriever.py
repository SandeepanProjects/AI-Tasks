from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chunk import DocumentChunk
from app.services.embeddings import EmbeddingService

class VectorRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings = EmbeddingService()

    async def search(self, tenant_id: str, query: str, top_k: int = 5):
        vector = await self.embeddings.embed(query)
        distance = DocumentChunk.embedding.cosine_distance(vector)

        stmt = (
            select(DocumentChunk)
            .where(
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(top_k)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
