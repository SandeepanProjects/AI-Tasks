# app/schemas/rag_schema.py

from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User query for RAG pipeline",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of retrieved chunks",
    )


class SourceDocument(BaseModel):
    document_name: str
    chunk_index: int
    content: str
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str

    sources: List[SourceDocument]

    latency_ms: Optional[float] = None

    cached: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class IngestRequest(BaseModel):
    folder_path: str = Field(
        ...,
        description="Path to documents folder",
    )


class IngestResponse(BaseModel):
    status: str
    documents_processed: int
    chunks_created: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

