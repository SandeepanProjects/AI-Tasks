from fastapi import APIRouter

from pydantic import BaseModel

from app.rag.service.rag_service import RAGService


router = APIRouter()

rag_service = RAGService()


class QueryRequest(BaseModel):

    question: str

    metadata_filter: dict | None = None

    top_k: int = 5


@router.post("/rag/query")
def query_rag(request: QueryRequest):

    result = rag_service.query(
        question=request.question,
        metadata_filter=request.metadata_filter,
        top_k=request.top_k
    )

    return result




from fastapi import FastAPI

from app.api.v1.health import router as health_router

from app.rag.api.rag_routes import router as rag_router


app = FastAPI(
    title="Financial Advisor Copilot"
)

app.include_router(health_router)

app.include_router(rag_router)