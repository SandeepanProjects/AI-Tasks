from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Document:
    document_id: str
    tenant_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Evidence:
    chunk_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
