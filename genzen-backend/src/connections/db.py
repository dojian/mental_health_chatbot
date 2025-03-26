from psycopg_pool import ConnectionPool
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langchain_openai import OpenAIEmbeddings
from src.utils.config_setting import Settings
import atexit
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

pool = ConnectionPool(
    conninfo=POSTGRES_CONN_STRING,
    max_size=20,
    kwargs=connection_kwargs,
    open=True
)
checkpointer = PostgresSaver(pool)

# Initialize OpenAI embeddings for semantic search
embeddings = OpenAIEmbeddings()
# Set up memory store with vector search - only pass required parameters
memory_store = PostgresStore(pool)

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
def setup_checkpoint_and_memory_store():
    """
    Initialize the Postgres db for checkpointer and store.
    """
    try:
        # Print connection parameters (obscuring password)
        conn_info = POSTGRES_CONN_STRING.replace(settings.POSTGRES_PASSWORD, "********")
        print(f"Setting up memory systems with connection: {conn_info}")
        
        # Initialize checkpointer for short-term memory
        print("Setting up checkpointer...")
        checkpointer.setup()
        print("Checkpointer initialized successfully.")
        
        # Initialize memory store for long-term memory
        print("Setting up memory store...")
        memory_store.setup()
        print("Memory store initialized successfully.")
        
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
            memory_store.put(test_namespace, test_id, test_data)
            print("Successfully stored test data")
            
            # Try to retrieve the test item
            retrieved = memory_store.get(test_namespace, test_id)
            if retrieved:
                print("Successfully retrieved test data")
            else:
                print("Warning: Could not retrieve test data")
            
            # Clean up test data
            memory_store.delete(test_namespace, test_id)
            print("Memory store verification complete")
        except Exception as e:
            print(f"Warning: Memory store verification failed: {e}")
            raise
            
    except Exception as e:
        print(f"Error setting up memory systems: {e}")
        import traceback
        traceback.print_exc()
        raise
    
def close_pool():
    """Gracefully close the connection pool."""
    if pool is not None:
        print("Closing database connection pool...")
        pool.close()

# Ensure the pool is closed when the program exits
atexit.register(close_pool)