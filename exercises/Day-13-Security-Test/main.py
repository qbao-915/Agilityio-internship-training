import sys
import os
import sqlite3
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Ensure the current directory is in sys.path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import routers
from routers.tasks_router import router as tasks_router
from routers.auth_router import router as auth_router

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Day13App")

# Database Constants
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "tasks.db")
SQL_SETUP_PATH = os.path.join(DB_DIR, "db-setup.sql")

def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Enforces foreign key constraints and enables dictionary-like row access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that initializes the SQLite database on startup.
    Reads db-setup.sql and seeds the SQLite database if it does not exist or is empty.
    """
    conn = None
    try:
        db_exists = os.path.exists(DB_PATH)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If database is new or empty, initialize schema and seed mock data
        if not db_exists or os.path.getsize(DB_PATH) == 0:
            logger.info("Initializing database schema...")
            if os.path.exists(SQL_SETUP_PATH):
                with open(SQL_SETUP_PATH, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                cursor.executescript(sql_script)
                conn.commit()
                logger.info("Database schema initialized and seeded successfully.")
            else:
                logger.warning(f"SQL setup file not found at {SQL_SETUP_PATH}. Skipping seeding.")
        else:
            logger.info("Database already exists. Skipping schema initialization.")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
    finally:
        if conn:
            conn.close()
    
    yield
    logger.info("Shutting down application...")

# FastAPI Application Declaration
app = FastAPI(
    title="Day 13: Simple Login & Protected Endpoint",
    description="FastAPI exercise demonstrating bcrypt password hashing and JWT protected endpoints using raw SQL.",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(tasks_router)
app.include_router(auth_router)

# Custom Exception Handlers (Same as Day 10 for robust error formatting)
def serialize_validation_errors(errors: list) -> list:
    """
    Safely serialize Pydantic validation errors by converting any embedded
    Exception objects to strings.
    """
    cleaned = []
    for err in errors:
        err_copy = dict(err)
        if "ctx" in err_copy and isinstance(err_copy["ctx"], dict):
            safe_ctx = {}
            for k, v in err_copy["ctx"].items():
                if isinstance(v, Exception):
                    safe_ctx[k] = str(v)
                else:
                    try:
                        jsonable_encoder(v)
                        safe_ctx[k] = v
                    except Exception:
                        safe_ctx[k] = str(v)
            err_copy["ctx"] = safe_ctx
        cleaned.append(err_copy)
    return jsonable_encoder(cleaned)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global exception handler for validation errors (RequestValidationError).
    Logs error details alongside the invalid input body or query parameters
    and returns a structured JSON payload for client debugging.
    """
    raw_errors = exc.errors()
    error_details = serialize_validation_errors(raw_errors)
    
    # Safeguard body extraction
    body_payload = None
    try:
        if hasattr(exc, "body") and exc.body is not None:
            body_payload = jsonable_encoder(exc.body)
    except Exception as parse_err:
        logger.warning(f"Failed to encode request body for validation logging: {parse_err}")
        body_payload = str(exc.body)

    logger.error(
        f"Validation failed on URL: {request.url.path} | HTTP Method: {request.method}\n"
        f"Errors: {error_details}\n"
        f"Invalid Request Payload: {body_payload}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": error_details,
            "body": body_payload
        }
    )

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint serving a simple welcome message.
    """
    return {"message": "Welcome to the Day 13 Auth & Tasks API. Go to /docs to view interactive documentation."}
