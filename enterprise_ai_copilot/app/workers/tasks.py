import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.services.embeddings import EmbeddingService
from app.workers.celery_app import celery_app

def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks

async def _process(document_id: str):
    async with SessionLocal() as db:
        document = await db.get(Document, document_id)
        if not document:
            raise ValueError("Document not found")

        document.status = "processing"
        await db.commit()

        chunks = chunk_text(document.content)
        vectors = await EmbeddingService().embed_many(chunks)

        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            result = await db.execute(
                select(DocumentChunk).where(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.chunk_index == index,
                )
            )
            row = result.scalar_one_or_none()

            if row:
                row.content = content
                row.embedding = vector
            else:
                db.add(DocumentChunk(
                    document_id=document_id,
                    tenant_id=document.tenant_id,
                    chunk_index=index,
                    content=content,
                    embedding=vector,
                ))

        document.status = "ready"
        await db.commit()

@celery_app.task(
    bind=True,
    autoretry_for=(TimeoutError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_document(self, document_id: str):
    asyncio.run(_process(document_id))
    return {"document_id": document_id, "status": "ready"}
