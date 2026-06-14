# db/redis_client.py

import redis
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_cache(key):
    return r.get(key)


def set_cache(key, value, ttl=3600):
    r.setex(key, ttl, value)


def get_session(user_id):
    return r.get(f"session:{user_id}")


def set_session(user_id, context):
    r.set(f"session:{user_id}", context, ex=1800)