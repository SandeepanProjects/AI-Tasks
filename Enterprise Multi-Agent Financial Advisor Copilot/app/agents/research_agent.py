from app.rag.service.rag_service import RAGService


class ResearchAgent:

    def __init__(self):

        self.rag = RAGService()

    def run(self, state: dict):

        result = self.rag.query(
            state["query"]
        )

        state["research"] = result["context"]

        return state