from sqlalchemy import text
from app.db.postgres import engine
from app.embeddings.embedding_service import EmbeddingService

class Retriever:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def retrieve(self, query: str, top_k: int = 5):
        query_embedding = self.embedding_service.create_embedding(query)

        sql = text(
            """
            SELECT content,
                   1 - (embedding <=> :embedding) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> :embedding
            LIMIT :top_k
            """
        )

        with engine.begin() as conn:
            rows = conn.execute(
                sql,
                {
                    "embedding": query_embedding,
                    "top_k": top_k,
                },
            ).fetchall()

        return rows