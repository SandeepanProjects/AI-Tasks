# class RiskAgent:

#     def run(self, state: dict):

#         portfolio = state.get(
#             "portfolio_analysis",
#             {}
#         )

#         risk = portfolio.get("risk", "UNKNOWN")

#         state["risk_analysis"] = (
#             f"Overall portfolio risk is {risk}"
#         )

#         return state

from app.agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):

    def __init__(self, llm):

        self.llm = llm

    async def run(
        self,
        state: dict
    ):

        prompt = f"""
        Analyze investment risks.

        Query:
        {state['query']}
        """

        result = await self.llm.generate(
            prompt
        )

        return result