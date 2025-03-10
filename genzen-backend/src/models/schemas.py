from pydantic import BaseModel
from pydantic import EmailStr

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
    session_id: str | None = None  # Optional field for existing sessions
