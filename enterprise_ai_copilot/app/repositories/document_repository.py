from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant_id: str, title: str, content: str):
        document = Document(tenant_id=tenant_id, title=title, content=content)
        self.db.add(document)
        await self.db.flush()
        return document

    async def get_for_tenant(self, document_id: str, tenant_id: str):
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()
