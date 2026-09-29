from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job

class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_tenant(self, job_id: str, tenant_id: str):
        result = await self.db.execute(
            select(Job).where(Job.id == job_id, Job.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
