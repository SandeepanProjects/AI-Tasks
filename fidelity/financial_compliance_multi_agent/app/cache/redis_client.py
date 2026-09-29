import json
from redis.asyncio import Redis
from app.core.config import settings
redis=Redis.from_url(settings.redis_url,decode_responses=True)
async def cache_get(key):
    value=await redis.get(key); return json.loads(value) if value else None
async def cache_set(key,value,ttl=None):
    await redis.set(key,json.dumps(value),ex=ttl or settings.cache_ttl_seconds)
