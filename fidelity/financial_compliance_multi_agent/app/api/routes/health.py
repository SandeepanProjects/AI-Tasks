from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import engine
from app.cache.redis_client import redis
router=APIRouter(tags=["health"])
@router.get("/live")
async def live(): return {"status":"alive"}
@router.get("/ready")
async def ready():
    checks={}
    try:
        async with engine.connect() as c: await c.execute(text("SELECT 1"))
        checks["postgres"]="ok"
    except Exception: checks["postgres"]="error"
    try: await redis.ping(); checks["redis"]="ok"
    except Exception: checks["redis"]="error"
    return {"status":"ready" if all(v=="ok" for v in checks.values()) else "degraded","checks":checks}
