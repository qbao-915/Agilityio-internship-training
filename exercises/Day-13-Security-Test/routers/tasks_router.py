import os
import sqlite3
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field, field_validator

# Logging & Router setup
logger = logging.getLogger("Day13App.TasksRouter")
router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Database Path & Connection Helpers
# Resolves to: exercises/Day-13/tasks.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks.db"))

def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.
    Enables dictionary-like row access and enforces foreign key constraints.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Pydantic Schemas (Input Validation & Output Formatting)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the task")
    status: Optional[str] = Field("Pending", description="Status of the task. Allowed: 'Pending', 'In Progress', 'Completed'")

    @field_validator("title")
    @classmethod
    def validate_title(cls, val: str) -> str:
        """
        Validate that the title is not empty, does not consist solely of whitespace,
        and sanitizes any leading or trailing whitespace.
        """
        cleaned = val.strip()
        if not cleaned:
            raise ValueError("Task title cannot be empty or contain only whitespace.")
        return cleaned

    @field_validator("status")
    @classmethod
    def validate_status(cls, val: Optional[str]) -> Optional[str]:
        """
        Validates task status to enforce a rigid set of values (case-insensitive conversion).
        Allowed states: 'Pending', 'In Progress', 'Completed'.
        """
        if val is None:
            return "Pending"
            
        cleaned = val.strip().title()
        allowed_states = {"Pending", "In Progress", "Completed"}
        
        if cleaned not in allowed_states:
            raise ValueError(f"Task status must be one of: {', '.join(allowed_states)}")
        return cleaned

class TaskResponse(BaseModel):
    id: int
    title: str
    status: str

# API Endpoints
@router.get("", response_model=list[TaskResponse], summary="Retrieve all tasks")
def get_tasks():
    """
    Retrieve all task records from the database using a Raw SQL query.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, status FROM tasks ORDER BY id ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_err:
        logger.error(f"Database error in get_tasks: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching tasks from the database."
        )
    finally:
        if conn:
            conn.close()

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    """
    Create a new task with validated title and status.
    Uses Raw SQL for insertion and selects the newly created record.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO tasks (title, status) VALUES (?, ?);",
            (payload.title, payload.status)
        )
        conn.commit()
        new_id = cursor.lastrowid
        
        # Fetch and return the newly inserted task record
        cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?;", (new_id,))
        task_row = cursor.fetchone()
        return dict(task_row)
    except sqlite3.Error as db_err:
        if conn:
            conn.rollback()
        logger.error(f"Database error in create_task: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while inserting the task into the database."
        )
    finally:
        if conn:
            conn.close()

@router.get("/{task_id}", response_model=TaskResponse, summary="Retrieve a specific task by ID")
def get_task(
    task_id: int = Path(..., ge=1, description="The ID of the task to retrieve (must be >= 1)")
):
    """
    Retrieve a specific task by ID using `cursor.fetchone()`.
    Raises HTTP 404 Not Found if no corresponding record is found in the database.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?;", (task_id,))
        row = cursor.fetchone()
        
        # If row is None, raise a clean HTTP 404 Exception
        if row is None:
            logger.info(f"Task retrieve failed: ID {task_id} not found in database.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} does not exist in the system."
            )
            
        return dict(row)
    except HTTPException:
        # Re-raise standard HTTP exceptions
        raise
    except sqlite3.Error as db_err:
        logger.error(f"Database error in get_task: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the task."
        )
    finally:
        if conn:
            conn.close()

@router.delete("/{task_id}", summary="Delete a specific task by ID")
def delete_task(
    task_id: int = Path(..., ge=1, description="The ID of the task to delete (must be >= 1)")
):
    """
    Delete a task from the system.
    Strictly performs a SELECT lookup first to verify existence before deletion.
    Raises HTTP 404 Not Found if record is missing.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Perform existence check using SELECT query
        cursor.execute("SELECT id FROM tasks WHERE id = ?;", (task_id,))
        row = cursor.fetchone()
        
        if row is None:
            logger.info(f"Task deletion aborted: ID {task_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found. Cannot perform delete operation."
            )
            
        # 2. Task exists, execute the Raw SQL DELETE query
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        conn.commit()
        logger.info(f"Task ID {task_id} deleted successfully.")
        
        return {"message": f"Task with ID {task_id} was successfully deleted."}
    except HTTPException:
        # Re-raise standard HTTP exceptions
        raise
    except sqlite3.Error as db_err:
        if conn:
            conn.rollback()
        logger.error(f"Database error in delete_task: {db_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the task from the database."
        )
    finally:
        if conn:
            conn.close()
