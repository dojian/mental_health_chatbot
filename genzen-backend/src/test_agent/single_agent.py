from src.test_agent.tools import empathic_dialogue
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from src.connections.llm_client import get_llm_client
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.runnables import Runnable
from pprint import pprint

### Medium
# from langchain_core.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import Runnable
# from langchain_aws import ChatBedrock
# import boto3
# from typing import Annotated
# from typing_extensions import TypedDict
# from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
# from langgraph.prebuilt import ToolNode
# from langgraph.prebuilt import tools_condition

# Create Memory
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
local_file = "test_agent.sqlite"
conn = sqlite3.connect(local_file, check_same_thread=False)
memory = SqliteSaver(conn)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# Create LLM with tools
tools = [empathic_dialogue]
llm = get_llm_client(temperature=.2)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# Set up Agent called Assistant
# sys_msg = SystemMessage(content="You are a helpful assistant tasked to find the root cause of a user's emotional state.")

def run_llm(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(State)
builder.add_node("llm", run_llm)

builder.add_edge(START, "llm")
builder.add_edge("llm", END)

graph = builder.compile()

messages = [HumanMessage(content="tell me a joke")]
result = graph.invoke({"messages": messages})
print(result['messages'][-1].content)

# builder = StateGraph(MessagesState)
# builder.add_node("assistant", assistant)
# builder.add_node("tools", ToolNode(tools))

# builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     tools_condition,
#     END
# )
# builder.add_edge("tools", "assistant")

# react_graph = builder.compile(checkpointer=memory)










# messages = [HumanMessage(content="tell me a joke")]
# messages = [HumanMessage(content="Add 6 and 4. Divide the output by 5")]
# messages = [HumanMessage(content="what was the joke again?")]


# Short Term: Thread ID will be sed for each session aka conversation - save full convo his for the session in checkpoints
# Long Term: Checkpoint_ns (namespace) to store user-specific attributes or summarized data that spans convos - shared across threads
# Summarize convos: part of the long term - use checkpoint_ns to store summarizaed associated with a user

# thread_id: unique identifier for a single conversation or session
# checkpint_ns: namespace for user-specific long-term memory
# checkpoint_id: specific checkpoint within a thread


# config = {"configurable": {"thread_id": "lit-another"}}
# config = {"configurable": {"thread_id": "lit-test"}}

# messages = react_graph.invoke({"messages": messages}, config=config)

# for m in messages['messages']:
#     m.pretty_print()