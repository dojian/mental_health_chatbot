
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):

    # Debug
    DEBUG: bool = os.getenv("DEBUG")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")
    REDIS_SESSION_PREFIX: str = os.getenv("REDIS_SESSION_PREFIX")

    # Postgres
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    # AWS
    # AWS_PROFILE: str = os.getenv("AWS_PROFILE")
    AWS_REGION: str = os.getenv("AWS_REGION")
    MENTAL_HEALTH_ENDPOINT: str = os.getenv("MENTAL_HEALTH_ENDPOINT")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    S3_BUCKET_EMBEDDINGS_KEY: str = os.getenv("S3_BUCKET_EMBEDDINGS_KEY")
    S3_BUCKET_CHUNK_TEMP_PATH: str = os.getenv("S3_BUCKET_CHUNK_TEMP_PATH")

    # AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    # AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    RERANK_MODEL: str = os.getenv("RERANK_MODEL")

    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    
    #allow advice
    allow_advice: bool = True