import pytest
import asyncio
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, create_engine
from src.main import app
from src.connections.redis_cache import init_redis
from src.connections.db import sync_pool, async_pool, memory_store, checkpointer
from src.connections.database_creation import delete_database
from src.utils.config_setting import Settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

settings = Settings()

# Test database connection string
TEST_POSTGRES_CONN_STRING = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
TEST_DB_NAME = f"test_{settings.POSTGRES_DB}"

def create_test_database():
    """Create test database if it doesn't exist"""
    conn = psycopg2.connect(TEST_POSTGRES_CONN_STRING)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if database exists
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
    exists = cur.fetchone()
    
    if not exists:
        cur.execute(f'CREATE DATABASE {TEST_DB_NAME}')
    
    cur.close()
    conn.close()

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db(event_loop):
    """Create and setup test database"""
    # Create test database
    create_test_database()
    
    # Create engine for test database
    test_engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DB_NAME}?sslmode=disable",
        echo=False
    )
    
    # Setup tables and memory systems
    from src.connections.db import create_db_and_tables, setup_checkpoint_and_memory_store
    create_db_and_tables()
    memory_store, checkpointer = await setup_checkpoint_and_memory_store()

    yield test_engine, memory_store, checkpointer

    # Cleanup
    delete_database()

@pytest_asyncio.fixture(scope="module")
async def auth_client(event_loop, test_db):
    """Initialize the Redis cache and the test client by registering a test user and logging in."""
    print("Initializing auth client...")
    # Initialize the Redis cache
    await init_redis(app)
    print("Redis cache initialized")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        test_user = {
            "username": "testclient",
            "password": "testpassword123",
            "email": "testclient@example.com",
            "role": "user"
        }
        # register the test user
        print("Registering test user...")
        register_response = await client.post("/auth/register", json=test_user)
        print(f"Register response status: {register_response.status_code}")
        if register_response.status_code != 200:
            print(f"Register response: {register_response.text}")

        # login the test user
        print("Logging in test user...")
        response = await client.post(
            "/auth/login", 
            data={"username": "testclient", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Login response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Login response: {response.text}")
            raise Exception("Failed to login test user")
        
        token = response.json()["access_token"]
        print("Successfully logged in test user")
        yield client, token

@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a fresh database session for each test"""
    with Session(test_db[0]) as session:
        yield session
        session.rollback()

@pytest_asyncio.fixture(scope="function")
async def memory_store_fixture(test_db):
    """Provide access to memory store for testing"""
    _, memory_store, _ = test_db
    yield memory_store

@pytest_asyncio.fixture(scope="function")
async def checkpointer_fixture(test_db):
    """Provide access to checkpointer for testing"""
    _, _, checkpointer = test_db
    yield checkpointer 