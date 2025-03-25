### Redis ###
from fastapi import Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.utils.config_setting import Settings

settings = Settings()

session_redis = None
cache_redis = None

async def init_redis(app) -> None:
    """
    Create a Redis client and initialize FastAPI Cache.
    This cliennt is stored in app.state for later use.
    """
    global cache_redis, session_redis

    cache_redis = aioredis.from_url(settings.REDIS_URL)
    await cache_redis.ping()
    FastAPICache.init(RedisBackend(cache_redis), prefix="fastapi-cache")

    session_redis = aioredis.from_url(settings.REDIS_URL)
    await session_redis.ping()

    app.state.cache_redis = cache_redis
    app.state.session_redis = session_redis

def get_redis_client(request: Request):
    """
    Get the Redis client from the request.
    """
    redis_instance = getattr(request.app.state, "session_redis", None)
    if redis_instance is None:
        raise RuntimeError("Redis client has not been initialized")
    return redis_instance


async def close_redis_client():
    """
    Close the Redis client.
    """
    global session_redis, cache_redis
    if session_redis:
        await session_redis.close()
    if cache_redis:
        await cache_redis.close()