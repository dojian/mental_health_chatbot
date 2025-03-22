from pydantic import BaseModel
from pydantic import EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class CreateGenZenUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str # user or admin

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None    # Optional field for existing sessions
    session_name: Optional[str] = None  # Optional allow users to name their sessions
