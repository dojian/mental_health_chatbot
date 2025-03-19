# from langgraph.graph import MessagesState
# from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
# from langchain_openai import ChatOpenAI

# from .tools import add, divide

# # Import Graph
# from langgraph.graph import START, StateGraph, END
# from langgraph.prebuilt import tools_condition, ToolNode




# tools = [add, divide]

# model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# model_with_tools = model.bind_tools(tools, parallel_tool_calls=False)
# sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")


# # state class to store messages and summary
# class State(MessagesState):
#     summary: str

# def call_model(state: State):
#     # get summary if it exists
#     summary = state.get("summary", "")

#     # if there is summary, add it to messages
#     if summary:
#         system_message = f"Summary of conversation earlier: {summary}"
#         messages = [HumanMessage(content=system_message)] + state["messages"]
#     else:
#         messages = state["messages"]
    
#     response = model.invoke(messages)
#     return {"messages": response}


# def summarize_conversation(state: State):
#     summary = state.get("summary", "")
#     if summary:
#         summary_message = (
#             f"This is summary of the conversation so far: {summary}\n\n"
#             "Extend the summary by taking into account the new messages above:"
#         )
#     else:
#         summary_message = "Create a summary of the conversation above:"

#     # add prompt to history
#     messages = state['messages'] + [HumanMessage(content=summary_message)]
#     response = model.invoke(messages)

#     delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
#     return {
#         "summary": response.content, "messages": delete_messages
#     }

# def should_continue(state:State):
#     """Return the next node to execute."""
#     messages = state['messages']
#     if len(messages) >6:
#         return "summarize_conversation"

#     return END


# def assistant(state: MessagesState):
#     return {
#         "messages": [model_with_tools.invoke([sys_msg] + state["messages"])],
#     }


# # Memory workflow
# workflow = StateGraph(State)
# workflow.add_node("conversation", call_model)
# workflow.add_node(summarize_conversation)

# workflow.add_edge(START, "conversation")
# workflow.add_conditional_edges("conversation", should_continue)
# workflow.add_edge("summarize_conversation", END)

# graph = workflow.compile()

# def create_agent(store,checkpointer):
#     workflow = StateGraph(State)
#     workflow.add_node("conversation", call_model)
#     workflow.add_node(summarize_conversation)

#     workflow.add_edge(START, "conversation")
#     workflow.add_conditional_edges("conversation", should_continue)
#     workflow.add_edge("summarize_conversation", END)

#     return workflow.compile(store=store, checkpointer=checkpointer)

# # Build graph
# # builder = StateGraph(MessagesState)

# # builder.add_node("assistant", assistant)
# # builder.add_node("tools", ToolNode(tools))

# # builder.add_edge(START, "assistant")
# # builder.add_conditional_edges(
# #     "assistant",
# #     # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
# #     # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
# #     tools_condition,
# # )
# # builder.add_edge("tools", "assistant")

# # graph = builder.compile()