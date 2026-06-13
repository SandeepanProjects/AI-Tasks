# class ComplianceAgent:

#     def run(self, state: dict):

#         notes = []

#         if "buy" in state["query"].lower():

#             notes.append(
#                 "No guaranteed financial returns should be implied"
#             )

#         notes.append(
#             "All recommendations are informational only"
#         )

#         state["compliance_notes"] = notes

#         return state

from app.agents.base_agent import BaseAgent


class ComplianceAgent(BaseAgent):

    def __init__(self, llm):

        self.llm = llm

    async def run(
        self,
        state: dict
    ):

        prompt = f"""
        Review for compliance concerns.

        Query:
        {state['query']}
        """

        return await self.llm.generate(
            prompt
        )