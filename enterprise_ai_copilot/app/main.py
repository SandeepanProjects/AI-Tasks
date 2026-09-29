from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import auth, documents, jobs, chat, hitl
from app.core.config import settings
from app.core.redis import redis_client
from app.services.rate_limit_service import RateLimitService

app = FastAPI(title=settings.app_name, version="1.0.0")

for router in [auth.router, documents.router, jobs.router, chat.router, hitl.router]:
    app.include_router(router, prefix=settings.api_v1_prefix)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in {"/health", "/docs", "/openapi.json"}:
        return await call_next(request)

    identifier = request.client.host if request.client else "unknown"
    try:
        allowed = await RateLimitService().allowed(identifier)
    except Exception:
        # Explicit demo availability policy: fail open.
        # Security-sensitive deployments may choose fail closed.
        allowed = True

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )
    return await call_next(request)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await redis_client.aclose()
