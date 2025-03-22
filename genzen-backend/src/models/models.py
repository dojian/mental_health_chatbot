# from typing import Annotated

from sqlmodel import Field, SQLModel, Relationship
import datetime
from pydantic import EmailStr
from sqlalchemy import String

class GenZenUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    email: EmailStr = Field(
        sa_type=String(),
        unique=True,
        index=True,
        nullable=False,
        description="Email address of the user"
    )
    role: str

class ChatSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, index=True)
    session_name: str | None = Field(default=None)
    user_id: int = Field(foreign_key="genzenuser.id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class ChatHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    user_id: int = Field(foreign_key="genzenuser.id")
    role: str = Field(index=True) # user or assistant
    message: str
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))