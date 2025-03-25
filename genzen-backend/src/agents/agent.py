import os, uuid
from datetime import datetime
from dotenv import load_dotenv
import os, uuid
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from src.connections.db import checkpointer, memory_store
from src.agents.tools import mental_health, remember_information, recall_information
from src.agents.pii_masker import anonymize_pii

load_dotenv()

model_name = os.getenv("OPENAI_MODEL_NAME")


# Tool
tools = [mental_health, remember_information, recall_information]

# Define LLM with bound tools
llm = ChatOpenAI(model=model_name)
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful student assistant tasked with mental health counseling. When counseling, make sure to use the **answer** directly from the mental_health tool output")

# Node
def assistant(state: MessagesState):
    """Handles assistant responses, memory operations, and decides next actions."""
    
    # Extract all user messages as conversation history
    user_history = "\n".join(msg.content for msg in state["messages"])

    # Get the latest user message
    user_text = state["messages"][-1].content if state["messages"] else ""

    # Get user_id from config if available
    user_id = state.get("configurable", {}).get("user_id", "default_user")
    
    # Expanded trigger phrases to capture more user information
    trigger_facts = [
        "my name is", "i am", "i'm studying", "i love", "i study",
        "i'm interested in", "i like", "i enjoy", "i want to",
        "my major is", "i'm majoring in", "i'm a student of"
    ]
    # Expanded trigger phrases to capture more user information
    trigger_facts = [
        "my name is", "i am", "i'm studying", "i love", "i study",
        "i'm interested in", "i like", "i enjoy", "i want to",
        "my major is", "i'm majoring in", "i'm a student of"
    ]

    try:
        # Check if message contains any trigger phrases
        # Check if message contains any trigger phrases
        if any(trigger in user_text.lower() for trigger in trigger_facts):
            memory_id = uuid.uuid4().hex

            # Store personal fact with structured data

            # Store personal fact with structured data
            memory_store.put(
                (str(user_id), "facts"), 
                (str(user_id), "facts"), 
                memory_id,
                {
                    "content": user_text,
                    "timestamp": str(datetime.now()),
                    "type": "personal_fact",
                    "metadata": {
                        "source": "user_message",
                        "trigger": next((t for t in trigger_facts if t in user_text.lower()), None),
                        "message_length": len(user_text),
                        "has_name": any(trigger in user_text.lower() for trigger in ["my name is", "i am", "i'm"]),
                        "has_study": any(trigger in user_text.lower() for trigger in ["studying", "study", "major"]),
                        "has_interests": any(trigger in user_text.lower() for trigger in ["love", "like", "enjoy", "interested"])
                    }
                    "timestamp": str(datetime.now()),
                    "type": "personal_fact",
                    "metadata": {
                        "source": "user_message",
                        "trigger": next((t for t in trigger_facts if t in user_text.lower()), None),
                        "message_length": len(user_text),
                        "has_name": any(trigger in user_text.lower() for trigger in ["my name is", "i am", "i'm"]),
                        "has_study": any(trigger in user_text.lower() for trigger in ["studying", "study", "major"]),
                        "has_interests": any(trigger in user_text.lower() for trigger in ["love", "like", "enjoy", "interested"])
                    }
                }
            )
            print(f"Stored personal fact: {user_text}")  # Debug logging
            print(f"Stored personal fact: {user_text}")  # Debug logging
    except Exception as e:
        print(f"Error storing personal fact: {e}")
        print(f"Error storing personal fact: {e}")

    # Retrieve relevant memories if available
    memories = []
    try:
        # Try to retrieve from personal facts
        try:
            # Get all facts for the user using a pattern match
            facts = memory_store.get((str(user_id), "facts"), "*")  # Use * as wildcard
            if facts:
                for fact in facts:
                    if isinstance(fact, dict) and "content" in fact:
                        memories.append(f"I remember that {fact['content']}")
                        print(f"Retrieved fact: {fact['content']}")  # Debug logging
            # Get all facts for the user using a pattern match
            facts = memory_store.get((str(user_id), "facts"), "*")  # Use * as wildcard
            if facts:
                for fact in facts:
                    if isinstance(fact, dict) and "content" in fact:
                        memories.append(f"I remember that {fact['content']}")
                        print(f"Retrieved fact: {fact['content']}")  # Debug logging
        except Exception as e:
            print(f"Error retrieving facts: {e}")

        # Try to retrieve recent conversations
        try:
            # Get recent conversations using a pattern match
            conversations = memory_store.get((str(user_id), "conversations"), "*")  # Use * as wildcard
            if conversations:
                # Sort by timestamp and get last 3
                recent_convs = sorted(
                    conversations, 
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True
                )[:3]
                for conv in recent_convs:
                    if isinstance(conv, dict) and "content" in conv:
                        memories.append(f"Previous conversation: {conv['content']}")
                        print(f"Retrieved conversation: {conv['content']}")  # Debug logging

        # Try to retrieve recent conversations
        try:
            # Get recent conversations using a pattern match
            conversations = memory_store.get((str(user_id), "conversations"), "*")  # Use * as wildcard
            if conversations:
                # Sort by timestamp and get last 3
                recent_convs = sorted(
                    conversations, 
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True
                )[:3]
                for conv in recent_convs:
                    if isinstance(conv, dict) and "content" in conv:
                        memories.append(f"Previous conversation: {conv['content']}")
                        print(f"Retrieved conversation: {conv['content']}")  # Debug logging
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            
            print(f"Error retrieving conversations: {e}")
            
    except Exception as e:
        print(f"Error retrieving memories: {e}")
    
    # Add memories to system message if available
    memory_context = ""
    if memories:
        memory_context = "\n\nUser context from previous conversations:\n" + "\n".join(memories)
        print(f"Memory context: {memory_context}")  # Debug logging
        print(f"Memory context: {memory_context}")  # Debug logging

    context_system_message = SystemMessage(content=sys_msg.content + memory_context)

    # Call LLM with tool support
    response = llm_with_tools.invoke([context_system_message] + state["messages"])

    # Store important insights from this conversation
    if user_text and len(user_text) > 5:  # Only store substantial messages
        try:
            # Store this interaction for future reference
            memory_id = uuid.uuid4().hex
            memory_store.put(
                (str(user_id), "conversations"),
                (str(user_id), "conversations"),
                memory_id,
                {
                    "content": user_text,
                    "response": response.content,
                    "timestamp": str(datetime.now()),
                    "type": "conversation",
                    "metadata": {
                        "thread_id": state.get("configurable", {}).get("thread_id", "unknown_thread"),
                        "message_length": len(user_text),
                        "has_trigger": any(trigger in user_text.lower() for trigger in trigger_facts),
                        "response_length": len(response.content)
                    }
                }
            )
            print(f"Stored conversation: {user_text}")  # Debug logging
                    "timestamp": str(datetime.now()),
                    "type": "conversation",
                    "metadata": {
                        "thread_id": state.get("configurable", {}).get("thread_id", "unknown_thread"),
                        "message_length": len(user_text),
                        "has_trigger": any(trigger in user_text.lower() for trigger in trigger_facts),
                        "response_length": len(response.content)
                    }
                }
            )
            print(f"Stored conversation: {user_text}")  # Debug logging
        except Exception as e:
            print(f"Error storing conversation memory: {e}")
            print(f"Error storing conversation memory: {e}")
    
    return {
        "messages": [response],
        "user_history": user_history,
        "user_text": anonymize_pii(user_text),
    }

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile(checkpointer=checkpointer)