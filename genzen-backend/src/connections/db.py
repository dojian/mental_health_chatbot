# import psycopg
import os
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_postgres import PostgresChatMessageHistory
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool

# from langchain_openai import OpenAIEmbeddings

load_dotenv()

from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Session, create_engine

class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

settings = Settings()

SQLALCHEMY_DB_URI = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}?sslmode=disable"
POSTGRES_CONN_STRING = SQLALCHEMY_DB_URI

print("--------------------------------")
print(SQLALCHEMY_DB_URI)
print("--------------------------------")

engine = create_engine(
    SQLALCHEMY_DB_URI,
    echo=True
)

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0
}

pool = ConnectionPool(
    conninfo=POSTGRES_CONN_STRING,
    max_size=20,
    kwargs=connection_kwargs
)
checkpointer = PostgresSaver(pool)
memory_store = PostgresStore(pool)

# checkpointer = PostgresSaver.from_conn_string(POSTGRES_CONN_STRING)

# Initialize memory store for long-term memory (across sessions)
# memory_store = PostgresStore.from_conn_string(POSTGRES_CONN_STRING)

def get_connection():
    """
    Get a connection to the Postgres database.
    """
    return engine

def get_session():
    """
    Get a session for the Postgres database.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    

# Setup checkpoint and memory store
def setup_checkpoint_and_memory_store():
    """
    Initialize the Postgres db for checkpointer and store.
    """
    checkpointer.setup()
    memory_store.setup()
