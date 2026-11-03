from uuid import UUID
from sqlalchemy import select, update, text, func
from sqlalchemy.exc import IntegrityError
from app.adapters.models_mapper import review_from_row, review_to_row
from app.db.models import ReviewRow, IdempotencyRow, EvidenceChunkRow, AuditEventRow, WorkflowCheckpointRow, OutboxEventRow
from app.domain.models import Review, Evidence
from app.core.errors import ConflictError
import hashlib
import json

class SqlReviewRepository:
    def __init__(self, session): self.session=session

    async def _set_tenant(self, tenant_id: str):
        await self.session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id},
        )

    async def add(self, review: Review, idempotency_key: str) -> tuple[bool, Review | None]:
        await self._set_tenant(review.tenant_id)
        canonical = json.dumps({"question": review.question, "assets": review.assets,
                                "lookback_days": review.lookback_days, "purpose": review.purpose},
                               sort_keys=True, separators=(",", ":"))
        request_hash = hashlib.sha256(canonical.encode()).hexdigest()
        existing = await self.session.scalar(select(IdempotencyRow).where(
            IdempotencyRow.tenant_id == review.tenant_id, IdempotencyRow.key == idempotency_key))
        if existing:
            if existing.request_hash != request_hash:
                raise ConflictError("Idempotency key was already used with a different request")
            prior = await self.get(review.tenant_id, existing.review_id)
            return False, prior
        self.session.add(review_to_row(review))
        # Creation audit is committed atomically with the review and outbox event.
        self.session.add(AuditEventRow(tenant_id=review.tenant_id, actor_id=review.created_by,
            action="review.created", resource_id=str(review.id), details={"purpose": review.purpose}))
        self.session.add(IdempotencyRow(key=idempotency_key, tenant_id=review.tenant_id,
                                        request_hash=request_hash, review_id=review.id))
        self.session.add(OutboxEventRow(tenant_id=review.tenant_id, aggregate_id=review.id,
            event_type="review.requested", payload={"review_id": str(review.id),
            "tenant_id": review.tenant_id}))
        try:
            await self.session.commit()
            return True, None
        except IntegrityError:
            await self.session.rollback()
            await self._set_tenant(review.tenant_id)
            existing = await self.session.scalar(select(IdempotencyRow).where(
                IdempotencyRow.tenant_id == review.tenant_id, IdempotencyRow.key == idempotency_key))
            if existing and existing.request_hash == request_hash:
                return False, await self.get(review.tenant_id, existing.review_id)
            raise ConflictError("Idempotency key conflict")

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
                    reviewer_comment=review.reviewer_comment, version=review.version,
                    processing_started_at=None)
        result=await self.session.execute(stmt.values(**values))
        if result.rowcount != 1:
            await self.session.rollback()
            raise ConflictError("Concurrent review update detected")
        await self.session.commit()

    async def save_with_audit(self, review: Review, expected_version: int, actor_id: str,
                              action: str, details: dict) -> None:
        await self._set_tenant(review.tenant_id)
        result = await self.session.execute(update(ReviewRow).where(
            ReviewRow.id == review.id, ReviewRow.tenant_id == review.tenant_id,
            ReviewRow.version == expected_version).values(status=review.status.value,
            report=review.report, reviewer_id=review.reviewer_id,
            reviewer_comment=review.reviewer_comment, version=review.version,
            processing_started_at=None))
        if result.rowcount != 1:
            await self.session.rollback()
            raise ConflictError("Concurrent review update detected")
        self.session.add(AuditEventRow(tenant_id=review.tenant_id, actor_id=actor_id,
            action=action, resource_id=str(review.id), details=details))
        await self.session.commit()

    async def requeue_failed(self, review: Review, expected_version: int, actor_id: str) -> None:
        await self._set_tenant(review.tenant_id)
        result = await self.session.execute(update(ReviewRow).where(
            ReviewRow.id == review.id, ReviewRow.tenant_id == review.tenant_id,
            ReviewRow.status == "failed", ReviewRow.version == expected_version).values(
            status="queued", version=review.version, report=None, reviewer_id=None,
            reviewer_comment=None, processing_started_at=None))
        if result.rowcount != 1:
            await self.session.rollback()
            raise ConflictError("Review could not be requeued; status/version changed")
        self.session.add(OutboxEventRow(tenant_id=review.tenant_id, aggregate_id=review.id,
            event_type="review.requeued", payload={"review_id": str(review.id),
            "tenant_id": review.tenant_id}))
        self.session.add(AuditEventRow(tenant_id=review.tenant_id, actor_id=actor_id,
            action="review.requeued", resource_id=str(review.id), details={}))
        await self.session.commit()

