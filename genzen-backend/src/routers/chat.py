import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from langchain_core.messages import HumanMessage, AIMessage
from src.models.models import GenZenUser, ChatHistory, ChatSession, SurveyData
from src.models.schemas import ChatRequest, PreChatSurveyCreate, PostChatSurveyCreate
from src.connections.db import get_session
from src.utils.auth_utils import get_current_user
from src.agents.agent import graph, llm, llm_with_tools

router = APIRouter()

model = llm
model_with_tools = llm_with_tools

@router.get("/chat/sessions")
async def list_chat_sessions(session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    List all chat sessions for the current user."
    """
    chat_sessions = (
        session.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .all()
    )
    session_list = []
    for chat_session in chat_sessions:
        first_message = (
            session.query(ChatHistory)
            .filter(
                ChatHistory.session_id == chat_session.session_id,
                ChatHistory.role == "user"
            )
            .order_by(ChatHistory.timestamp)
            .first()
        )
        session_list.append({
            "session_id": chat_session.session_id,
            "created_at": chat_session.created_at,
            "first_query": first_message.message if first_message else "No query yet"
        })
    return session_list

@router.post("/agent-chat")
async def agent_chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: GenZenUser = Depends(get_current_user),
):
    """
    Handles user queries using the langgraph agent.
    """
    try:

        # Step 1: Handle session management
        if request.session_id:
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
            session_id = f"{current_user.id}-{uuid.uuid4().hex}"
            chat_session = ChatSession(
                user_id=current_user.id,
                session_id=session_id,
                session_name=request.session_name
            )
            session.add(chat_session)
            session.commit()
        
        # Retrieve existing chat history
        existing_messages = session.query(ChatHistory).filter(
            ChatHistory.session_id == session_id).order_by(
                ChatHistory.timestamp).all()

        # Step 2: Format the message for the agent
        # The agent expects a list of messages
        messages = [
            HumanMessage(content=msg.message) if msg.role == "user" else AIMessage(content=msg.message)
            for msg in existing_messages
        ]
        messages.append(HumanMessage(content=request.query))  

        # Step 2.1: Configure thread_id and user_id for memory
        config = {
            "configurable": {
                "thread_id": session_id,  # For short-term memory (checkpointer)
                "user_id": str(current_user.id),  # For long-term memory (store)
                "checkpoint_ns": f"user_{current_user.id}",  # Optional namespace for checkpoints
                "session_context": {
                    "session_id": session_id,
                    "session_name": chat_session.session_name if hasattr(chat_session, "session_name") else None,
                    "session_start": str(chat_session.created_at) if hasattr(chat_session, "created_at") else None
                }
            }
        }

        # Step 3: Invoke the agent
        agent_response = graph.invoke({"messages": messages}, config)
        
        # Extract the response from the agent's output
        assistant_msg_txt = agent_response["messages"][-1].content

        # Step 4: Log the interaction
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
        
        session.add_all([user_message, assistant_message])
        session.commit()

        return {
            "session_id": session_id,
            "query": request.query,
            "response": assistant_msg_txt,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in agent chat: {str(e)}"
        )

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
    try:

        # Step 1: Retrieve or create a session
        if request.session_id:
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
        # Serialize metadata with datetime handling
        metadata = request.session_metadata.model_dump()
        
        user_message = ChatHistory(
            session_id=session_id,
            user_id=current_user.id,
            role="user",
            message=request.query,
            chat_metadata=metadata
        )
        
        assistant_message = ChatHistory(
            session_id=session_id,
            user_id=current_user.id,
            role="assistant",
            message=assistant_msg_txt,
            chat_metadata={}  # Empty metadata for assistant messages
        )
        
        session.add_all([user_message, assistant_message])
        session.commit()

        return {
            "session_id": session_id,
            "query": request.query,
            "response": assistant_msg_txt,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in chat endpoint: {str(e)}"
        )

@router.post("/pre-chat-survey")
async def submit_pre_chat_survey(
    survey: PreChatSurveyCreate,
    session: Session = Depends(get_session),
    current_user: GenZenUser = Depends(get_current_user),
):
    # First check if the chat session exists
    chat_session = session.query(ChatSession).filter(
        ChatSession.session_id == survey.session_id,
        ChatSession.user_id == current_user.id,
    ).first()

    # If chat session doesn't exist, create it
    if not chat_session:
        chat_session = ChatSession(
            session_id=survey.session_id,
            user_id=current_user.id,
            session_name=None  # Can be updated later
        )
        session.add(chat_session)
        session.commit()

    # Now create the survey data
    survey_data = SurveyData(
        user_id=current_user.id,
        session_id=survey.session_id,
        survey_type="pre",
        survey_data=survey.model_dump()
    )
    session.add(survey_data)
    session.commit()
    return {"message": "Pre-chat survey submitted successfully"}

@router.post("/post-chat-survey")
async def submit_post_chat_survey(
    survey: PostChatSurveyCreate,
    session: Session = Depends(get_session),
    current_user: GenZenUser = Depends(get_current_user),
):
    survey_data = SurveyData(
        user_id = current_user.id,
        session_id = survey.session_id,
        survey_type = "post",
        data = survey.model_dump()
    )
    session.add(survey_data)
    session.commit()
    return {"message": "Post-chat survey submitted successfully"} 