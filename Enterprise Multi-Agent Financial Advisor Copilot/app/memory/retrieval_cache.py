# app/memory/retrieval_cache.py

import hashlib

from app.memory.redis_client import (
    redis_client
)


class RetrievalCache:

    @staticmethod
    def cache_key(
        query: str
    ):

        return hashlib.sha256(
            query.encode()
        ).hexdigest()


    async def get(
        self,
        query: str
    ):

        key = self.cache_key(query)

        return await redis_client.get_json(
            key
        )


    async def set(
        self,
        query: str,
        value
    ):

        key = self.cache_key(query)

        await redis_client.set_json(
            key,
            value,
            ttl=3600
        )