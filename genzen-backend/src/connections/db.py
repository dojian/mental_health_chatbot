import psycopg
import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_postgres import PostgresChatMessageHistory
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Get a connection to the Postgres database.
    """
    connection = psycopg.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    return connection

table_name = "chat_history"
def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    sync_connection = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    return PostgresChatMessageHistory(
        table_name, session_id, sync_connection
    )