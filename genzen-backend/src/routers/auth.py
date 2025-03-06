from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
import jwt
import uuid
import os

from src.models.authentication import User, Token

from passlib.context import CryptContext
from src.connections.db import get_connection
from src.connections.redis_cache import get_redis_client

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
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

def get_user(username: str) -> User | None:
    """
    Get a user by username.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, hashed_password FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        return User(**row)
    else:
        return None

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), redis = Depends(get_redis_client)):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user(form_data.username)
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

# @router.post("/refresh")
# async def refresh_token(token: str = Depends(OAuth2PasswordBearer(auto_error=False))):
#     """
#     OAuth2 compatible token refresh, get a new access token.
#     """
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#         session_id = payload.get("session_id")
#         username = payload.get("sub")
#     except jwt.JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     if not session_id or not username:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     user = get_user(username)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     new_access_token = create_access_token(
#         data={"sub": user.username, "session_id": session_id},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
#     )
#     return {"access_token": new_access_token, "token_type": "bearer"}

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