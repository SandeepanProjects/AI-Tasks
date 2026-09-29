import json
from app.agents.base import AgentBase
class ComplianceAnalysisAgent(AgentBase):
    async def run(self,content,claims,research):
        context={"content":content,"claims":claims,"evidence":research.get("evidence_by_claim",[])}
        def fallback():
            findings=[]
            for item in context["evidence"]:
                claim=item["claim"]; ev=item["evidence"]
                risky=any(t in claim.lower() for t in ["guarantee","guaranteed","no risk","risk-free","certain return"])
                findings.append({"claim":claim,"status":"potential_violation" if risky else ("needs_review" if ev else "insufficient_evidence"),"rationale":"Absolute guarantee/zero-risk language needs substantiation and policy review." if risky else "Compare claim with cited policy text; automated result is advisory.","policy_ids":[e["policy_id"] for e in ev],"policy_codes":[e["policy_code"] for e in ev]})
            return {"summary":"Preliminary automated review; human approval required.","findings":findings}
        data=await self.json_completion("Assess each claim against supplied policy evidence. Never invent policy IDs. Return JSON {summary,findings:[{claim,status,rationale,policy_ids,policy_codes}]}. Allowed status: potential_violation, compliant, needs_review, insufficient_evidence.",json.dumps(context),fallback)
        return data if isinstance(data,dict) else fallback()
