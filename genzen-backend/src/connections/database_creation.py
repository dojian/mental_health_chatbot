import os
import psycopg2
from dotenv import load_dotenv
from sqlmodel import SQLModel
from src.connections.db import engine
load_dotenv()

def delete_database():
    """
    Reset the database.
    """
    commands_drop = [
        "DROP TABLE IF EXISTS chathistory CASCADE",
        "DROP TABLE IF EXISTS chatsession CASCADE",
        "DROP TABLE IF EXISTS checkpoint_blobs CASCADE",
        "DROP TABLE IF EXISTS checkpoint_migrations CASCADE",
        "DROP TABLE IF EXISTS checkpoint_writes CASCADE",
        "DROP TABLE IF EXISTS checkpoints CASCADE",
        "DROP TABLE IF EXISTS genzenuser CASCADE",
        "DROP TABLE IF EXISTS store CASCADE",
        "DROP TABLE IF EXISTS store_migrations CASCADE",
        "DROP TABLE IF EXISTS survey CASCADE",
    ]

    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

    try:
        cur = conn.cursor()
        for command in commands_drop:
            cur.execute(command)
        conn.commit()
        print("Database reset successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_database()