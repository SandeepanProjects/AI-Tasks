import hashlib
import json
from uuid import UUID
from app.domain.models import Review
from app.core.errors import ConflictError


class InMemoryReviewRepository:
    """Test adapter; never wired into the production application composition root."""
    def __init__(self):
        self.items = {}
        self.idempotency = {}

    async def add(self, review: Review, idempotency_key: str):
        key = (review.tenant_id, idempotency_key)
        digest = hashlib.sha256(json.dumps({"question": review.question, "assets": review.assets,
            "lookback_days": review.lookback_days, "purpose": review.purpose}, sort_keys=True).encode()).hexdigest()
        prior = self.idempotency.get(key)
        if prior:
            if prior[0] != digest:
                raise ConflictError("Idempotency key reused with a different request")
            return False, self.items[prior[1]][1]
        self.items[review.id] = (key, review)
        self.idempotency[key] = (digest, review.id)
        return True, None

    async def get(self, tenant_id: str, review_id: UUID):
        item = self.items.get(review_id)
        return item[1] if item and item[1].tenant_id == tenant_id else None

    async def save(self, review, expected_version=None):
        self.items[review.id] = (self.items[review.id][0], review)

    async def save_with_audit(self, review, expected_version, actor_id, action, details):
        await self.save(review, expected_version)

    async def requeue_failed(self, review, expected_version, actor_id):
        current = self.items[review.id][1]
        if current.version != expected_version:
            raise ConflictError("Concurrent review update detected")
        self.items[review.id] = (self.items[review.id][0], review)
