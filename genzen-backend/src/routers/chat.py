from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.models.models import GenZenUser, ChatHistory, ChatSession
from src.models.schemas import ChatRequest
from src.connections.db import get_session
from src.utils.auth_utils import get_current_user
from langchain_openai import ChatOpenAI
import uuid, logging


router = APIRouter()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

@router.get("/chat/sessions")
async def list_chat_sessions(session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    List all chat sessions for the current user."
    """
    chat_sessions = session.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return [{
        "session_id": cs.session_id,
        "created_at": cs.created_at
    } for cs in chat_sessions]


# @router.get("/chat")
# async def chat(
#     request: ChatRequest,
#     session: Session = Depends(get_session),
#     current_user: GenZenUser = Depends(get_current_user),
# ):
#     """
#     Handles user queries and returns responses from OpenAI.
#     """

#     context = {}

#     # context['request'] = request.query

#     if request.session_id:
#         chat_session = session.query(ChatSession).filter(
#             ChatSession.session_id == session_id,
#             ChatSession.user_id == current_user.id
#         ).first()
#         if not chat_session:
#             raise HTTPException(status__code=status.HTTP_404_NOT_FOUND, detail="Session not found")
#     else:
#         session_id = f"{current_user.id}-{uuid.uuid4().hex}"
#         chat_session = ChatSession(
#             session_id=session_id,
#             user_id=current_user.id,
#         )
#         session.add(chat_session)
#         session.commit()
    
#     context["session_id"] = session_id

#     existing_messages = (
#         session.query(ChatHistory)
#         .filter(ChatHistory.session_id == session_id)
#         .order_by(ChatHistory.timestamp)
#         .all()
#     )

#     messages = [
#         {"role": message.role, "content": message.message}
#         for message in existing_messages
#     ]

#     messages.append({"role": "user", "content": request.query})

#     try:
#         openai_response = model.invoke(messages)
#         assistant_msg_txt = openai_response.content
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error communicating with OpenAI: {str(e)}"
#         )

#     user_msg = ChatHistory(
#         session_id=session_id,
#         user_id=current_user.id,
#         role="user",
#         message=request.query,
#     )

#     context['assistant_msg_txt'] = assistant_msg_txt

#     assistant_msg = ChatHistory(
#         session_id=session_id,
#         user_id=current_user.id,
#         role="assistant",
#         message=assistant_msg_txt,
#     )
#     session.add_all([user_msg, assistant_msg])
#     session.commit()


#     return {"response": context}

@router.post("/chat")
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: GenZenUser = Depends(get_current_user),
):
    """
    Handles user queries, stores them in ChatHistory, sends them to OpenAI,
    and stores and returns both the query and OpenAI's response.
    """
    
    # Step 1: Retrieve or create a session
    if request.session_id:
        # Retrieve existing session
        chat_session = session.query(ChatSession).filter(
            ChatSession.session_id == request.session_id,
            ChatSession.user_id == current_user.id,
        ).first()
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        session_id = request.session_id
    else:
        # Create a new session if no session_id is provided
        session_id = f"{current_user.id}-{uuid.uuid4().hex}"
        chat_session = ChatSession(
            session_id=session_id,
            user_id=current_user.id,
        )
        session.add(chat_session)
        session.commit()

    # Step 2: Retrieve existing chat history for this session
    existing_messages = (
        session.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.timestamp)
        .all()
    )

    # Format history for OpenAI
    messages = [
        {"role": message.role, "content": message.message}
        for message in existing_messages
    ]

    # Add user's new query to the message list
    messages.append({"role": "user", "content": request.query})

    # Step 3: Send query + history to OpenAI and get response
    try:
        openai_response = model(messages)
        assistant_msg_txt = openai_response.content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with OpenAI: {str(e)}"
        )

    # Step 4: Log user's query and assistant's response in ChatHistory
    user_message = ChatHistory(
        session_id=session_id,
        user_id=current_user.id,
        role="user",
        message=request.query,
    )
    
    assistant_message = ChatHistory(
        session_id=session_id,
        user_id=current_user.id,
        role="assistant",
        message=assistant_msg_txt,
    )
    
    # Use add_all to add multiple objects at once
    session.add_all([user_message, assistant_message])
    session.commit()

    return {
        "session_id": session_id,
        "query": request.query,
        "response": assistant_msg_txt,
    }