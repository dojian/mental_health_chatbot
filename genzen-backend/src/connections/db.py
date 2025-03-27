from psycopg_pool import ConnectionPool, AsyncConnectionPool
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from langchain_openai import OpenAIEmbeddings
from src.utils.config_setting import Settings
import atexit
import asyncio
settings = Settings()

POSTGRES_CONN_STRING = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}?sslmode=disable"
engine = create_engine(
    POSTGRES_CONN_STRING,
    echo=settings.DEBUG
)

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0
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
    """
    global sync_pool, async_pool, memory_store, checkpointer
    try:
        # Print connection parameters (obscuring password)
        conn_info = POSTGRES_CONN_STRING.replace(settings.POSTGRES_PASSWORD, "********")
        print(f"Setting up memory systems with connection: {conn_info}")
        
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
        await checkpointer.setup()  # This will create necessary tables
        print("Checkpointer initialized successfully.")
        
        # Verify PostgresStore is working with a simple put/get operation
        try:
            print("Testing memory store with a simple operation...")
            test_namespace = ("test_user", "test_facts")
            test_id = "test_id"
            test_data = {
                "content": "Test message",
                "timestamp": str(datetime.now())
            }
            
            # Store test data
            await memory_store.aput(test_namespace, test_id, test_data)
            print("Successfully stored test data")
            
            # Try to retrieve the test item
            retrieved = await memory_store.aget(test_namespace, test_id)
            if retrieved:
                print("Successfully retrieved test data")
            else:
                print("Warning: Could not retrieve test data")
            
            # Clean up test data
            await memory_store.adelete(test_namespace, test_id)
            print("Memory store verification complete")
        except Exception as e:
            print(f"Warning: Memory store verification failed: {e}")
            raise
            
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