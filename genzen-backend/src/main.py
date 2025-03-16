from fastapi import FastAPI
from src.connections.lifespan import lifespan

from src.routers import base, auth, chat

app = FastAPI(title="GenZen Backend", 
              description="A Simple AI Agent API application for mental health", 
              lifespan=lifespan)

### API Routes ###
app.include_router(base.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
