from fastapi import APIRouter

from pydantic import BaseModel

from app.rag.generation.full_pipeline import AdvancedRAGPipeline


router = APIRouter()

pipeline = AdvancedRAGPipeline()


class QueryRequest(BaseModel):

    question: str

    metadata_filter: dict | None = None


@router.post("/rag/generate")
def generate_answer(request: QueryRequest):

    return pipeline.query(
        request.question,
        request.metadata_filter
    )