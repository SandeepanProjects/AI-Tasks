from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.generation.prompt_builder import PromptBuilder
from app.generation.llm_service import LLMService
from app.retrieval.hybrid_search import RetrievalCache


class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.prompt_builder = PromptBuilder()
        self.llm_service = LLMService()
        self.cache = RetrievalCache()

    def query(self, user_query):
        cached = self.cache.get(user_query)

        if cached:
            return cached

        retrieved_docs = self.retriever.retrieve(user_query)

        reranked = self.reranker.rerank(
            user_query,
            retrieved_docs,
        )

        contexts = [doc[0][0] for doc in reranked[:3]]

        prompt = self.prompt_builder.build_prompt(
            user_query,
            contexts,
        )
        
        answer = self.llm_service.generate(prompt)

        self.cache.set(user_query, answer)

        return answer
