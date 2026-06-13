# app/db/health.py

from sqlalchemy import text

from app.db.postgres import AsyncSessionLocal


async def db_health():

    async with AsyncSessionLocal() as session:

        await session.execute(
            text("SELECT 1")
        )

    return True