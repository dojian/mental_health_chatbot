import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def reset_database():
    """
    Reset the database.
    """
    commands = [
        "DROP TABLE IF EXISTS users CASCADE",
        (
            "CREATE TABLE users (\n"
            "    id SERIAL PRIMARY KEY,\n"
            "    username VARCHAR(255) UNIQUE NOT NULL,\n"
            "    hashed_password TEXT NOT NULL,\n"
            "    role VARCHAR(50) NOT NULL\n"
            ");"
        ),
        "DROP TABLE IF EXISTS sessions CASCADE",
        (
            "CREATE TABLE sessions (\n"
            "    session_id UUID PRIMARY KEY,\n"
            "    username VARCHAR(255) REFERENCES users(username) ON DELETE CASCADE,\n"
            "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
            ");"
        )
    ]
    commands_drop = [
        "DROP TABLE IF EXISTS users CASCADE",
        "DROP TABLE IF EXISTS sessions CASCADE",
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
    reset_database()