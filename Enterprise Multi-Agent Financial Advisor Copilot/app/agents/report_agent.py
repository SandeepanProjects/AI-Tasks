# class ReportAgent:

#     def run(self, state: dict):

#         report = f"""
# FINANCIAL ADVISORY REPORT

# Query: {state['query']}

# --- PORTFOLIO ANALYSIS ---
# {state.get('portfolio_analysis', {})}

# --- MARKET RESEARCH ---
# {state.get('research', '')}

# --- RISK ANALYSIS ---
# {state.get('risk_analysis', '')}

# --- COMPLIANCE NOTES ---
# {state.get('compliance_notes', [])}

# DISCLAIMER:
# This is not financial advice.
# """

#         state["final_report"] = report

#         return state


from app.agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):

    def __init__(self, llm):

        self.llm = llm

    async def run(
        self,
        state: dict
    ):

        prompt = f"""
        Create final advisory report.

        Risk Analysis:
        {state['risk_analysis']}

        Market Research:
        {state['market_research']}

        Compliance Review:
        {state['compliance_review']}
        """

        return await self.llm.generate(
            prompt
        )