import pytest
from app.adapters.in_memory import InMemoryReviewRepository
from app.domain.models import Review

@pytest.mark.asyncio
async def test_repository_is_tenant_scoped():
    repo = InMemoryReviewRepository()
    review = Review(tenant_id="tenant-a", created_by="user-a", question="test", assets=["BTC"], lookback_days=7)
    await repo.add(review)
    assert await repo.get("tenant-a", review.id) is review
    assert await repo.get("tenant-b", review.id) is None
