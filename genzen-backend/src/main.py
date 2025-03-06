from fastapi import FastAPI
# import uuid
from src.connections.lifespan import lifespan

from src.routers import base, auth

app = FastAPI(lifespan=lifespan)

### API Routes ###
app.include_router(base.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])