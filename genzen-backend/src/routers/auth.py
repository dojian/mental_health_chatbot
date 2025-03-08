from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
import jwt
import uuid
import os

from src.models.schemas import Token, CreateUser
from src.models.models import User

from passlib.context import CryptContext
from src.connections.db import get_session
from src.connections.redis_cache import get_redis_client

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Get a hashed password.
    """
    return pwd_context.hash(password)

def get_user(username: str, session) -> User | None:
    """
    Get a user by username.
    """
    user = session.query(User).filter(User.username == username).first()
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=Token)
async def register_user(user_create: CreateUser, redis = Depends(get_redis_client), session = Depends(get_session)):
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
    new_user = User(username=user_create.username, hashed_password=hashed_password, role=user_create.role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create session in Redis and issue access token
    session_id = uuid.uuid4().hex
    await redis.set(f"session:{session_id}", new_user.username, ex=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username, "session_id": session_id}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), redis = Depends(get_redis_client), session = Depends(get_session)):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user(form_data.username, session)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    session_id = uuid.uuid4().hex
    await redis.set(f"session:{session_id}", user.username, ex=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    await redis.delete(f"session:{session_id}")
    return {"message": "Successfully logged out"}