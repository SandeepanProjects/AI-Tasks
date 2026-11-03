from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.api.routes import router
from app.api.ingestion import router as ingestion_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.observability import CorrelationIdMiddleware

configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield
    from app.db.session import engine
    await engine.dispose()

app=FastAPI(title="Investment Market Intelligence API",version="1.0.0",lifespan=lifespan)
if settings.cors_origins:
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
        allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Correlation-ID"])
app.add_middleware(CorrelationIdMiddleware)
app.include_router(router,prefix="/v1")
app.include_router(ingestion_router,prefix="/v1")
app.mount("/metrics",make_asgi_app())

@app.get("/health/live",tags=["health"])
async def liveness(): return {"status":"alive"}

@app.get("/health/ready",tags=["health"])
async def readiness():
    from app.db.session import engine
    from redis.asyncio import Redis
    try:
        async with engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1")
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        try:
            await redis.ping()
        finally:
            await redis.aclose()
        return {"status": "ready", "dependencies": {"postgres": "ok", "redis": "ok"}}
    except Exception:
        raise HTTPException(503, "dependencies unavailable")
