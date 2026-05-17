from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def query_rag(request: QueryRequest):
    response = rag_service.query(request.query)

    return {
        "answer": response,
    }