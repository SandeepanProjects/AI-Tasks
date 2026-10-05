from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.adapters.models_mapper import review_from_row, review_to_row
from app.db.models import ReviewRow, IdempotencyRow, EvidenceChunkRow, AuditEventRow, WorkflowCheckpointRow
from app.domain.models import Review, Evidence
from app.core.errors import ConflictError

class SqlReviewRepository:
    def __init__(self, session): self.session=session

    async def _set_tenant(self, tenant_id: str):
        await self.session.execute(
            __import__("sqlalchemy").text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id},
        )

    async def add(self, review: Review, idempotency_key: str) -> bool:
        await self._set_tenant(review.tenant_id)
        existing = await self.session.get(IdempotencyRow, idempotency_key)
        if existing: return False
        self.session.add(review_to_row(review))
        self.session.add(IdempotencyRow(key=idempotency_key, tenant_id=review.tenant_id, review_id=review.id))
        try:
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def get(self, tenant_id: str, review_id: UUID):
        await self._set_tenant(tenant_id)
        row = await self.session.scalar(select(ReviewRow).where(
            ReviewRow.id==review_id, ReviewRow.tenant_id==tenant_id))
        return review_from_row(row) if row else None

    async def save(self, review: Review, expected_version: int|None=None):
        await self._set_tenant(review.tenant_id)
        stmt=update(ReviewRow).where(ReviewRow.id==review.id, ReviewRow.tenant_id==review.tenant_id)
        if expected_version is not None: stmt=stmt.where(ReviewRow.version==expected_version)
        # Only update mutable fields; never pass ORM internal state into SQLAlchemy.
        values=dict(status=review.status.value, report=review.report, reviewer_id=review.reviewer_id,
                    reviewer_comment=review.reviewer_comment, version=review.version)
        result=await self.session.execute(stmt.values(**values))
        if result.rowcount != 1:
            await self.session.rollback()
            raise ConflictError("Concurrent review update detected")
        await self.session.commit()

class SqlEvidenceRepository:
    def __init__(self, session): self.session=session

    async def _set_tenant(self, tenant_id: str):
        await self.session.execute(
            __import__("sqlalchemy").text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id},
        )
    async def search(self, tenant_id: str, query: str, limit: int):
        await self._set_tenant(tenant_id)
        rows=(await self.session.scalars(select(EvidenceChunkRow)
               .where(EvidenceChunkRow.tenant_id==tenant_id)
               .order_by(EvidenceChunkRow.observed_at.desc()).limit(limit))).all()
        return [Evidence(str(r.id),r.source_name,r.source_uri,r.observed_at,r.content,r.content_hash,
                         r.tenant_id,r.metadata_json or {}) for r in rows]

    async def search_by_embedding(self, tenant_id: str, embedding: list[float], limit: int):
        await self._set_tenant(tenant_id)
        distance=EvidenceChunkRow.embedding.cosine_distance(embedding)
        rows=(await self.session.scalars(select(EvidenceChunkRow)
               .where(EvidenceChunkRow.tenant_id==tenant_id, EvidenceChunkRow.embedding.is_not(None))
               .order_by(distance).limit(limit))).all()
        return [Evidence(str(r.id),r.source_name,r.source_uri,r.observed_at,r.content,r.content_hash,
                         r.tenant_id,r.metadata_json or {}) for r in rows]

class SqlAuditRepository:
    def __init__(self, session): self.session=session
    async def append(self, tenant_id, actor_id, action, resource_id, details):
        self.session.add(AuditEventRow(tenant_id=tenant_id,actor_id=actor_id,action=action,
                                       resource_id=resource_id,details=details))
        await self.session.commit()

class SqlCheckpointRepository:
    def __init__(self, session): self.session=session
    async def save(self, review_id, node, state):
        self.session.add(WorkflowCheckpointRow(review_id=review_id,node=node,state=state))
        await self.session.commit()
