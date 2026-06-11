from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

from app.core.config import settings


class QdrantManager:

    def __init__(self):

        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

    def create_collection(self):

        collections = (
            self.client.get_collections()
        )

        names = [
            c.name
            for c in collections.collections
        ]

        if (
            settings.QDRANT_COLLECTION
            not in names
        ):

            self.client.create_collection(
                collection_name=
                settings.QDRANT_COLLECTION,

                vectors_config=
                VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                )
            )

    def upsert(
        self,
        chunk_id,
        vector,
        payload
    ):

        self.client.upsert(
            collection_name=
            settings.QDRANT_COLLECTION,

            points=[
                PointStruct(
                    id=chunk_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )