# models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# =========================
# 🧑 User Request Schema
# =========================
class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    query: str = Field(..., description="User question or prompt")


# =========================
# 🤖 Chat Response Schema
# =========================
class ChatResponse(BaseModel):
    user_id: str
    query: str
    response: str
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =========================
# 🐘 PostgreSQL Chat History Model
# =========================
class ChatHistory(BaseModel):
    id: Optional[int] = None
    user_id: str
    query: str
    response: str
    created_at: Optional[datetime] = None


# =========================
# 🔍 Document Schema (for Qdrant ingestion)
# =========================
class DocumentChunk(BaseModel):
    id: str
    text: str
    embedding: List[float]
    metadata: dict = Field(default_factory=dict)


# =========================
# 📦 Qdrant Search Result
# =========================
class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict


# =========================
# 🧠 RAG Context Builder Output
# =========================
class RAGContext(BaseModel):
    query: str
    context: str
    sources: List[str]