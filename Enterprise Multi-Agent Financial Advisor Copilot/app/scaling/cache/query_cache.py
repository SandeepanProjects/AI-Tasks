from app.scaling.cache.redis_cache import RedisCache


class QueryCache:

    PREFIX = "rag_query"

    @staticmethod
    def get(query: str):

        return RedisCache.get(
            QueryCache.PREFIX,
            query
        )


    @staticmethod
    def set(query: str, response: dict):

        RedisCache.set(
            QueryCache.PREFIX,
            query,
            response,
            ttl=1800
        )