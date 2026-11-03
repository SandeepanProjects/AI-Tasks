from contextlib import asynccontextmanager
from hashlib import sha256
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db, get_tenant_db, engine
from app.db.models import Review, AuditEvent, OutboxEvent, IdempotencyRecord
from app.domain.schemas import ReviewRequest, DecisionRequest, PolicyIngestRequest, ReviewStatus
from app.auth import Principal
from app.security.rbac import require_permission, Permission
from app.domain.state_machine import assert_transition
from app.retrieval.ingestion import ingest_policy
from app.repositories.sqlalchemy import SqlReviewRepository
from app.observability import log
from app.config import settings

@asynccontextmanager
async def lifespan(app):
    yield
    await engine.dispose()

app = FastAPI(title="Financial Compliance Review Platform", version="3.1.0", lifespan=lifespan)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    request.state.request_id = request_id
    log.info("http_request", request_id=request_id, method=request.method, path=request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health/live")
async def live():
    return {"status": "alive"}

@app.get("/health/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    await db.execute(select(1))
    return {"status": "ready"}

@app.post("/v1/reviews", status_code=202)
async def create_review(
    body: ReviewRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    p: Principal = Depends(require_permission(Permission.REVIEW_CREATE)),
    db: AsyncSession = Depends(get_tenant_db),
):
    if idempotency_key and (len(idempotency_key) > settings.idempotency_key_max_length or not idempotency_key.strip()):
        raise HTTPException(400, "Invalid Idempotency-Key")
    request_hash = sha256(body.model_dump_json().encode()).hexdigest()
    if idempotency_key:
        existing = await db.scalar(select(IdempotencyRecord).where(
            IdempotencyRecord.tenant_id == p.tenant_id,
            IdempotencyRecord.idempotency_key == idempotency_key,
        ))
        if existing:
            if existing.request_hash != request_hash:
                raise HTTPException(409, "Idempotency-Key was already used with a different request")
            review = await SqlReviewRepository(db).get(p.tenant_id, existing.resource_id)
            return {"review_id": existing.resource_id, "status": review.status if review else "queued"}

    rid = uuid4().hex
    obj = Review(id=rid, tenant_id=p.tenant_id, created_by=p.sub,
                 status=ReviewStatus.QUEUED.value, input_text=body.statement,
                 result_json=None, thread_id=f"tenant:{p.tenant_id}:review:{rid}")
    db.add(obj)
    db.add(AuditEvent(id=uuid4().hex, tenant_id=p.tenant_id, review_id=rid,
                      actor_id=p.sub, event_type="review.created", details={}))
    db.add(OutboxEvent(id=uuid4().hex, tenant_id=p.tenant_id, aggregate_id=rid,
                       event_type="reviews.execute", payload={"tenant_id": p.tenant_id, "review_id": rid}))
    if idempotency_key:
        db.add(IdempotencyRecord(id=uuid4().hex, tenant_id=p.tenant_id,
              idempotency_key=idempotency_key, request_hash=request_hash, resource_id=rid))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        if idempotency_key:
            from app.security.tenant_context import set_tenant_context
            await set_tenant_context(db, p.tenant_id)
            existing = await db.scalar(select(IdempotencyRecord).where(
                IdempotencyRecord.tenant_id == p.tenant_id,
                IdempotencyRecord.idempotency_key == idempotency_key))
            if existing and existing.request_hash == request_hash:
                existing_review = await SqlReviewRepository(db).get(p.tenant_id, existing.resource_id)
                return {"review_id": existing.resource_id,
                        "status": existing_review.status if existing_review else ReviewStatus.QUEUED.value}
        raise HTTPException(409, "Concurrent request used this Idempotency-Key")
    return {"review_id": rid, "status": ReviewStatus.QUEUED.value}

@app.get("/v1/reviews/{rid}")
async def get_review(rid: str, p: Principal = Depends(require_permission(Permission.REVIEW_READ)),
                     db: AsyncSession = Depends(get_tenant_db)):
    obj = await SqlReviewRepository(db).get(p.tenant_id, rid)
    if not obj:
        raise HTTPException(404, "Review not found")
    return {"review_id": obj.id, "status": obj.status, "result": obj.result_json}

@app.get("/v1/reviews/{rid}/audit")
async def get_review_audit(rid: str, p: Principal = Depends(require_permission(Permission.AUDIT_READ)),
                           db: AsyncSession = Depends(get_tenant_db)):
    review = await SqlReviewRepository(db).get(p.tenant_id, rid)
    if not review:
        raise HTTPException(404, "Review not found")
    events = list((await db.scalars(select(AuditEvent).where(
        AuditEvent.tenant_id == p.tenant_id, AuditEvent.review_id == rid
    ).order_by(AuditEvent.created_at))).all())
    return [{"event_id": event.id, "actor_id": event.actor_id, "event_type": event.event_type,
             "details": event.details, "created_at": event.created_at} for event in events]

@app.post("/v1/reviews/{rid}/decision", status_code=202)
async def decide(rid: str, body: DecisionRequest,
                 p: Principal = Depends(require_permission(Permission.REVIEW_APPROVE)),
                 db: AsyncSession = Depends(get_tenant_db)):
    obj = await db.scalar(select(Review).where(Review.id == rid, Review.tenant_id == p.tenant_id).with_for_update())
    if not obj:
        raise HTTPException(404, "Review not found")
    if obj.created_by == p.sub:
        raise HTTPException(403, "Review creators cannot approve or reject their own reviews")
    try:
        assert_transition(obj.status, ReviewStatus.DECISION_QUEUED)
    except ValueError:
        raise HTTPException(409, "Review is not awaiting a decision")
    obj.status = ReviewStatus.DECISION_QUEUED.value
    db.add(AuditEvent(id=uuid4().hex, tenant_id=p.tenant_id, review_id=rid,
        actor_id=p.sub, event_type="review.decision_queued", details={"decision": body.decision}))
    db.add(OutboxEvent(id=uuid4().hex, tenant_id=p.tenant_id, aggregate_id=rid,
        event_type="reviews.resume", payload={"tenant_id": p.tenant_id, "review_id": rid,
        "decision": {"decision": body.decision, "comment": body.comment, "actor_id": p.sub}}))
    await db.commit()
    return {"review_id": rid, "status": ReviewStatus.DECISION_QUEUED.value}

@app.post("/v1/policies/ingest", status_code=201)
async def policy_ingest(body: PolicyIngestRequest,
    p: Principal = Depends(require_permission(Permission.POLICY_INGEST)),
    db: AsyncSession = Depends(get_tenant_db)):
    try:
        rows = await ingest_policy(db, p.tenant_id, body.code, body.version, body.title, body.text, body.source_uri)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    db.add(AuditEvent(id=uuid4().hex, tenant_id=p.tenant_id,
        review_id="policy:" + rows[0].id, actor_id=p.sub, event_type="policy.ingested",
        details={"code": body.code, "version": body.version, "chunks": len(rows)}))
    await db.commit()
    return {"policy_code": body.code, "version": body.version, "chunks": len(rows)}

@app.exception_handler(Exception)
async def unhandled(request, exc):
    log.exception("unhandled_api_error", path=request.url.path,
                  request_id=getattr(request.state, "request_id", None))
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
