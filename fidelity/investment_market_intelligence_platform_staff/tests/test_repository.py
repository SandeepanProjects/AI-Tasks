import pytest
from app.adapters.in_memory import InMemoryReviewRepository
from app.domain.models import Review
@pytest.mark.asyncio
async def test_tenant_scope():
    repo=InMemoryReviewRepository()
    r=Review("a","u","q",["BTC"],7)
    await repo.add(r,"key")
    assert await repo.get("a",r.id) is r
    assert await repo.get("b",r.id) is None
