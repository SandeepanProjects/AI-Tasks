from qdrant_client import AsyncQdrantClient

from app.config.settings import settings
from app.rag.vector_store import VectorStore


class QdrantStore(VectorStore):

    def __init__(self):

        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL
        )


    async def search(
        self,
        query_vector,
        top_k=30
    ):

        results = await self.client.search(
            collection_name=
            settings.QDRANT_COLLECTION,

            query_vector=query_vector,

            limit=top_k
        )

        return results


    async def upsert(
        self,
        ids,
        vectors,
        payloads
    ):

        await self.client.upsert(
            collection_name=
            settings.QDRANT_COLLECTION,

            points=[
                {
                    "id": ids[i],

                    "vector": vectors[i],

                    "payload": payloads[i]
                }
                for i in range(len(ids))
            ]
        )