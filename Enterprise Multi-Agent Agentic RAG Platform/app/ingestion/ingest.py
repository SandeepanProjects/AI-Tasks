import uuid

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import split_documents
from app.ingestion.embedder import create_embeddings

from app.rag.vector_store import (
    client,
    COLLECTION_NAME,
    create_collection
)


def ingest_pdf(path: str):

    create_collection()

    docs = load_pdf(path)

    chunks = split_documents(docs)

    texts, vectors = create_embeddings(chunks)

    points = []

    for text, vector in zip(texts, vectors):

        points.append(
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "text": text
                }
            }
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("Documents ingested")