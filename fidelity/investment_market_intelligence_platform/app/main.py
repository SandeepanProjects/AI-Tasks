from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared clients here; close them in finally in a real deployment.
    yield

app = FastAPI(title="Investment Market Intelligence API", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/v1")

@app.get("/health/live", tags=["health"])
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready", tags=["health"])
async def readiness():
    # Replace with real DB/Redis/provider dependency checks.
    return {"status": "ready", "mock_mode": settings.mock_mode}
