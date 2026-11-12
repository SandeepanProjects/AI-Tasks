"""PostgreSQL persistence adapter for evidence provenance records."""
from sqlalchemy import select
from app.db.models import EvidenceLedgerEntry
from app.enterprise.evidence import EvidenceRecord

class SqlEvidenceLedger:
    def __init__(self, session): self.session = session
    async def append(self, record: EvidenceRecord, *, review_id: str) -> None:
        existing = await self.session.scalar(select(EvidenceLedgerEntry).where(
            EvidenceLedgerEntry.tenant_id == record.tenant_id,
            EvidenceLedgerEntry.evidence_id == record.evidence_id))
        if existing:
            if existing.quote_sha256 != record.quote_sha256 or existing.document_version != record.document_version:
                raise ValueError("evidence IDs are immutable")
            return
        self.session.add(EvidenceLedgerEntry(
            evidence_id=record.evidence_id, tenant_id=record.tenant_id, review_id=review_id,
            document_id=record.document_id, document_version=record.document_version,
            chunk_id=record.chunk_id, page=record.page, section=record.section,
            start_char=record.start_char, end_char=record.end_char, quote=record.quote,
            quote_sha256=record.quote_sha256, retrieval_method=record.retrieval_method,
            retrieval_score=record.retrieval_score))
        await self.session.flush()
    async def get(self, evidence_id: str, *, tenant_id: str):
        return await self.session.scalar(select(EvidenceLedgerEntry).where(
            EvidenceLedgerEntry.evidence_id == evidence_id,
            EvidenceLedgerEntry.tenant_id == tenant_id))
