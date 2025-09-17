from src.models.models import GenZenUser
from datetime import timedelta, datetime, UTC
from sqlalchemy.orm import Session
import jwt
import time
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from src.connections.db import get_session
from src.connections.redis_cache import get_redis_client

from src.utils.config_setting import Settings

settings = Settings()

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
REDIS_SESSION_PREFIX = settings.REDIS_SESSION_PREFIX

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


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

def get_user(username: str, session) -> GenZenUser | None:
    """
    Get a user by username.
    """
    return session.query(GenZenUser).filter(GenZenUser.username == username).first()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create an access token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

async def token_bucket_limiter(redis, user_id: str, capacity: int = 10, refill_rate: float = 5.0):
    """
    Token bucket rate limiter using Redis.
    """
    key = f"rate_limit:{user_id}"
    now = time.time()
    data = await redis.hgetall(key)
    if not data:
        tokens = capacity
        last_refill = now
    else:
        tokens = float(data.get(b'tokens', capacity))
        last_refill = float(data.get(b'last_refill', now))
    elapsed = now - last_refill
    tokens = min(capacity, tokens + elapsed * refill_rate)
    if tokens < 1:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    tokens -= 1
    await redis.hset(key, mapping={'tokens': str(tokens), 'last_refill': str(now)})
    await redis.expire(key, 3600)  # Expire after 1 hour

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis = Depends(get_redis_client),
    session: Session = Depends(get_session)
) -> GenZenUser:
    """
    Retrieve the current authenticated user based on the JWT token.
    """
    # Exception to raise for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        session_id: str = payload.get("session_id")

        if username is None or session_id is None:
            raise credentials_exception
        
        # Check if session exists in Redis
        stored_username = await redis.get(f"user_session:{session_id}")
        if not stored_username or stored_username.decode() != username:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username=username, session=session)
    if user is None:
        raise credentials_exception
    await token_bucket_limiter(redis, user.username)
    return user
