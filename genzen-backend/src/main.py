from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.connections.lifespan import lifespan

from src.routers import base, auth, chat, resources

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

### API Routes ###
app.include_router(base.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(resources.router, prefix="/resources", tags=["resources"])
