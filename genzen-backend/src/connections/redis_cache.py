### Redis ###
from fastapi_cache import FastAPICache
# from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
# from joblib import load
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