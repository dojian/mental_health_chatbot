import uuid
from datetime import datetime

from src.agents.agent import memory_store

async def save_to_long_term_memory(user_id, content, metadata=None):
    """
    Save information to long-term memory.
    """
    memory_id = uuid.uuid4().hex
    namespace = f"user:{user_id}"

    memory_data = {
        "content": content,
        "timestamp": str(datetime.now()),
        "metadata": metadata or {}
    }

    await memory_store.aput(namespace, memory_id, memory_data)
    return memory_id

async def retrieve_from_long_term_memory(user_id, query, limit=5):
    """
    Retrieve information from long-term memory.
    """
    namespace = f"user:{user_id}"
    results = await memory_store.asearch(query, namespace=namespace, limit=limit)
    return results

# async def search_memories(user_id, query, limit=5):
#     """
#     Search memories for relevant information.
#     """
#     namespace = str(user_id)
#     results = await memory_store.asearch(query, namespace=namespace, limit=limit)
#     return results