import sqlite3
import os
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Absolute path to the SQLite database file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks.db"))

def get_db_connection():
    """Helper to establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables access to columns by name like a dict
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --- PYDANTIC SCHEMAS ---

TaskStatus = Literal["pending", "in_progress", "completed"]

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task, cannot be empty")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    status: TaskStatus = Field("pending", description="Status of the task")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="New title of the task")
    description: Optional[str] = Field(None, description="New description of the task")
    status: Optional[TaskStatus] = Field(None, description="New status of the task")

class TaskResponse(BaseModel):
    taskID: int
    title: str
    description: Optional[str]
    status: str
    created_at: str

# --- API ENDPOINTS ---

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    """
    Create a new task in the system.
    - **title**: Required, cannot be empty or whitespace only.
    - **description**: Optional.
    - **status**: Defaults to 'pending', accepts 'pending', 'in_progress', or 'completed'.
    """
    title_clean = payload.title.strip()
    if not title_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or whitespace only."
        )
        
    description_clean = payload.description.strip() if payload.description is not None else None

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?);",
            (title_clean, description_clean, payload.status)
        )
        conn.commit()
        new_id = cursor.lastrowid
        
        # Fetch the newly created task to return the complete object
        cursor.execute("SELECT * FROM tasks WHERE taskID = ?;", (new_id,))
        new_task = cursor.fetchone()
        return dict(new_task)
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error while creating task: {e}"
        )
    finally:
        conn.close()


@router.get("", response_model=List[TaskResponse], summary="Retrieve all tasks")
def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter tasks by status")
):
    """
    Retrieve all tasks from the system.
    Supports filtering by the optional query parameter `status`:
    - `pending`
    - `in_progress`
    - `completed`
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if status_filter:
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY taskID ASC;", (status_filter,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY taskID ASC;")
            
        tasks = cursor.fetchall()
        return [dict(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error while retrieving tasks: {e}"
        )
    finally:
        conn.close()


@router.get("/{task_id}", response_model=TaskResponse, summary="Retrieve a specific task by ID")
def get_task(task_id: int):
    """
    Retrieve details of a specific task by its unique ID.
    Returns 404 Not Found if the task does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM tasks WHERE taskID = ?;", (task_id,))
        task = cursor.fetchone()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found with ID: {task_id}"
            )
        return dict(task)
    finally:
        conn.close()


@router.put("/{task_id}", response_model=TaskResponse, summary="Update an existing task")
def update_task(task_id: int, payload: TaskUpdate):
    """
    Update information of an existing task.
    - Supports partial or full updates of properties (`title`, `description`, `status`).
    - Validates inputs before database execution.
    - Returns 404 Not Found if the task does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the task exists and fetch its current data
        cursor.execute("SELECT * FROM tasks WHERE taskID = ?;", (task_id,))
        current_task = cursor.fetchone()
        if not current_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found with ID: {task_id} to update."
            )
        
        current_data = dict(current_task)
        
        # Merge existing data with new update payload
        title_new = payload.title.strip() if payload.title is not None else current_data["title"]
        if not title_new:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New title cannot be empty or whitespace only."
            )
            
        description_new = payload.description.strip() if payload.description is not None else current_data["description"]
        status_new = payload.status if payload.status is not None else current_data["status"]
        
        # Execute the update query
        cursor.execute(
            """
            UPDATE tasks 
            SET title = ?, description = ?, status = ? 
            WHERE taskID = ?;
            """,
            (title_new, description_new, status_new, task_id)
        )
        conn.commit()
        
        # Return the updated object
        cursor.execute("SELECT * FROM tasks WHERE taskID = ?;", (task_id,))
        updated_task = cursor.fetchone()
        return dict(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error while updating task: {e}"
        )
    finally:
        conn.close()


@router.delete("/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    """
    Delete a specific task by its unique ID from the system.
    Returns success message or 404 Not Found if the task does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE taskID = ?;", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found with ID: {task_id} to delete."
            )
        conn.commit()
        return {"message": f"Task deleted successfully with ID {task_id}.", "taskID": task_id}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error while deleting task: {e}"
        )
    finally:
        conn.close()
