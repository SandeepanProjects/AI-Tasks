import pytest
from app.application.ingestion import EvidenceIngestionService

class FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 384

class FakeRepository:
    def __init__(self): self.rows = []
    async def add_many(self, tenant_id, rows):
        self.rows.extend(rows)
        return len(rows)

@pytest.mark.asyncio
async def test_ingestion_chunks_and_embeds_content():
    repo = FakeRepository()
    service = EvidenceIngestionService(repo, FakeEmbedder(), chunk_size=40, overlap=8)
    count = await service.ingest(tenant_id="tenant-a", source_name="test", source_uri="fixture://test",
        content="This is a sufficiently long paragraph. " * 8)
    assert count > 1
    assert all(row["tenant_id"] == "tenant-a" for row in repo.rows)
    assert all(len(row["embedding"]) == 384 for row in repo.rows)
    assert all(row["content_hash"] for row in repo.rows)

@pytest.mark.asyncio
async def test_ingestion_rejects_empty_content():
    service = EvidenceIngestionService(FakeRepository(), FakeEmbedder())
    with pytest.raises(ValueError):
        await service.ingest(tenant_id="t", source_name="s", source_uri="u", content="   ")
