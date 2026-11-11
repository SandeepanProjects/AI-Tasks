"""Evidence provenance records independent of free-form LLM output."""
from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Iterable

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    tenant_id: str
    document_id: str
    document_version: str
    chunk_id: str
    page: int | None
    section: str | None
    start_char: int
    end_char: int
    quote: str
    quote_sha256: str
    retrieval_method: str
    retrieval_score: float

    @classmethod
    def create(cls, *, evidence_id: str, tenant_id: str, document_id: str, document_version: str,
               chunk_id: str, quote: str, start_char: int, end_char: int,
               retrieval_method: str, retrieval_score: float, page: int | None = None,
               section: str | None = None):
        if not quote.strip() or start_char < 0 or end_char < start_char:
            raise ValueError("invalid evidence span")
        if not 0 <= retrieval_score <= 1:
            raise ValueError("retrieval_score must be in [0,1]")
        return cls(evidence_id, tenant_id, document_id, document_version, chunk_id, page, section,
                   start_char, end_char, quote, sha256(quote.encode()).hexdigest(), retrieval_method, retrieval_score)

class EvidenceLedger:
    """In-memory append-only reference ledger; production adapter persists to PostgreSQL."""
    def __init__(self): self._records: dict[str, EvidenceRecord] = {}
    def append(self, record: EvidenceRecord) -> None:
        if record.evidence_id in self._records:
            if self._records[record.evidence_id] != record:
                raise ValueError("evidence IDs are immutable")
            return
        self._records[record.evidence_id] = record
    def get(self, evidence_id: str, *, tenant_id: str) -> EvidenceRecord:
        record = self._records[evidence_id]
        if record.tenant_id != tenant_id:
            raise PermissionError("cross-tenant evidence access denied")
        return record
    def export(self, *, tenant_id: str) -> list[dict]:
        return [asdict(r) for r in self._records.values() if r.tenant_id == tenant_id]
