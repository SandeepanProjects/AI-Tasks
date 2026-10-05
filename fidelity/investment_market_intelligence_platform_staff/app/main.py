from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.observability import CorrelationIdMiddleware

configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield

app=FastAPI(title="Investment Market Intelligence API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router,prefix="/v1")
app.mount("/metrics",make_asgi_app())

@app.get("/health/live",tags=["health"])
async def liveness(): return {"status":"alive"}

@app.get("/health/ready",tags=["health"])
async def readiness():
    from app.db.session import engine
    try:
        async with engine.connect() as conn: await conn.exec_driver_sql("SELECT 1")
        return {"status":"ready"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(503,"dependencies unavailable")
