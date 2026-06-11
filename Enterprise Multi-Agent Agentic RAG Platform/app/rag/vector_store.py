from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import VectorParams

from app.config.settings import settings


COLLECTION_NAME = "knowledge_base"


client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT
)


def create_collection():

    existing = [
        c.name
        for c in client.get_collections().collections
    ]

    if COLLECTION_NAME in existing:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE
        )
    )