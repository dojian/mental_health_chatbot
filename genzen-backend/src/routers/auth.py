import jwt, uuid, os
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.models.schemas import Token, CreateGenZenUser
from src.models.models import GenZenUser
from src.connections.db import get_session
from src.connections.redis_cache import get_redis_client
from src.utils.auth_utils import verify_password, get_password_hash, get_user, create_access_token
# from dotenv import load_dotenv
# load_dotenv()

from src.utils.config_setting import Settings

settings = Settings()

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REDIS_SESSION_PREFIX = settings.REDIS_SESSION_PREFIX

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(user_create: CreateGenZenUser, redis = Depends(get_redis_client), session = Depends(get_session)):
    """
    Register a new user.
    """

    # Check if user exists
    if get_user(user_create.username, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # Validate role
    accepted_roles = {"user", "admin"}
    if user_create.role not in accepted_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    
    # Hash password and insert new user into database
    hashed_password = get_password_hash(user_create.password)
    new_user = GenZenUser(
        username=user_create.username, 
        hashed_password=hashed_password,
        email=user_create.email,
        role=user_create.role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create session in Redis and issue access token
    session_id = uuid.uuid4().hex
    session_key = f"{REDIS_SESSION_PREFIX}{session_id}"
    await redis.set(session_key, new_user.username, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    access_token = create_access_token(
        data={"sub": new_user.username, "session_id": session_id}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    redis = Depends(get_redis_client), 
    session = Depends(get_session)
    ):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user(form_data.username, session)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create session in Redis and issue access token
    session_id = uuid.uuid4().hex
    session_key = f"{REDIS_SESSION_PREFIX}{session_id}"
    await redis.set(session_key, user.username, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    access_token = create_access_token(
        data={"sub": user.username, "session_id": session_id}
    )
    return Token(access_token=access_token, token_type="bearer")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), redis = Depends(get_redis_client)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        session_id = payload.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    session_key = f"{REDIS_SESSION_PREFIX}{session_id}"
    await redis.delete(session_key)
    return {"message": "Successfully logged out"}