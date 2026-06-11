from app.rag.vectorstore.qdrant_manager import QdrantManager
from app.core.config import settings


class Retriever:

    def __init__(self):

        self.qdrant = QdrantManager()

    def retrieve(
        self,
        query_vector,
        top_k: int = 5,
        filters: dict = None
    ):

        search_result = self.qdrant.client.search(
            collection_name=settings.QDRANT_COLLECTION,

            query_vector=query_vector,

            limit=top_k,

            query_filter=filters
        )

        results = []

        for hit in search_result:

            results.append(
                {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text"),
                    "metadata": hit.payload
                }
            )

        return results