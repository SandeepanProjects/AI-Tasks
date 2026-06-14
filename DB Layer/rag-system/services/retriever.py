# services/retriever.py

# Purpose:

# Fetch context from Qdrant.

from db.qdrant_client import search_vector
from services.embedder import embed

def retrieve_context(query: str):
    query_vector = embed(query) # Converts query into embedding.

    results = search_vector(query_vector) # Qdrant searches nearest chunks.

    context = []
    for r in results:
        context.append(r.payload["text"])

    return "\n".join(context)