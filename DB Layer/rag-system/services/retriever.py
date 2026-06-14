# services/retriever.py

from db.qdrant_client import search_vector
from services.embedder import embed

def retrieve_context(query: str):
    query_vector = embed(query)

    results = search_vector(query_vector)

    context = []
    for r in results:
        context.append(r.payload["text"])

    return "\n".join(context)