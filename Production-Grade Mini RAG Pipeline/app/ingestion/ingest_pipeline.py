from app.ingestion.loader import load_documents
from app.ingestion.chunking import TextChunker
from app.embeddings.embedding_service import EmbeddingService
from app.db.vector_store import VectorStore

class IngestionPipeline:
    def __init__(self):
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def ingest(self, folder_path: str):
        documents = load_documents(folder_path)

        for document in documents:
            chunks = self.chunker.chunk_text(document["content"])

            for idx, chunk in enumerate(chunks):
                embedding = self.embedding_service.create_embedding(chunk)

                self.vector_store.insert_chunk(
                    document_name=document["name"],
                    chunk_index=idx,
                    content=chunk,
                    embedding=embedding,
                )
                
                print(f"Inserted chunk {idx}")