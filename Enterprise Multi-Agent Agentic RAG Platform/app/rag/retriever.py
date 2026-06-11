from app.rag.embeddings import get_embeddings
from app.rag.vector_store import (
    client,
    COLLECTION_NAME
)


def retrieve_context(
    query: str,
    top_k: int = 5
):

    embeddings = get_embeddings()

    query_vector = embeddings.embed_query(query)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    docs = []

    for result in results:

        docs.append(
            result.payload["text"]
        )

    return docs