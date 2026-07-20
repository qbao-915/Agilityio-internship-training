import os
import datetime
from typing import Optional
import jwt
import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load environment variables from .env file
load_dotenv()

# Configuration constants
JWT_SECRET = os.environ.get("JWT_SECRET", "supersecretkey_change_me_in_production_1234567890")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed bcrypt password.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(username: str) -> str:
    """
    Create a JWT access token for a username with an expiration time.
    """
    payload = {
        "sub": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT access token. Returns the username if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    FastAPI dependency to extract and verify the bearer token from the Authorization header.
    Raises HTTP 401 Unauthorized for missing, invalid, or expired tokens.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Bearer token required."
        )
    
    token = credentials.credentials
    username = verify_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )
    
    return username
