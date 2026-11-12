from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.security.tenant_context import set_tenant_context
from app.auth import current_principal, Principal
from fastapi import Depends

engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with Session() as db:
        yield db

async def get_tenant_db(principal: Principal = Depends(current_principal)):
    async with Session() as db:
        await set_tenant_context(db, principal.tenant_id)
        yield db
