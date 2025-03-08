from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.models.models import GenZenUser, Session, ChatHistory
from src.connections.db import get_session
from langchain_openai import ChatOpenAI
import uuid


router = APIRouter()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

@router.post("/chat")
async def chat(
    query: str,
    session: Session = Depends(get_session),
    current_user: GenZenUser = Depends(get_current_user)
):
    """
    Handles user queries and returns responses from OpenAI.
    """

    # 1 - retrieve or create session_id for conversation
    session_id = f"{current_user.id}-{uuid.uuid4().hex}"

    # 2 - log users query in ChatHistory table
    user_message = ChatHistory(
        session_id=session_id,
        user_id=current_user.id,
        role="user",
        message=query,
    )
    session.add(user_message)
    session.commit()

    # 3 - send query to OpenAI via LangChain to get response
    try:
        openai_response = model(query)
        assistant_msg_txt = openai_response.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {e}"
        )
    
    # 4 - log assistant response in ChatHistory table
    assistant_message = ChatHistory(
        session_id=session_id,
        user_id=current_user.id,
        role="assistant",
        message=assistant_msg_txt,
    )
    session.add(assistant_message)
    session.commit()

    return {"response": assistant_msg_txt}