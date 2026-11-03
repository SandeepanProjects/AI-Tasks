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

@pytest.mark.asyncio
async def test_idempotency_replay_returns_original_review():
    repo = InMemoryReviewRepository()
    original = Review("tenant-a", "user-a", "Analyze BTC", ["BTC"], 30)
    created, existing = await repo.add(original, "same-key-123")
    assert created is True and existing is None

    retry = Review("tenant-a", "user-a", "Analyze BTC", ["BTC"], 30)
    created, existing = await repo.add(retry, "same-key-123")
    assert created is False
    assert existing.id == original.id


@pytest.mark.asyncio
async def test_idempotency_rejects_same_key_with_different_payload():
    from app.core.errors import ConflictError
    repo = InMemoryReviewRepository()
    original = Review("tenant-a", "user-a", "Analyze BTC", ["BTC"], 30)
    await repo.add(original, "same-key-456")
    different = Review("tenant-a", "user-a", "Analyze ETH", ["ETH"], 30)
    with pytest.raises(ConflictError):
        await repo.add(different, "same-key-456")
