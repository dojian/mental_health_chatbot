from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

from src.agents.tools import mental_health

import os
from dotenv import load_dotenv
load_dotenv()

# Tool
tools = [mental_health]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define LLM with bound tools
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful student assistant tasked with managing calendar and mental health counseling.")

# Node
def assistant(state: MessagesState):
    """Handles assistant responses and decides next actions."""
    
    # Extract all user messages as conversation history
    user_history = "\n".join(
        msg.content for msg in state["messages"]
    )

    # Get the latest user message
    user_text = state["messages"][-1].content if state["messages"] else ""

    # Call LLM with tool support
    response = llm_with_tools.invoke([sys_msg] + state["messages"])

    return {
        "messages": [response],
        "user_history": user_history,  # Store conversation history in state
        "user_text": user_text,        # Store last user message in state
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
graph = builder.compile()

# messages = [HumanMessage(content="I feel sad about not having friends. I am anxious about making new friends. I was bullied when I was younger.")]

# messages = graph.invoke({"messages": messages})

# for m in messages['messages']:
#     m.pretty_print()