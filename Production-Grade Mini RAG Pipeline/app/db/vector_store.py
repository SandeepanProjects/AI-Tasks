from sqlalchemy import text
from app.db.postgres import engine


class VectorStore:
    def insert_chunk(
        self,
        document_name,
        chunk_index,
        content,
        embedding,
    ):
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO document_chunks
                    (document_name, chunk_index, content, embedding)
                    VALUES (:document_name, :chunk_index, :content, :embedding)
                    """
                ),
                {
                    "document_name": document_name,
                    "chunk_index": chunk_index,
                    "content": content,
                    "embedding": embedding,
                },
            )