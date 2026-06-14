# services/rag_pipeline.py

from db.redis_client import get_cache, set_cache
from db.postgres import save_chat
from services.retriever import retrieve_context
from services.llm import generate_answer

def rag_pipeline(user_id: str, query: str):

    cache_key = f"cache:{query}"

    # ⚡ 1. Redis Cache Check
    cached = get_cache(cache_key)
    if cached:
        return cached

    # 🔍 2. Retrieve context from Qdrant
    context = retrieve_context(query)

    # 🧠 3. Generate answer using LLM
    answer = generate_answer(context, query)

    # 🐘 4. Store in PostgreSQL
    save_chat(user_id, query, answer)

    # ⚡ 5. Cache response in Redis
    set_cache(cache_key, answer)

    return answer