### Redis ###
from fastapi import Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

import os
from dotenv import load_dotenv
load_dotenv()

async def init_redis(app) -> None:
    """
    Create a Redis client and initialize FastAPI Cache.
    This cliennt is stored in app.state for later use.
    """
    redis = aioredis.from_url(os.getenv("REDIS_URL"))
    await redis.ping()
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    app.state.redis = redis

def get_redis_client(request: Request):
    """
    Get the Redis client from the request.
    """
    redis_instance = getattr(request.app.state, "redis", None)
    if redis_instance is None:
        raise RuntimeError("Redis client has not been initialized")
    return redis_instance