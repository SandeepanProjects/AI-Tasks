from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.models import *  # noqa
from app.api.routes import health,policies,reviews
@asynccontextmanager
async def lifespan(app):
    # Local convenience only; use reviewed migrations in production.
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
app=FastAPI(title=settings.app_name,version="1.0.0",lifespan=lifespan)
app.include_router(health.router,prefix="/health")
app.include_router(policies.router,prefix=settings.api_prefix)
app.include_router(reviews.router,prefix=settings.api_prefix)
