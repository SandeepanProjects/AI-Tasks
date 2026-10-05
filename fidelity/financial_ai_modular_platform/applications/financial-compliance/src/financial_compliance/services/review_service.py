from ai_guardrails.engine import GuardrailEngine
from ai_guardrails.validators import reject_empty, reject_prompt_injection
from ai_llm.ports import LLMRequest
from ai_agents.contracts import AgentContext
from ..domain.models import classify_risk
from ..agents import ComplianceResearchAgent, ComplianceWriterAgent

class ComplianceReviewService:
    def __init__(self, llm):
        self.llm = llm
        self.guardrails = GuardrailEngine([reject_empty, reject_prompt_injection])
        self.researcher = ComplianceResearchAgent()
        self.writer = ComplianceWriterAgent()

    async def review(self, tenant_id: str, material: str, material_type: str) -> dict:
        guard = self.guardrails.check(material)
        if not guard.allowed:
            return {
                "status": "blocked",
                "risk": "unknown",
                "summary": "Request blocked by input guardrails.",
                "citations": [],
                "requires_human_approval": True,
            }

        risk = classify_risk(material)
        context = AgentContext(
            request_id="local-review",
            tenant_id=tenant_id,
            input={"material": material, "material_type": material_type},
            state={"risk": risk},
        )
        research = await self.researcher.run(context)

        llm_response = await self.llm.generate(
            LLMRequest(
                system="You are a financial compliance review assistant.",
                user=material,
                metadata={"tenant_id": tenant_id, "risk": risk},
            )
        )
        context.state["llm"] = llm_response.text
        context.state["research"] = research.output

        written = await self.writer.run(context)
        return {
            "status": "pending_human_approval" if risk == "high" else "completed",
            "risk": risk,
            "summary": written.output["summary"],
            "citations": [x["citation"] for x in research.output["evidence"]],
            "requires_human_approval": risk == "high",
        }
