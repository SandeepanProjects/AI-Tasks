from app.agents.base import AgentBase
class ClaimExtractionAgent(AgentBase):
    async def run(self,content):
        fallback=lambda:{"claims":[{"text":content.strip(),"claim_type":"financial_or_product_claim"}]}
        data=await self.json_completion("Extract material factual, performance, risk, fee, guarantee and suitability claims. Return JSON {claims:[{text,claim_type}]}. Do not invent claims.",content,fallback)
        return [{"text":str(c.get("text",""))[:3000],"claim_type":str(c.get("claim_type","other"))} for c in (data.get("claims") or fallback()["claims"]) if c.get("text")]
