from app.scaling.cache.query_cache import QueryCache
from app.scaling.rate_limit.limiter import RateLimiter
from app.rag.service.rag_service import RAGService
from app.rag.generation.full_pipeline import AdvancedRAGPipeline


class ScaledRAGPipeline:

    def __init__(self):

        self.rag = AdvancedRAGPipeline()

        self.limiter = RateLimiter()


    def query(self, user_id: str, question: str):

        # Rate limit
        if not self.limiter.allow(user_id):

            return {
                "error": "rate_limit_exceeded"
            }

        # Cache check
        cached = QueryCache.get(question)

        if cached:

            return cached

        # Run RAG
        result = self.rag.query(question)

        # Cache store
        QueryCache.set(question, result)

        return result