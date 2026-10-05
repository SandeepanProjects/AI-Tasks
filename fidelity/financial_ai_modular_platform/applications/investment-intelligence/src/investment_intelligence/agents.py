from ai_agents.contracts import AgentContext, AgentResult

class MarketResearchAgent:
    name = "market_research"

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            output={"evidence": [{
                "source": "market-data://demo",
                "text": f"Evidence retrieved for: {context.input['question']}",
            }]},
        )

class InvestmentWriterAgent:
    name = "investment_writer"

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            output={
                "analysis": (
                    f"Research-backed analysis for {context.input['asset']}. "
                    "This is illustrative, not investment advice."
                )
            },
        )
