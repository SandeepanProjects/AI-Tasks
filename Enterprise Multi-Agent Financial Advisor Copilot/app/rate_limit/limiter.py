import time
from app.db.redis import redis_client


class RateLimiter:

    def __init__(self, limit=10, window=60):

        self.limit = limit
        self.window = window


    def allow(self, user_id: str):

        key = f"rate:{user_id}"

        current = redis_client.get(key)

        now = int(time.time())

        if not current:

            redis_client.setex(
                key,
                self.window,
                1
            )

            return True

        count = int(current)

        if count >= self.limit:

            return False

        redis_client.incr(key)

        return True