from uuid import uuid4

from app.rag.schemas.document import (
    DocumentChunk
)


class RecursiveChunker:

    def __init__(
        self,
        chunk_size=1000,
        chunk_overlap=200
    ):

        self.chunk_size = chunk_size

        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        text: str,
        metadata: dict
    ):

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[start:end]

            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid4()),
                    text=chunk_text,
                    metadata=metadata
                )
            )

            start += (
                self.chunk_size
                - self.chunk_overlap
            )

        return chunks