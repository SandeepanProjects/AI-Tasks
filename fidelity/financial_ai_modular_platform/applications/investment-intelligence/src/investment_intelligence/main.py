from fastapi import FastAPI, Depends
from pydantic import BaseModel
from platform_auth.dependencies import get_principal
from platform_auth.models import Principal
from ai_llm.factory import create_llm
from .services.analysis_service import InvestmentAnalysisService

app = FastAPI(title="Investment Market Intelligence API", version="1.0.0")

class AnalysisRequest(BaseModel):
    question: str
    asset: str = "BTC"

class AnalysisResponse(BaseModel):
    status: str
    analysis: str
    evidence_count: int

@app.get("/health")
async def health():
    return {"status": "ok", "application": "investment-intelligence"}

@app.post("/v1/analysis", response_model=AnalysisResponse)
async def analysis(
    request: AnalysisRequest,
    principal: Principal = Depends(get_principal),
):
    return await InvestmentAnalysisService(create_llm()).analyze(
        principal.tenant_id, request.question, request.asset
    )
