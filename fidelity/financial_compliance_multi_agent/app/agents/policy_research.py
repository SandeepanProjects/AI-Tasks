from app.tools.policy_search import search_policies
from app.tools.policy_lookup import get_policy_by_code
from app.tools.claim_evidence import extract_claim_evidence
class PolicyResearchAgent:
    async def run(self,db,tenant_id,claims):
        all_records={}; per_claim=[]
        for claim in claims:
            records=await search_policies(db,tenant_id,claim["text"],5)
            evidence=extract_claim_evidence(claim["text"],records)
            per_claim.append({"claim":claim["text"],"evidence":evidence})
            for r in records: all_records[r["policy_id"]]=r
        return {"evidence_by_claim":per_claim,"policies":list(all_records.values()),"tools_used":["search_policies","extract_claim_evidence"]}
