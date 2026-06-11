from app.db.redis import redis_client
import json
import hashlib


class RedisCache:

    @staticmethod
    def _key(prefix: str, data: str):

        hashed = hashlib.sha256(
            data.encode()
        ).hexdigest()

        return f"{prefix}:{hashed}"


    @staticmethod
    def get(prefix: str, data: str):

        key = RedisCache._key(
            prefix, data
        )

        value = redis_client.get(key)

        if value:

            return json.loads(value)

        return None


    @staticmethod
    def set(prefix: str, data: str, value, ttl=3600):

        key = RedisCache._key(
            prefix, data
        )

        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )