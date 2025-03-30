from psycopg_pool import ConnectionPool, AsyncConnectionPool
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from langchain_openai import OpenAIEmbeddings
from src.utils.config_setting import Settings
import atexit
import asyncio
from psycopg.rows import dict_row

settings = Settings()

POSTGRES_CONN_STRING = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}?sslmode=disable"
engine = create_engine(
    POSTGRES_CONN_STRING,
    echo=settings.DEBUG
)

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
    "row_factory": dict_row
}

# Initialize variables that will be set up later
sync_pool = None
async_pool = None
memory_store = None
checkpointer = None

def get_connection():
    """
    Get a connection to the Postgres database.
    """
    return engine

def get_session():
    """
    Get a session for the Postgres database.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
# Setup checkpoint and memory store
async def setup_checkpoint_and_memory_store():
    """
    Initialize the Postgres db for checkpointer and store.
    Returns:
        tuple: (memory_store, checkpointer)
    """
    try:
        # Print connection parameters (obscuring password)
        conn_info = POSTGRES_CONN_STRING.replace(settings.POSTGRES_PASSWORD, "********")

        if settings.DEBUG:
            print(f"Setting up memory systems with connection: {conn_info}")
        else:
            print(f"Setting up memory systems to database")
        
        # Initialize connection pools
        print("Setting up connection pools...")
        sync_pool = ConnectionPool(
            conninfo=POSTGRES_CONN_STRING,
            max_size=20,
            kwargs=connection_kwargs,
            open=True
        )
        print("Sync pool initialized")
        async_pool = AsyncConnectionPool(
            conninfo=POSTGRES_CONN_STRING,
            max_size=20,
            kwargs=connection_kwargs,
            open=True
        )
        print("Async pool initialized")
        
        # Initialize memory store with async pool
        print("Setting up memory store...")
        memory_store = AsyncPostgresStore(async_pool)
        await memory_store.setup()
        print("Memory store initialized successfully.")
        
        # Initialize checkpointer with async pool
        print("Setting up checkpointer...")
        checkpointer = AsyncPostgresSaver(async_pool)
        await checkpointer.setup()
        print("Checkpointer initialized successfully.")
        
        return memory_store, checkpointer
            
    except Exception as e:
        print(f"Error setting up memory systems: {e}")
        import traceback
        traceback.print_exc()
        raise
    
async def close_pools():
    """Gracefully close the connection pools."""
    if sync_pool is not None:
        print("Closing sync connection pool...")
        sync_pool.close()
    if async_pool is not None:
        print("Closing async connection pool...")
        await async_pool.close()

# Ensure the pools are closed when the program exits
atexit.register(lambda: asyncio.run(close_pools()))