import json
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel
from pydantic import EmailStr
from sqlmodel import Field
from typing import Optional, List, Dict, Literal as TypeLiteral

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateGenZenUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str  # user or admin

class EmotionalState(BaseModel):
    intensity: int = Field(ge=1, le=5)
    type: str
    timestamp: datetime

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d['timestamp'] = d['timestamp'].isoformat()
        return d

class ChatSessionMetadata(BaseModel):
    emotional_history: List[EmotionalState] = []
    topic_engagement: Dict[str, int] = {}
    suggestion_enabled: bool = True
    last_memory_access: Optional[datetime] = None
    memory_context: List[str] = []  # List of relevant memories used in the session

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if d['last_memory_access']:
            d['last_memory_access'] = d['last_memory_access'].isoformat()
        return d

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        if d['last_memory_access']:
            d['last_memory_access'] = d['last_memory_access'].isoformat()
        return d

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None    # Optional field for existing sessions
    session_name: Optional[str] = None  # Optional allow users to name their sessions
    session_metadata: ChatSessionMetadata

class MemoryFactCreate(BaseModel):
    fact_type: TypeLiteral["personal_fact", "conversation_memory", "emotional_state"]
    content: str
    fact_metadata: dict

class MemoryFactResponse(MemoryFactCreate):
    id: UUID
    user_id: int
    created_at: datetime
    last_accessed: datetime

class SurveyResponseBase(BaseModel):
    emotional_intensity: Optional[int] = Field(ge=1, le=5)
    selected_topics: List[TypeLiteral[
        "Budgeting", "Career", "Coursework", "Internship", "Interviewing",
        "Major", "Mentoring", "Networking", "Post-Graduation", "Resume", "Other"
    ]]
    suggestions_enabled: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PreChatSurveyCreate(SurveyResponseBase):
    user_disclaimer_accepted: bool = True

class PostChatSurveyCreate(SurveyResponseBase):
    session_id: str  # Keep session_id for post-chat survey since it's tied to a specific chat
    feedback: Optional[str]

# Checkpoint-specific models (reusing existing structures where possible)
class CheckpointConfig(BaseModel):
    configurable: Dict[str, str]

class CheckpointMetadata(BaseModel):
    version: int
    timestamp: datetime

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        d['timestamp'] = d['timestamp'].isoformat()
        return d


