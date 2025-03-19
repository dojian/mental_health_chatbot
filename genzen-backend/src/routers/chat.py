from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from src.models.db_models import GenZenUser, ChatHistory, ChatSession
from src.models.pydantic_schemas import ChatRequest
from src.connections.db import get_session, get_postgres_url
from src.utils.auth_utils import get_current_user
from langchain_openai import ChatOpenAI
import uuid
import logging


### Single Agent ###
from src.test_agent.tools import empathic_dialogue
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode
from src.connections.llm_client import get_llm_client

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


### Connect to Sqlite ###
local_file = "test_agent.db"
conn = sqlite3.connect(local_file, check_same_thread=False)
memory = SqliteSaver(conn)

### Structure State ###
class State(MessagesState):
    summary: str

### Tool set up
tools = [empathic_dialogue]
llm = get_llm_client(temperature=0.2)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

sys_msg = SystemMessage(content="You are a helpful assistant tasked with providing empathic support.")

def assistant(state: MessagesState):
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])],
    }

# Define the logic to call the model
def call_model(state: State):
    # Get summary if it exists
    summary = state.get("summary", "")
    print(f"Summary: {summary}")
    # If there is summary, then we add it
    if summary:
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"
        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": response}

def summarize_conversation(state: State):
    # First, we get any existing summary
    summary = state.get("summary", "")
    # Create our summarization prompt 
    if summary:
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm_with_tools.invoke(messages)
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

def build_agent():
    builder = StateGraph(State)
    builder.add_node("talker", call_model)
    builder.add_node(summarize_conversation)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "talker")
    builder.add_conditional_edges("talker", summarize_conversation)
    builder.add_edge("summarize_conversation", END)

    # builder.add_edge(START, "assistant")
    # builder.add_conditional_edges(
    #     "assistant",
    #     # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    #     # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    #     tools_condition,
    #     END
    # )
    # builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=memory)

react_graph = build_agent()


router = APIRouter()


# link memory to graph from fastapi startup
logging.basicConfig(filename=f"genzen-backend-log.log", encoding="utf-8", level=logging.DEBUG)

@router.post("/single_agent/chat")
async def chat_with_agent(request: Request, chat_request: ChatRequest, current_user = Depends(get_current_user)):
    """
    Test to reachout using the agent
    """
    user_id = current_user.id
    config = {
        "configurable": {
            "thread_id": f"user_{user_id}_session_1",  # Short-term memory (conversation history)
            # "checkpoint_ns": f"user_{user_id}_attributes",  # Long-term memory (user-specific attributes)
        }
    }
    messages = react_graph.invoke({"messages": [{"role": "user", "content": chat_request.query}]}, config=config)
    # graph = create_agent(store=request.app.state.store, checkpointer=request.app.state.checkpointer)

    ### find thread_id built with user_id and messages





    context = {
        "chat_request_query": chat_request.query, 
        "current_id": user_id,
        "messages": messages['messages'][-1],
    }
    return {"response": context}

    # if not request.app.state.store or not request.app.state.checkpointer:
    #     raise HTTPException(status_code=500, detail="Memory not initialized")
    # logging.debug(f"Store: {request.app.state.store}")
    # logging.debug(f"Checkpointer: {request.app.state.checkpointer}")
    # # Create agent
    # graph = create_agent(store=request.app.state.store, checkpointer=request.app.state.checkpointer)
    # state = [HumanMessage(content=chat_request.query)]
    # config = {"configurable": {"thread_id": "lit-test"}}

    # # logging.info(f"Request Session ID: {request.session_id}")

    # try:
    #     result = await graph.ainvoke(state, config=config)
    #     return {"success": True, "response": result}
    # except Exception as e:
    #     logging.error(f"Error: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))




    # messages = [HumanMessage(content=request.query)]
    # assistant_response = graph.invoke({"messages": messages})
    # return assistant_response