class SqlEvidenceRepository:
    def __init__(self, session): self.session=session

    async def _set_tenant(self, tenant_id: str):
        await self.session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id},
        )
    async def search(self, tenant_id: str, query: str, limit: int, lookback_days: int):
        await self._set_tenant(tenant_id)
        from datetime import datetime, timedelta, timezone
        import re
        from sqlalchemy import func, literal_column
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        stop_words = {"the", "and", "for", "with", "from", "using", "available", "summarize", "analyze", "analysis"}
        terms = [token for token in re.findall(r"[a-z0-9]+", query.lower())
                 if len(token) > 1 and token not in stop_words]
        if not terms:
            return []
        english = literal_column("'english'::regconfig")
        ts_query = func.to_tsquery(english, " | ".join(terms))
        document_vector = func.to_tsvector(english, EvidenceChunkRow.content)
        rank = func.ts_rank(document_vector, ts_query)
        stmt = (select(EvidenceChunkRow).where(EvidenceChunkRow.tenant_id == tenant_id,
                EvidenceChunkRow.observed_at >= cutoff,
                document_vector.op("@@")(ts_query))
                .order_by(rank.desc(), EvidenceChunkRow.observed_at.desc()).limit(limit))
        rows = (await self.session.scalars(stmt)).all()
        return [Evidence(str(r.id), r.source_name, r.source_uri, r.observed_at, r.content,
                         r.content_hash, r.tenant_id, r.metadata_json or {}) for r in rows]

    async def search_by_embedding(self, tenant_id: str, embedding: list[float], limit: int, lookback_days: int):
        await self._set_tenant(tenant_id)
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        distance=EvidenceChunkRow.embedding.cosine_distance(embedding)
        rows=(await self.session.scalars(select(EvidenceChunkRow)
               .where(EvidenceChunkRow.tenant_id==tenant_id, EvidenceChunkRow.embedding.is_not(None),
                      EvidenceChunkRow.observed_at >= cutoff)
               .order_by(distance).limit(limit))).all()
        return [Evidence(str(r.id),r.source_name,r.source_uri,r.observed_at,r.content,r.content_hash,
                         r.tenant_id,r.metadata_json or {}) for r in rows]

class SqlAuditRepository:
    def __init__(self, session): self.session=session
    async def append(self, tenant_id, actor_id, action, resource_id, details):
        await self.session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"), {"tenant_id": tenant_id})
        self.session.add(AuditEventRow(tenant_id=tenant_id,actor_id=actor_id,action=action,
                                       resource_id=resource_id,details=details))
        await self.session.commit()

class SqlCheckpointRepository:
    def __init__(self, session): self.session=session
    async def save(self, tenant_id, review_id, node, state):
        await self.session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"), {"tenant_id": tenant_id})
        self.session.add(WorkflowCheckpointRow(tenant_id=tenant_id, review_id=review_id,node=node,state=state))
        await self.session.commit()


class SqlOutboxRepository:
    def __init__(self, session): self.session = session

    async def pending(self, limit: int = 100):
        from sqlalchemy import or_
        rows = (await self.session.scalars(select(OutboxEventRow).where(
            OutboxEventRow.completed_at.is_(None),
            or_(OutboxEventRow.published_at.is_(None),
                OutboxEventRow.published_at < func.now() - text("INTERVAL '10 minutes'")))
            .order_by(OutboxEventRow.created_at).limit(limit))).all()
        return rows

    async def mark_completed(self, aggregate_id):
        from datetime import datetime, timezone
        await self.session.execute(update(OutboxEventRow).where(
            OutboxEventRow.aggregate_id == aggregate_id, OutboxEventRow.completed_at.is_(None)).values(
            completed_at=datetime.now(timezone.utc)))
        await self.session.commit()

    async def mark_published(self, event_id):
        from datetime import datetime, timezone
        await self.session.execute(update(OutboxEventRow).where(OutboxEventRow.id == event_id).values(
            published_at=datetime.now(timezone.utc), attempts=OutboxEventRow.attempts + 1))
        await self.session.commit()

    async def mark_attempt(self, event_id):
        await self.session.execute(update(OutboxEventRow).where(OutboxEventRow.id == event_id).values(
            attempts=OutboxEventRow.attempts + 1))
        await self.session.commit()

class SqlEvidenceIngestionRepository:
    def __init__(self, session): self.session = session

    async def add_many(self, tenant_id: str, rows: list[dict]) -> int:
        await self.session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                                   {"tenant_id": tenant_id})
        hashes = [row["content_hash"] for row in rows]
        existing = set((await self.session.scalars(select(EvidenceChunkRow.content_hash).where(
            EvidenceChunkRow.tenant_id == tenant_id,
            EvidenceChunkRow.content_hash.in_(hashes)))).all())
        new_rows = []
        seen = set(existing)
        for row in rows:
            if row["content_hash"] in seen:
                continue
            seen.add(row["content_hash"])
            new_rows.append(EvidenceChunkRow(id=__import__("uuid").uuid4(), tenant_id=tenant_id, source_name=row["source_name"],
                source_uri=row["source_uri"], observed_at=row["observed_at"], content=row["content"],
                content_hash=row["content_hash"], embedding=row["embedding"], metadata_json=row["metadata"]))
        if not new_rows:
            return 0
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        values = [{"id": row.id, "tenant_id": row.tenant_id, "source_name": row.source_name,
            "source_uri": row.source_uri, "observed_at": row.observed_at, "content": row.content,
            "content_hash": row.content_hash, "embedding": row.embedding, "metadata": row.metadata_json}
            for row in new_rows]
        statement = pg_insert(EvidenceChunkRow).values(values).on_conflict_do_nothing(
            index_elements=["tenant_id", "content_hash"])
        result = await self.session.execute(statement)
        await self.session.commit()
        return result.rowcount or 0
