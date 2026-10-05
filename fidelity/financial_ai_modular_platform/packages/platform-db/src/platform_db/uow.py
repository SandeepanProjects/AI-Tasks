from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def transaction(session: AsyncSession):
    async with session.begin():
        yield session
