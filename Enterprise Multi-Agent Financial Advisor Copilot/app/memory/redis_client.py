# pip install redis

# app/memory/redis_client.py

import json

from redis.asyncio import Redis

from app.config.settings import settings


class RedisClient:

    def __init__(self):

        self.client = Redis.from_url(

            settings.REDIS_URL,

            encoding="utf-8",

            decode_responses=True
        )


    async def get_json(
        self,
        key: str
    ):

        value = await self.client.get(key)

        if value:

            return json.loads(value)

        return None


    async def set_json(
        self,
        key: str,
        value,
        ttl: int = 3600
    ):

        await self.client.setex(
            key,
            ttl,
            json.dumps(value)
        )


    async def delete(
        self,
        key: str
    ):

        await self.client.delete(key)


redis_client = RedisClient()