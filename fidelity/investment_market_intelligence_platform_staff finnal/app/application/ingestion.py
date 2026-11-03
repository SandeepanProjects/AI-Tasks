from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from app.adapters.embeddings import EmbeddingProvider
from app.core.errors import ConflictError


class EvidenceIngestionService:
    """Tenant-scoped text ingestion with deterministic chunk IDs and deduplication."""
    def __init__(self, repository, embedder: EmbeddingProvider,
                 chunk_size: int = 1600, overlap: int = 200):
        if chunk_size <= overlap or overlap < 0:
            raise ValueError("chunk_size must be greater than non-negative overlap")
        self.repository = repository
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _chunk(self, content: str) -> list[str]:
        normalized = " ".join(content.split())
        if not normalized:
            raise ValueError("Evidence content cannot be empty")
        chunks, start = [], 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            # Prefer a sentence boundary near the end without creating tiny chunks.
            if end < len(normalized):
                boundary = normalized.rfind(". ", start + self.chunk_size // 2, end)
                if boundary > start:
                    end = boundary + 1
            chunks.append(normalized[start:end].strip())
            if end >= len(normalized):
                break
            start = max(end - self.overlap, start + 1)
        return chunks

    async def ingest(self, *, tenant_id: str, source_name: str, source_uri: str,
                     content: str, metadata: dict | None = None) -> int:
        if len(content) > 100_000:
            raise ValueError("Evidence content exceeds 100,000 characters")
        chunks = self._chunk(content)
        rows = []
        observed_at = datetime.now(timezone.utc)
        for index, chunk in enumerate(chunks):
            digest = hashlib.sha256(f"{source_uri}\0{chunk}".encode("utf-8")).hexdigest()
            vector = await self.embedder.embed(chunk)
            rows.append({"tenant_id": tenant_id, "source_name": source_name,
                "source_uri": source_uri, "observed_at": observed_at, "content": chunk,
                "content_hash": digest, "embedding": vector,
                "metadata": {**(metadata or {}), "chunk_index": index,
                             "chunk_count": len(chunks), "ingested_at": observed_at.isoformat()}})
        return await self.repository.add_many(tenant_id, rows)
