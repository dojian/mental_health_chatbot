import datetime
from pydantic import EmailStr
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from sqlalchemy import String, Column, Index
from sqlalchemy.dialects.postgresql import JSONB


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
    user_id: int = Field(foreign_key="genzenuser.id", index=True)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_interaction: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    session_metadata: dict = Field(sa_column=Column(JSONB), default={})

class ChatHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    user_id: int = Field(foreign_key="genzenuser.id", index=True)
    role: str = Field(index=True) # user or assistant
    message: str
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    chat_metadata: dict = Field(sa_column=Column(JSONB), default={})  # For storing memory context, emotional state, etc.

    __table_args__ = (
        Index('idx_chat_history_user_session', 'user_id', 'session_id'),  # Composite index for faster lookups
    )

class MemoryFact(SQLModel, table=True):
    """Stores personal facts and important information about users for long-term memory."""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="genzenuser.id", index=True)
    fact_type: str = Field(index=True)  # personal_fact, conversation_memory, etc.
    content: str
    fact_metadata: dict = Field(sa_column=Column(JSONB))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_accessed: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index('idx_memory_facts_user_type', 'user_id', 'fact_type'),  # Composite index for memory lookups
    )

class SurveyData(SQLModel, table=True):
    __tablename__ = "survey"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="genzenuser.id", index=True)
    session_id: str = Field(foreign_key="chatsession.session_id")
    survey_type: str = Field(max_length=20) # pre or post
    survey_data: dict = Field(sa_column=Column(JSONB))
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        Index('idx_survey_user_session', 'user_id', 'session_id'),  # Composite index for survey lookups
    )
