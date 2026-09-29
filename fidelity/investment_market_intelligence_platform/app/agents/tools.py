from dataclasses import dataclass
from typing import Callable, Awaitable, Any

@dataclass(frozen=True)
class ToolResult:
    name: str
    payload: dict[str, Any]
    evidence_ids: list[str]

class ResearchTools:
    """Explicit allow-list. Tools accept validated parameters, never arbitrary SQL/URLs."""
    def __init__(self, evidence_repo):
        self._evidence_repo = evidence_repo

    async def search_evidence(self, tenant_id: str, query: str) -> ToolResult:
        evidence = await self._evidence_repo.search(tenant_id, query, limit=8)
        return ToolResult("search_evidence",
                          {"items": [{"id": e.evidence_id, "source": e.source_name,
                                      "uri": e.source_uri, "observed_at": e.observed_at.isoformat(),
                                      "content": e.content, "hash": e.content_hash} for e in evidence]},
                          [e.evidence_id for e in evidence])
