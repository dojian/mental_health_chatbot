import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def reset_database():
    """
    Reset the database.
    """
    commands_drop = [
        # "DROP TABLE IF EXISTS genzenuser CASCADE",
        "DROP TABLE IF EXISTS session CASCADE",
        "DROP TABLE IF EXISTS chathistory CASCADE",
        "DROP TABLE IF EXISTS chatsession CASCADE",

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