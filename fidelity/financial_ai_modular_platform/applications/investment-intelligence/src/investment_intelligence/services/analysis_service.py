from ai_guardrails.engine import GuardrailEngine
from ai_guardrails.validators import reject_empty, reject_prompt_injection
from ai_llm.ports import LLMRequest
from ai_agents.contracts import AgentContext
from ..domain.models import risk_label
from ..agents import MarketResearchAgent, InvestmentWriterAgent

class InvestmentAnalysisService:
    def __init__(self, llm):
        self.llm = llm
        self.guardrails = GuardrailEngine([reject_empty, reject_prompt_injection])
        self.researcher = MarketResearchAgent()
        self.writer = InvestmentWriterAgent()

    async def analyze(self, tenant_id: str, question: str, asset: str) -> dict:
        guard = self.guardrails.check(question)
        if not guard.allowed:
            return {
                "status": "blocked",
                "analysis": "Request blocked by input guardrails.",
                "evidence_count": 0,
            }

        context = AgentContext(
            request_id="local-analysis",
            tenant_id=tenant_id,
            input={"question": question, "asset": asset},
            state={"risk": risk_label(asset)},
        )
        research = await self.researcher.run(context)
        await self.llm.generate(
            LLMRequest(
                system="You are an investment research assistant.",
                user=question,
                metadata={"asset": asset, "risk": risk_label(asset)},
            )
        )
        written = await self.writer.run(context)

        return {
            "status": "completed",
            "analysis": written.output["analysis"],
            "evidence_count": len(research.output["evidence"]),
        }
