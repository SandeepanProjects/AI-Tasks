from pydantic import BaseModel
from typing import List, Dict, Any


class Source(BaseModel):

    id: str
    score: float
    text: str


class RAGResponse(BaseModel):

    question: str

    answer: str

    summary: str

    risk_level: str

    compliance_notes: List[str]

    sources: List[Source]