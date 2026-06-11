from pathlib import Path

from app.rag.loaders.pdf_loader import (
    PDFLoader
)

from app.rag.loaders.docx_loader import (
    DOCXLoader
)

from app.rag.loaders.text_loader import (
    TextLoader
)

from app.rag.chunking.chunker import (
    RecursiveChunker
)

from app.rag.embeddings.embedder import (
    OpenAIEmbedder
)

from app.rag.vectorstore.qdrant_manager import (
    QdrantManager
)


class IngestionService:

    def __init__(self):

        self.chunker = (
            RecursiveChunker()
        )

        self.embedder = (
            OpenAIEmbedder()
        )

        self.qdrant = (
            QdrantManager()
        )

    def ingest(
        self,
        file_path: str
    ):

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        if extension == ".pdf":
            text = PDFLoader.load(
                file_path
            )

        elif extension == ".docx":
            text = DOCXLoader.load(
                file_path
            )

        else:
            text = TextLoader.load(
                file_path
            )

        metadata = {
            "source": file_path
        }

        chunks = self.chunker.chunk(
            text,
            metadata
        )

        for chunk in chunks:

            vector = (
                self.embedder.embed(
                    chunk.text
                )
            )

            self.qdrant.upsert(
                chunk.chunk_id,
                vector,
                {
                    "text": chunk.text,
                    **chunk.metadata
                }
            )

        return {
            "chunks_ingested":
            len(chunks)
        }