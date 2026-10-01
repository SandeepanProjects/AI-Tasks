from sqlalchemy import select, or_
from app.db.models import Policy, Review


class SqlPolicyRepository:
    def __init__(self, db):
        self.db = db

    async def search(self, tenant_id, query, limit=6):
        terms = [x for x in query.lower().split() if len(x) > 2][:8]
        stmt = select(Policy).where(
            Policy.tenant_id == tenant_id, Policy.active.is_(True)
        )
        if terms:
            stmt = stmt.where(
                or_(
                    *[
                        Policy.text.ilike(f"%{t}%") | Policy.title.ilike(f"%{t}%")
                        for t in terms
                    ]
                )
            )
        return list(await self.db.scalars(stmt.limit(limit)))

    async def get_by_code(self, tenant_id, code):
        return await self.db.scalar(
            select(Policy)
            .where(
                Policy.tenant_id == tenant_id,
                Policy.code == code,
                Policy.active.is_(True),
            )
            .limit(1)
        )


class SqlReviewRepository:
    def __init__(self, db):
        self.db = db

    async def get(self, tenant_id, review_id):
        return await self.db.scalar(
            select(Review).where(Review.tenant_id == tenant_id, Review.id == review_id)
        )

    async def add(self, obj):
        self.db.add(obj)
        await self.db.commit()

    async def save(self, obj):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