# @router.post("/test_agent/chat")
# async def chat_with_agent(request: ChatRequest, session = Depends(get_session), current_user = Depends(get_current_user)):
#     """
#     Test to reachout using the agent
#     """
#     print(f"Request Session ID: {request.session_id}")
#     logging.info(f"Request Session ID: {request.session_id}")
#     print(f"Current User ID: {current_user.id}")
#     logging.info(f"Current User ID: {current_user.id}")
#     print(f"Session ID: {session}")

#     messages = [HumanMessage(content=request.query)]
#     assistant_response = graph.invoke({"messages": messages})
#     return assistant_response




# @router.post("/agent/chat")
# async def chat_with_agent(request: ChatRequest, session = Depends(get_session), current_user = Depends(get_current_user)):
#     """
#     Test to reachout using the agent
#     """

#     config = {"configurable": {"thread_id": request.session_id}}
#     assistant_response = graph.invoke({"messages": [{"role": "user", "content": request.query}]})
#     return assistant_response

# @router.get("/chat/sessions")
# async def list_chat_sessions(session = Depends(get_session), current_user = Depends(get_current_user)):
#     """
#     List all chat sessions for the current user."
#     """
#     chat_sessions = (
#         session.query(ChatSession)
#         .filter(ChatSession.user_id == current_user.id)
#         .all()
#     )
#     session_list = []
#     for chat_session in chat_sessions:
#         first_message = (
#             session.query(ChatHistory)
#             .filter(
#                 ChatHistory.session_id == chat_session.session_id,
#                 ChatHistory.role == "user"
#             )
#             .order_by(ChatHistory.timestamp)
#             .first()
#         )
#         session_list.append({
#             "session_id": chat_session.session_id,
#             "created_at": chat_session.created_at,
#             "first_query": first_message.message if first_message else "No query yet"
#         })
#     return session_list


# @router.post("/chat")
# async def chat(
#     request: ChatRequest,
#     session: Session = Depends(get_session),
#     current_user: GenZenUser = Depends(get_current_user),
# ):
#     """
#     Handles user queries, stores them in ChatHistory, sends them to OpenAI,
#     and stores and returns both the query and OpenAI's response.
#     """
    
#     # Step 1: Retrieve or create a session
#     if request.session_id:
#         # Retrieve existing session
#         chat_session = session.query(ChatSession).filter(
#             ChatSession.session_id == request.session_id,
#             ChatSession.user_id == current_user.id,
#         ).first()
#         if not chat_session:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Chat session not found"
#             )
#         session_id = request.session_id
#     else:
#         # Create a new session if no session_id is provided
#         session_id = f"{current_user.id}-{uuid.uuid4().hex}"
#         chat_session = ChatSession(
#             session_id=session_id,
#             user_id=current_user.id,
#         )
#         session.add(chat_session)
#         session.commit()

#     # Step 2: Retrieve existing chat history for this session
#     existing_messages = (
#         session.query(ChatHistory)
#         .filter(ChatHistory.session_id == session_id)
#         .order_by(ChatHistory.timestamp)
#         .all()
#     )

#     # Format history for OpenAI
#     messages = [
#         {"role": message.role, "content": message.message}
#         for message in existing_messages
#     ]

#     # Add user's new query to the message list
#     messages.append({"role": "user", "content": request.query})

#     # Step 3: Send query + history to OpenAI and get response
#     try:
#         openai_response = model(messages)
#         assistant_msg_txt = openai_response.content
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error communicating with OpenAI: {str(e)}"
#         )

#     # Step 4: Log user's query and assistant's response in ChatHistory
#     user_message = ChatHistory(
#         session_id=session_id,
#         user_id=current_user.id,
#         role="user",
#         message=request.query,
#     )
    
#     assistant_message = ChatHistory(
#         session_id=session_id,
#         user_id=current_user.id,
#         role="assistant",
#         message=assistant_msg_txt,
#     )
    
#     # Use add_all to add multiple objects at once
#     session.add_all([user_message, assistant_message])
#     session.commit()

#     return {
#         "session_id": session_id,
#         "query": request.query,
#         "response": assistant_msg_txt,
#     }