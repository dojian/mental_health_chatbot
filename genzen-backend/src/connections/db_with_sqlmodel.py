from sqlmodel import SQLModel, Field

from src.connections.db import get_connection, get_session, create_db_and_tables

class UserBase(SQLModel):
    username: str = Field(index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: str = Field(default="user", nullable=False)

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)

class UserCreate(UserBase):
    pass

create_db_and_tables()