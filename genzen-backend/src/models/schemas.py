from pydantic import BaseModel
from pydantic import EmailStr
from typing import Optional, List, Dict
from sqlmodel import Field
from typing import Literal

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateGenZenUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str # user or admin

class ChatSessionMetadata(BaseModel):
    emotional_history: List[int] = []
    topic_engagement: Dict[str, int] = {}
    suggestion_enabled: bool = True

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None    # Optional field for existing sessions
    session_name: Optional[str] = None  # Optional allow users to name their sessions
    metadata: ChatSessionMetadata

class SurveyResponseBase(BaseModel):
    session_id: str
    emotional_intensity: Optional[int] = Field(ge=1, le=5)
    selected_topics: List[Literal["Budgeting", "Career", "Coursework", "Internship", "Interviewing",
                                  "Major", "Mentoring", "Networking", "Post-Graduation", "Resume", "Other"]] = ["General"]
    suggestions_enabled: bool = True

class PreChatSurveyCreate(SurveyResponseBase):
    user_disclaimer_accepted: bool = True

class PostChatSurveyCreate(SurveyResponseBase):
    feedback: Optional[str]


