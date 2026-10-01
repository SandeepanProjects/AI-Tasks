from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.auth import current_user, require, Principal
from app.domain.schemas import ReviewRequest, DecisionRequest
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("/reviews")
async def create(
    body: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    u: Principal = Depends(require("reviewer", "admin")),
):
    s = ReviewService(db)
    obj = await s.create(u.tenant_id, u.subject, body.statement)
    obj = await s.run(u.tenant_id, obj.id)
    return {"review_id": obj.id, "status": obj.status, "result": obj.result_json}


@router.get("/reviews/{rid}")
async def get(
    rid: str, db: AsyncSession = Depends(get_db), u: Principal = Depends(current_user)
):
    obj = await ReviewService(db).reviews.get(u.tenant_id, rid)
    if not obj:
        raise HTTPException(404, "Not found")
    return {"review_id": obj.id, "status": obj.status, "result": obj.result_json}


@router.post("/reviews/{rid}/decision")
async def decision(
    rid: str,
    b: DecisionRequest,
    db: AsyncSession = Depends(get_db),
    u: Principal = Depends(require("approver", "admin")),
):
    try:
        obj = await ReviewService(db).decide(
            u.tenant_id, rid, u.subject, b.decision, b.comment
        )
    except LookupError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))
    return {"review_id": obj.id, "status": obj.status, "result": obj.result_json}


@router.get("/health")
async def health():
    return {"status": "ok"}
