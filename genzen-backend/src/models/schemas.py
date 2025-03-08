from pydantic import BaseModel
from pydantic import EmailStr

class User(BaseModel):
    id: int | None = None
    username: str
    hashed_password: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str # user or admin