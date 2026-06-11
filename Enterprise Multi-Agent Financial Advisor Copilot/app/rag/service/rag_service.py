from app.rag.retrieval.retriever import Retriever
from app.rag.retrieval.reranker import Reranker
from app.rag.retrieval.hybrid import HybridSearch
from app.rag.embeddings.embedder import OpenAIEmbedder


class RAGService:

    def __init__(self):

        self.embedder = OpenAIEmbedder()

        self.retriever = Retriever()

    def query(
        self,
        question: str,
        metadata_filter: dict = None,
        top_k: int = 5
    ):

        # Step 1: Embed query
        query_vector = self.embedder.embed(question)

        # Step 2: Build filters
        q_filter = HybridSearch.build_filter(
            metadata_filter
        )

        # Step 3: Retrieve
        results = self.retriever.retrieve(
            query_vector=query_vector,
            top_k=top_k,
            filters=q_filter
        )

        # Step 4: Re-rank
        ranked = Reranker.rerank(
            results,
            question
        )

        # Step 5: Build context
        context = self.build_context(
            ranked
        )

        return {
            "question": question,
            "context": context,
            "sources": ranked
        }

    def build_context(
        self,
        results: list,
        max_chars: int = 6000
    ):

        context = ""

        for r in results:

            chunk = r["text"]

            if len(context) + len(chunk) > max_chars:
                break

            context += "\n\n" + chunk

        return context