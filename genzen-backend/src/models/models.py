# from typing import Annotated

from sqlmodel import Field, SQLModel
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy import String

class User(SQLModel, table=True):
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

class Session(SQLModel, table=True):
    session_id: str = Field(default=None, primary_key=True)
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())