# from app.rag.service.rag_service import RAGService


# class ResearchAgent:

#     def __init__(self):

#         self.rag = RAGService()

#     def run(self, state: dict):

#         result = self.rag.query(
#             state["query"]
#         )

#         state["research"] = result["context"]

#         return state

from app.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):

    def __init__(self, llm):

        self.llm = llm

    async def run(
        self,
        state: dict
    ):

        prompt = f"""
        Research market information.

        Query:
        {state['query']}
        """

        return await self.llm.generate(
            prompt
        )