import redis
import json


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


def get_cached_recommendations(user_id):

    data = redis_client.get(f"recs:{user_id}")

    if data:
        return json.loads(data)

    return None


def cache_recommendations(user_id, recommendations):

    redis_client.setex(
        f"recs:{user_id}",
        300,
        json.dumps(recommendations)
    )