# db/qdrant_client.py
# Purpose:

# Store vectors.

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from config import QDRANT_URL, COLLECTION_NAME

client = QdrantClient(url=QDRANT_URL) #  Connects to Qdrant.


def upsert_embedding(id, vector, payload):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=id,
                vector=vector,
                payload=payload
            )
        ]
    )


def search_vector(query_vector, top_k=5):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )