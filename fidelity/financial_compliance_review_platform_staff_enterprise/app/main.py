from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db, engine
from app.db.models import Review, AuditEvent
from app.domain.schemas import ReviewRequest, DecisionRequest, PolicyIngestRequest
from app.auth import current_principal, require_role, Principal
from app.workers.tasks import execute_review, resume_review
from app.retrieval.ingestion import ingest_policy
from app.repositories.sqlalchemy import SqlReviewRepository, SqlAuditRepository
from app.observability import log


@asynccontextmanager
async def lifespan(app):
    yield
    await engine.dispose()


app = FastAPI(
    title="Financial Compliance Review Platform", version="3.0.0", lifespan=lifespan
)


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
    p: Principal = Depends(current_principal),
    db: AsyncSession = Depends(get_db),
):
    rid = uuid4().hex
    obj = Review(
        id=rid,
        tenant_id=p.tenant_id,
        created_by=p.sub,
        status="queued",
        input_text=body.statement,
        result_json=None,
        thread_id=f"review:{rid}",
    )
    await SqlReviewRepository(db).add(obj)
    await SqlAuditRepository(db).add(
        AuditEvent(
            id=uuid4().hex,
            tenant_id=p.tenant_id,
            review_id=rid,
            actor_id=p.sub,
            event_type="review.created",
            details={},
        )
    )
    await db.commit()
    # Queue receives primitive identifiers only. Outbox is recommended for strict atomic delivery.
    execute_review.delay(p.tenant_id, rid)
    return {"review_id": rid, "status": "queued"}


@app.get("/v1/reviews/{rid}")
async def get_review(
    rid: str,
    p: Principal = Depends(current_principal),
    db: AsyncSession = Depends(get_db),
):
    obj = await SqlReviewRepository(db).get(p.tenant_id, rid)
    if not obj:
        raise HTTPException(404, "Review not found")
    return {"review_id": obj.id, "status": obj.status, "result": obj.result_json}


@app.post("/v1/reviews/{rid}/decision", status_code=202)
async def decide(
    rid: str,
    body: DecisionRequest,
    p: Principal = Depends(require_role("reviewer")),
    db: AsyncSession = Depends(get_db),
):
    obj = await SqlReviewRepository(db).get(p.tenant_id, rid)
    if not obj:
        raise HTTPException(404, "Review not found")
    # Conditional update prevents two reviewers from successfully claiming the same decision.
    result = await db.execute(
        update(Review)
        .where(
            Review.id == rid,
            Review.tenant_id == p.tenant_id,
            Review.status == "needs_human",
        )
        .values(status="decision_queued")
    )
    if result.rowcount != 1:
        raise HTTPException(409, "Review is not awaiting a decision")
    await SqlAuditRepository(db).add(
        AuditEvent(
            id=uuid4().hex,
            tenant_id=p.tenant_id,
            review_id=rid,
            actor_id=p.sub,
            event_type="review.decision_queued",
            details={"decision": body.decision},
        )
    )
    await db.commit()
    resume_review.delay(
        p.tenant_id,
        rid,
        {"decision": body.decision, "comment": body.comment, "actor_id": p.sub},
    )
    return {"review_id": rid, "status": "decision_queued"}


@app.post("/v1/policies/ingest", status_code=201)
async def policy_ingest(
    body: PolicyIngestRequest,
    p: Principal = Depends(require_role("policy_admin")),
    db: AsyncSession = Depends(get_db),
):
    try:
        rows = await ingest_policy(
            db, p.tenant_id, body.code, body.version, body.title, body.text
        )
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    await SqlAuditRepository(db).add(
        AuditEvent(
            id=uuid4().hex,
            tenant_id=p.tenant_id,
            review_id="policy:" + rows[0].id,
            actor_id=p.sub,
            event_type="policy.ingested",
            details={"code": body.code, "version": body.version, "chunks": len(rows)},
        )
    )
    await db.commit()
    return {"policy_code": body.code, "version": body.version, "chunks": len(rows)}


@app.exception_handler(Exception)
async def unhandled(request, exc):
    log.exception("unhandled_api_error", path=request.url.path)
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
