# from typing import Annotated

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone, UTC
import datetime
from pydantic import EmailStr
from sqlalchemy import String
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column


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

class SurveyData(SQLModel, table=True):
    __tablename__ = "survey"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="genzenuser.id")
    session_id: str = Field(foreign_key="chatsession.session_id")
    survey_type: str = Field(max_length=20) # pre or post
    data: dict = Field(sa_column=Column(JSONB))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
