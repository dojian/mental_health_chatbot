from src.test_agent.tools import add, divide
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from src.connections.llm_client import get_llm_client

import sqlite3
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver as SqliteSaver
local_file = "test_agent.sqlite"
conn = sqlite3.connect(local_file, check_same_thread=False)
memory = SqliteSaver(conn)

class State(MessagesState):
    summary: str

tools = [add, divide]
llm = get_llm_client(temperature=.2)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

def assistant(state: MessagesState):
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])],
    }

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
    END
)
builder.add_edge("tools", "assistant")

react_graph = builder.compile(checkpointer=memory)


# messages = [HumanMessage(content="tell me a joke")]
# messages = [HumanMessage(content="Add 6 and 4. Divide the output by 5")]
messages = [HumanMessage(content="what was the joke again?")]


# Short Term: Thread ID will be sed for each session aka conversation - save full convo his for the session in checkpoints
# Long Term: Checkpoint_ns (namespace) to store user-specific attributes or summarized data that spans convos - shared across threads
# Summarize convos: part of the long term - use checkpoint_ns to store summarizaed associated with a user

# thread_id: unique identifier for a single conversation or session
# checkpint_ns: namespace for user-specific long-term memory
# checkpoint_id: specific checkpoint within a thread


config = {"configurable": {"thread_id": "lit-another"}}
# config = {"configurable": {"thread_id": "lit-test"}}

messages = react_graph.invoke({"messages": messages}, config=config)

for m in messages['messages']:
    m.pretty_print()