from uuid import UUID
from app.domain.models import Review, Evidence

class InMemoryReviewRepository:
    def __init__(self): self.items: dict[UUID, Review] = {}
    async def add(self, review: Review) -> None: self.items[review.id] = review
    async def get(self, tenant_id: str, review_id: UUID) -> Review | None:
        item = self.items.get(review_id)
        return item if item and item.tenant_id == tenant_id else None
    async def save(self, review: Review) -> None: self.items[review.id] = review

class FixtureEvidenceRepository:
    async def search(self, tenant_id: str, query: str, limit: int = 8) -> list[Evidence]:
        from datetime import datetime, timezone
        from hashlib import sha256
        content = ("Illustrative fixture only: market prices are volatile; this record is not live data. "
                   "Use a licensed provider and verify timestamps before analysis.")
        return [Evidence("fixture-market-001", "local-fixture", "fixture://market/001",
                         datetime.now(timezone.utc), content, sha256(content.encode()).hexdigest(),
                         tenant_id, {"kind": "fixture", "live": False})]
