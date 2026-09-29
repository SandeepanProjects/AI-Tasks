from sqlalchemy import select
from app.db.models import Review, Policy, AuditEvent


class SqlReviewRepository:
    def __init__(self, db):
        self.db = db

    async def get(self, tenant_id, rid):
        return await self.db.scalar(
            select(Review).where(Review.tenant_id == tenant_id, Review.id == rid)
        )

    async def add(self, obj):
        self.db.add(obj)
        await self.db.flush()

    async def save(self, obj):
        await self.db.flush()


class SqlPolicyRepository:
    def __init__(self, db):
        self.db = db

    async def add(self, obj):
        self.db.add(obj)
        await self.db.flush()


class SqlAuditRepository:
    def __init__(self, db):
        self.db = db

    async def add(self, obj):
        self.db.add(obj)
        await self.db.flush()
