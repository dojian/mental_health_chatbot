import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime
from src.models.schemas import (
    ChatRequest, 
    ChatSessionMetadata,
    CheckpointConfig,
    CheckpointMetadata
)
import json

@pytest.mark.asyncio
@pytest.mark.memory
@pytest.mark.unit
async def test_short_term_memory(auth_client, checkpointer_fixture):
    """Test short-term memory (checkpointer) functionality"""
    client, token = auth_client
    
    # Create a test session
    session_id = str(uuid4())
    thread_id = str(uuid4())
    checkpoint_id = str(uuid4())
    
    # Create test data using existing models
    test_data = {
        "id": checkpoint_id,
        "channel_values": {
            "messages": [
                {"role": "user", "content": "Hello, my name is Test User"},
                {"role": "assistant", "content": "Nice to meet you, Test User!"}
            ]
        }
    }
    
    # Store data in checkpointer with required metadata using Pydantic models
    config = CheckpointConfig(configurable={
        "session_id": session_id,
        "thread_id": thread_id,
        "checkpoint_ns": "test_ns"
    })
    metadata = CheckpointMetadata(
        version=1,
        timestamp=datetime.now()
    )
    # Store messages directly in channel_values
    new_versions = {"channel_values": json.dumps(test_data["channel_values"])}
    
    # Pass data as dictionaries
    await checkpointer_fixture.aput(
        config.model_dump(),
        test_data,
        metadata.model_dump(),
        new_versions
    )
    
    # Retrieve data from checkpointer
    retrieved_data = await checkpointer_fixture.aget(config.model_dump())
    
    print("Retrieved data:", retrieved_data)
    print("Retrieved data type:", type(retrieved_data))
    if isinstance(retrieved_data, dict):
        print("Retrieved data keys:", retrieved_data.keys())
        if "channel_values" in retrieved_data:
            print("Channel values:", retrieved_data["channel_values"])
            # Parse the channel_values back from JSON string
            channel_values = json.loads(retrieved_data["channel_values"])
            assert channel_values["messages"] == test_data["channel_values"]["messages"]

    assert retrieved_data is not None
    assert retrieved_data["channel_values"]["messages"] == test_data["channel_values"]["messages"]

@pytest.mark.asyncio
@pytest.mark.memory
@pytest.mark.unit
async def test_long_term_memory(auth_client, memory_store_fixture):
    """Test long-term memory (memory store) functionality"""
    client, token = auth_client
    
    # Test data
    user_id = "test_user"
    namespace = ("test_user", "facts")
    memory_id = str(uuid4())
    test_data = {
        "content": "Test user is a software engineer",
        "timestamp": str(datetime.now()),
        "type": "personal_fact"
    }
    
    # Store data in memory store
    await memory_store_fixture.aput(namespace, memory_id, test_data)
    
    # Retrieve data from memory store
    retrieved_data = await memory_store_fixture.aget(namespace, memory_id)
    
    assert retrieved_data is not None
    assert retrieved_data == test_data

@pytest.mark.asyncio
@pytest.mark.memory
@pytest.mark.integration
async def test_memory_in_chat(auth_client, memory_store_fixture):
    """Test memory integration in chat functionality"""
    client, token = auth_client
    
    # Create session metadata
    session_metadata = ChatSessionMetadata(
        emotional_history=[],
        topic_engagement={},
        suggestion_enabled=True,
        memory_context=[]
    )
    
    # First interaction - store personal information
    query1 = "Hello, my name is Test User and I am a software engineer."
    response1 = await client.post(
        "/v1/agent-chat",
        json=ChatRequest(
            query=query1,
            session_metadata=session_metadata
        ).model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response1.status_code == 200
    response_data1 = response1.json()
    assert "response" in response_data1
    
    # Verify memory was stored
    namespace = ("test_user", "facts")
    facts = await memory_store_fixture.alist(namespace)
    assert len(facts) > 0
    assert any("software engineer" in str(fact) for fact in facts)
    
    # Second interaction - test memory recall
    query2 = "What is my profession?"
    response2 = await client.post(
        "/v1/agent-chat",
        json=ChatRequest(
            query=query2,
            session_id=response_data1["session_id"],
            session_metadata=session_metadata
        ).model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response2.status_code == 200
    response_data2 = response2.json()
    assert "software engineer" in response_data2["response"].lower()

@pytest.mark.asyncio
@pytest.mark.memory
@pytest.mark.unit
async def test_memory_cleanup(auth_client, memory_store_fixture):
    """Test memory cleanup functionality"""
    client, token = auth_client
    
    # Create test data
    user_id = "test_user"
    namespace = ("test_user", "facts")
    memory_id = str(uuid4())
    test_data = {
        "content": "Temporary fact",
        "timestamp": str(datetime.now()),
        "type": "personal_fact"
    }
    
    # Store data
    await memory_store_fixture.aput(namespace, memory_id, test_data)
    
    # Verify data is stored
    retrieved_data = await memory_store_fixture.aget(namespace, memory_id)
    assert retrieved_data is not None
    
    # Clean up data
    await memory_store_fixture.adelete(namespace, memory_id)
    
    # Verify data is removed
    cleaned_data = await memory_store_fixture.aget(namespace, memory_id)
    assert cleaned_data is None

@pytest.mark.asyncio
@pytest.mark.memory
@pytest.mark.integration
async def test_memory_persistence(auth_client, memory_store_fixture):
    """Test that memories persist across different sessions"""
    client, token = auth_client
    
    # Create session metadata
    session_metadata = ChatSessionMetadata(
        emotional_history=[],
        topic_engagement={},
        suggestion_enabled=True,
        memory_context=[]
    )
    
    # First session - store information
    query1 = "My favorite color is blue and I love programming."
    response1 = await client.post(
        "/v1/agent-chat",
        json=ChatRequest(
            query=query1,
            session_metadata=session_metadata
        ).model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response1.status_code == 200
    response_data1 = response1.json()
    assert "response" in response_data1
    
    # Verify memory was stored
    namespace = ("test_user", "facts")
    facts = await memory_store_fixture.alist(namespace)
    assert len(facts) > 0
    assert any("programming" in str(fact) for fact in facts)
    
    # Second session - retrieve stored information
    query2 = "What do I like?"
    response2 = await client.post(
        "/v1/agent-chat",
        json=ChatRequest(
            query=query2,
            session_metadata=session_metadata
        ).model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response2.status_code == 200
    response_data2 = response2.json()
    assert "programming" in response_data2["response"].lower() 