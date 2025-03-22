import pytest
import asyncio
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.connections.redis_cache import init_redis
# from src.connections.db import memory_store
# from src.utils.auth_utils import get_user
# from src.connections.db import get_session
# from pprint import pprint

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

### Set up the test client
@pytest_asyncio.fixture(scope="module")
async def auth_client(event_loop):
    """
    Initialize the Redis cache and the test client by registering a test user and logging in.
    Returns the test client and the token.
    """
    # Initialize the Redis cache
    await init_redis(app)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        test_user = {
            "username": "testclient",
            "password": "testpassword123",
            "email": "testclient@example.com",
            "role": "user"
        }
        # register the test user
        register_response = await client.post("/auth/register", json=test_user)

        # login the test user
        response = await client.post(
            "/auth/login", 
            data={"username": "testclient", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        yield client, token


@pytest.mark.asyncio
async def test_agent_chat(auth_client):
    client, token = auth_client

    query = "Hello, my name is Lit."

    response = await client.post(
        "/v1/agent-chat", 
        json = {
            "query": query
        }, 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["query"] == query

    session_id = response.json()["session_id"]
    response_2 = await client.post(
        "/v1/agent-chat", 
        json = {
            "query": "What is my name?",
            "session_id": session_id
        }, 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_2.status_code == 200
    assert response_2.json()["query"] == "What is my name?"

    answer = response_2.json()["response"]
    assert "Lit" in answer


@pytest.mark.asyncio
async def test_agent_chat_with_memory(auth_client):
    """
    Test the agent chat with memory.
    """
    client, token = auth_client

    query1 = "Hello, my name is Lit and I am a Data Scientist."
    # First interaction
    response1 = await client.post(
        "/v1/agent-chat",
        json = {
            "query": query1
        },
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )

    session_id = response1.json()["session_id"]

    assert response1.status_code == 200
    assert "Lit" in response1.json()["response"]

    # TODO:Verify memory was stored

    # Second interaction
    query2 = "What's my name and what do I do?"

    response2 = await client.post(
        "/v1/agent-chat",
        json = {
            "query": query2,
            "session_id": session_id
        },
        headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    assert response2.status_code == 200
    assert "Lit" in response2.json()["response"]
    assert "Data Scientist" in response2.json()["response"]

    # TODO: Verify memory was stored
    # TODO: Delete memory
