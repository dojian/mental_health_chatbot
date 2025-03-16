
from fastapi import FastAPI
import logging
from collections.abc import AsyncIterator
from datetime import datetime
from contextlib import asynccontextmanager

from src.connections.redis_cache import init_redis
from src.connections.db import create_db_and_tables
from src.connections.llm_client import get_llm_client

### PostgresSaver ###
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from src.connections.db import get_postgres_url

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    ### Logging ###
    logging.basicConfig(filename="genzen-backend-log.log", encoding="utf-8", level=logging.DEBUG)
    logging.info(f"{datetime.now()}: LIFESPAN - Startup Initiated")
    
    ### Redis ###
    await init_redis(app)
    logging.info(f"{datetime.now()}: LIFESPAN - Connected to Redis")

    ### OpenAI ###
    # model = get_llm_client()
    # logging.info(f"{datetime.now()}: LIFESPAN - Connected to OpenAI - gpt-4o-mini")

    ### Postgres ###
    async with AsyncPostgresStore.from_conn_string(
        get_postgres_url(),
    ) as store:
        async with AsyncPostgresSaver.from_conn_string(
            get_postgres_url()
        ) as checkpointer:
            app.state.store = store
            app.state.checkpointer = checkpointer

            await app.state.store.setup()
            await app.state.checkpointer.setup()
    create_db_and_tables()
    logging.info(f"{datetime.now()}: LIFESPAN - Connected to Postgres")
    yield
    await app.state.redis.close()
    logging.info(f"{datetime.now()}: LIFESPAN - Shutdown Complete")
    logging.info("--------------------------------------------------------------------------------")
