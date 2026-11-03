from dataclasses import dataclass
from typing import Any
from app.application.ports import EvidenceRepository
from app.core.metrics import RETRIEVAL_CALLS

@dataclass(frozen=True)
class ToolResult:
    name: str
    payload: dict[str, Any]
    evidence_ids: list[str]

class ResearchTools:
    def __init__(self, evidence_repo: EvidenceRepository, max_calls: int=8, max_chunks: int=8):
        self.repo=evidence_repo; self.max_calls=max_calls; self.max_chunks=max_chunks; self.calls=0
    async def search_evidence(self, tenant_id: str, query: str, lookback_days: int, limit: int=8) -> ToolResult:
        self.calls += 1
        if self.calls > self.max_calls: raise RuntimeError("Tool call budget exceeded")
        evidence=await self.repo.search(tenant_id, query, min(limit,self.max_chunks), lookback_days)
        RETRIEVAL_CALLS.labels("hit" if evidence else "miss").inc()
        return ToolResult("search_evidence",
            {"items":[{"id":e.evidence_id,"source":e.source_name,"uri":e.source_uri,
                       "observed_at":e.observed_at.isoformat(),"content":e.content,"hash":e.content_hash}
                      for e in evidence]},[e.evidence_id for e in evidence])
