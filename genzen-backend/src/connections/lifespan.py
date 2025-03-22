
from fastapi import FastAPI
import logging
from collections.abc import AsyncIterator
from datetime import datetime
from contextlib import asynccontextmanager

from src.connections.redis_cache import init_redis, close_redis_client
from src.connections.db import create_db_and_tables, setup_checkpoint_and_memory_store
from src.connections.llm_client import get_llm_client

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    ### Logging ###
    logging.basicConfig(filename="genzen-backend-log.log", encoding="utf-8", level=logging.DEBUG)
    logging.info("--------------------------------------------------------------------------------")
    logging.info(f"{datetime.now()}: LIFESPAN - Startup Initiated")
    
    ### Redis ###
    await init_redis(app)
    logging.info(f"{datetime.now()}: LIFESPAN - Connected to Redis")

    ### OpenAI ###
    model = get_llm_client()
    logging.info(f"{datetime.now()}: LIFESPAN - Connected to OpenAI - gpt-4o-mini")
    
    ### Postgres ###
    create_db_and_tables()
    setup_checkpoint_and_memory_store()
    logging.info(f"{datetime.now()}: LIFESPAN - Connected to Postgres")
    yield

    await close_redis_client()
    logging.info(f"{datetime.now()}: LIFESPAN - Shutdown Complete")
    logging.info("--------------------------------------------------------------------------------")