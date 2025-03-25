import psycopg2
from src.connections.db import pool
from src.utils.config_setting import Settings

settings = Settings()

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
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
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
    try:
        delete_database()
    finally:
        # Close the connection pool
        pool.close()