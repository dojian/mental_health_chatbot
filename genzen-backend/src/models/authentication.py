from pydantic import BaseModel

class User(BaseModel):
    id: int | None = None
    username: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
