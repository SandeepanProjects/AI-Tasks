import hashlib
import json

from app.db.redis_client import redis_client


class RetrievalCache:
    def create_key(self, query):
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query):
        key = self.create_key(query)

        value = redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    def set(self, query, value):
        key = self.create_key(query)

        redis_client.setex(
            key,
            3600,
            json.dumps(value),
        )