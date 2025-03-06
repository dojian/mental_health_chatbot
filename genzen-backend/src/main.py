from fastapi import FastAPI
# from collections.abc import AsyncIterator
# import os
# import logging
# from datetime import datetime
# from dotenv import load_dotenv
# from contextlib import asynccontextmanager

### Postgres ###
import uuid
# from src.connections.db import get_connection

### LLM Client ###
# from src.connections.llm_client import get_llm_client

# ### Redis ###
# from src.connections.redis_cache import init_redis

from src.connections.lifespan import lifespan

### Load environment variables from .env file ###
# load_dotenv()


# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncIterator[None]:

#     ### Logging ###
#     logging.basicConfig(filename="genzen-backend-log.log", encoding="utf-8", level=logging.DEBUG)
    
#     ### Redis ###
#     await init_redis(app)
#     logging.info(f"{datetime.now()}: LIFESPAN - Connected to Redis")

#     ### OpenAI ###
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     model = get_llm_client()
#     logging.info(f"{datetime.now()}: LIFESPAN - Connected to OpenAI - gpt-4o-mini")
    
#     ### Postgres ###
#     conn = get_connection()
#     logging.info(f"{datetime.now()}: LIFESPAN - Connected to Postgres")
#     yield


app = FastAPI(lifespan=lifespan)


### API Endpoints ###
@app.get("/")
async def get_root():
    '''
    Returns a welcome message.
    '''
    return {"message": "Welcome to the GenZen Root Backend!"}

@app.get("/health")
async def get_health():
    '''
    Returns a status check indicating if the service is healthy.
    '''
    return {"status": "healthy"}

@app.get("/hello")
async def get_hello(name: str):
    '''
    Takes a parameter of name and returns a json object with the parameter.
    '''
    return {"message": f"Hello {name}"}

@app.post("/login")
async def login(username: str, password: str):
    '''
    Takes a username and password and returns a json object with the username.
    '''
    return {"username": username, "message": "You have been logged in."}

@app.post("/logout")
async def logout(username: str):
    '''
    Takes a username and returns a json object with the username.
    '''
    return {"username": username, "message": "You have been logged out."}