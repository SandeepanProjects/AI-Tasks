import json
from app.core.config import settings
from app.core.redis import redis_client

class CacheService:
    async def get(self, key: str):
        value = await redis_client.get(key)
        return None if value is None else json.loads(value)

    async def set(self, key: str, value, ttl: int | None = None):
        await redis_client.set(key, json.dumps(value),
                               ex=ttl or settings.cache_ttl_seconds)

    async def delete(self, key: str):
        await redis_client.delete(key)
