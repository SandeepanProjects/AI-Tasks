from uuid import UUID
from app.domain.models import Review
class InMemoryReviewRepository:
    def __init__(self): self.items={}
    async def add(self,review,idempotency_key): 
        if any(v[0]==idempotency_key for v in self.items.values()): return False
        self.items[review.id]=(idempotency_key,review); return True
    async def get(self,tenant_id,review_id):
        item=self.items.get(review_id); return item[1] if item and item[1].tenant_id==tenant_id else None
    async def save(self,review,expected_version=None): self.items[review.id]=(self.items[review.id][0],review)
