from app.rag.qdrant_store import (
    QdrantStore
)

from app.rag.reranker import (
    Reranker
)


class Container:

    def __init__(self):

        self.vectorstore = (
            QdrantStore()
        )

        self.reranker = (
            Reranker()
        )


container = Container()