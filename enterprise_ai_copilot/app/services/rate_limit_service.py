import time
from app.core.config import settings
from app.core.redis import redis_client

class RateLimitService:
    async def allowed(self, identifier: str) -> bool:
        bucket = int(time.time()) // settings.rate_limit_window_seconds
        key = f"rl:{identifier}:{bucket}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, settings.rate_limit_window_seconds + 2)
        return count <= settings.rate_limit_requests
