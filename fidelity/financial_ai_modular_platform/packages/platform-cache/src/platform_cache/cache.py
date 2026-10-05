import json
from typing import Any
import redis.asyncio as redis

class Cache:
    def __init__(self, url: str):
        self.client = redis.from_url(url, decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        value = await self.client.get(key)
        return None if value is None else json.loads(value)

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        await self.client.set(key, json.dumps(value), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
