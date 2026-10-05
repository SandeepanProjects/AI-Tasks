from fastapi import FastAPI, Depends
from pydantic import BaseModel
from platform_auth.dependencies import get_principal
from platform_auth.models import Principal
from platform_observability.logging import configure_logging
from ai_llm.factory import create_llm
from .services.review_service import ComplianceReviewService

configure_logging()
app = FastAPI(title="Financial Compliance Review API", version="1.0.0")

class ReviewRequest(BaseModel):
    material: str
    material_type: str = "advisor_communication"

class ReviewResponse(BaseModel):
    status: str
    risk: str
    summary: str
    citations: list[str]
    requires_human_approval: bool

@app.get("/health")
async def health():
    return {"status": "ok", "application": "financial-compliance"}

@app.post("/v1/reviews", response_model=ReviewResponse)
async def review(
    request: ReviewRequest,
    principal: Principal = Depends(get_principal),
):
    service = ComplianceReviewService(llm=create_llm())
    return await service.review(
        tenant_id=principal.tenant_id,
        material=request.material,
        material_type=request.material_type,
    )
