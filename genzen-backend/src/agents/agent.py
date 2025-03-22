from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

import os, uuid
from datetime import datetime

from src.connections.db import checkpointer, memory_store
from dotenv import load_dotenv
load_dotenv()

from src.agents.tools import mental_health, remember_information, recall_information

model_name = os.getenv("OPENAI_MODEL_NAME")
# Tool
tools = [mental_health, remember_information, recall_information]

# Define LLM with bound tools
llm = ChatOpenAI(model=model_name)
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful student assistant tasked with mental health counseling. When counseling, make sure to use the **answer** directly from the mental_health tool output")

# Initialize checkpointer for short-term memory (session-specific)


# Node
def assistant(state: MessagesState):
    """Handles assistant responses, memory operations, and decides next actions."""

    
    # Extract all user messages as conversation history
    user_history = "\n".join(msg.content for msg in state["messages"])

    # Get the latest user message
    user_text = state["messages"][-1].content if state["messages"] else ""

    # Get user_id from config if available
    user_id = state.get("configurable", {}).get("user_id", "default_user")
    
    trigger_facts = ["my name is", "i am", "i'm studying"]

    try:
        if any(trigger in user_text.lower() for trigger in trigger_facts):
            memory_id = uuid.uuid4().hex
            memory_store.put(
                f"user:{user_id}:facts",
                memory_id,
                {
                    "content": user_text,
                    "timestamp": str(datetime.now())
                }
            )
    except Exception as e:
        print(f"Error storing memory: {e}")

    # Retrieve relevant memories if available
    memories = []
    try:
        # Try to retrieve from personal facts
        try:
            fact_results = memory_store.search(f"user:{user_id}:facts")
        except Exception as e:
            print(f"Error retrieving facts: {e}")
            fact_results = []
        # fact_results = memory_store.search(f"user:{user_id}:facts", user_text, limit=4)
        if fact_results:
            memories.extend([f"I remember that {fact['content']}" for fact in fact_results])

        # Try to retrieve conversation history
        try:
            memory_results = memory_store.search(f"user:{user_id}")
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            memory_results = []
        # memory_results = memory_store.search(f"user:{user_id}", user_text, limit=4)
        if memory_results:
            memories.extend([f"Previous memory: {mem['content']}" for mem in memory_results])
    except Exception as e:
        print(f"Error retrieving memories: {e}")
    
    # Add memories to system message if available
    memory_context = ""
    if memories:
        memory_context = "\n\nUser context from previous conversations:\n" + "\n".join(memories)

    context_system_message = SystemMessage(content=sys_msg.content + memory_context)

    # Call LLM with tool support
    response = llm_with_tools.invoke([context_system_message] + state["messages"])

    # Store important insights from this conversation
    if user_text and len(user_text) > 5:  # Only store substantial messages
        try:
            # Store this interaction for future reference
            memory_id = uuid.uuid4().hex
            memory_store.put(
                f"user:{user_id}",
                memory_id,
                {
                    "content": user_text,
                    "response": response.content,
                    "timestamp": str(datetime.now())
                }
            )
        except Exception as e:
            print(f"Error storing memory: {e}")
    
    return {
        "messages": [response],
        "user_history": user_history,
        "user_text": user_text,
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

# messages=[HumanMessage(content="I feel sad about my calculus homework. I don't know if i will be about to understand the chain rule.")]
# # Invoke graph
# result=graph. invoke({"messages": messages})

# # Print the messages
# for m in result['messages']:
#     m.pretty_print()
