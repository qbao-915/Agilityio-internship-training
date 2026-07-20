import os
import sqlite3
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from auth import verify_password, create_access_token, get_current_user

# Logger and Router setup
logger = logging.getLogger("Day13App.AuthRouter")
router = APIRouter(tags=["Authentication"])

# Database path resolution
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks.db"))

def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Enforces foreign key constraints and enables dictionary-like row access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Pydantic Schemas for Login
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="Username of the user")
    password: str = Field(..., min_length=1, description="Plain text password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Endpoints
@router.post("/login", response_model=TokenResponse, summary="User login and JWT acquisition")
def login(payload: UserLogin):
    """
    Authenticate a user by checking credentials against the SQLite database using raw SQL.
    Uses parameterized query to prevent SQL Injection and bcrypt for password verification.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Parameterized Query to prevent SQL Injection
        cursor.execute("SELECT username, hashed_password FROM users WHERE username = ?;", (payload.username,))
        user_row = cursor.fetchone()
        
        # 2. Verify username exists and password matches hashed password
        if not user_row or not verify_password(payload.password, user_row["hashed_password"]):
            logger.warning(f"Login failed authentication attempt for username: {payload.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # 3. Generate JWT access token
        token = create_access_token(payload.username)
        logger.info(f"User '{payload.username}' authenticated successfully.")
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except sqlite3.Error as db_err:
        logger.error(f"Database query error during login: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred while processing login."
        )
    finally:
        if conn:
            conn.close()

@router.get("/protected-data", summary="Access a protected resource")
def get_protected_data(current_user: str = Depends(get_current_user)):
    """
    Secure endpoint requiring a valid JWT access token.
    Uses FastAPI Depends with get_current_user dependency.
    """
    logger.info(f"Protected endpoint accessed by user: '{current_user}'")
    return {
        "message": "Access granted. This is highly confidential data.",
        "user": current_user,
        "sensitive_info": {
            "environment": "Sandbox",
            "server_time_utc": os.environ.get("TZ", "UTC"),
            "authorized_capabilities": [
                "read:data",
                "write:tasks"
            ]
        }
    }
