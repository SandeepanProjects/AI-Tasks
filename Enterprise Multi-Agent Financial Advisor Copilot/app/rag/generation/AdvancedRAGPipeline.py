from app.rag.service.rag_service import RAGService
from app.rag.generation.generator import RAGGenerator


class AdvancedRAGPipeline:

    def __init__(self):

        self.retriever = RAGService()

        self.generator = RAGGenerator()

    def query(self, question: str, metadata_filter=None):

        # Step 1: Retrieve
        retrieval = self.retriever.query(
            question,
            metadata_filter
        )

        context = retrieval["context"]

        sources = retrieval["sources"]

        # Step 2: Generate answer
        response = self.generator.generate(
            question,
            context,
            sources
        )

        return response