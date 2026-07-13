# 📝 Day 10: Input Validation & Error Handling (FastAPI & SQLite)

## 📋 Overview
This exercise showcases the implementation of strict data validation and thorough error handling using **FastAPI**, **Pydantic (v2)**, and Python's built-in **`sqlite3`** module. It emphasizes the "Never trust user input" security concept.

---

## 📂 Codebase Structure

```text
Day-10-Input-Validation-Error-Handling/
├── db-setup.sql
├── main.py
├── README.md
└── routers/
    └── tasks.py
```

- **`main.py`**: Manages application lifecycle hooks, starts the SQLite initialization, and handles global validation errors.
- **`routers/tasks.py`**: Contains task schemas (Pydantic models), database access helpers, and API route handlers.
- **`db-setup.sql`**: Raw SQL initialization script that outlines the `tasks` schema and seeds mock rows.

---

## 🗄️ Database Schema & Connection
The database consists of a single `tasks` table with the following layout:
- **`id`** (`INTEGER PRIMARY KEY AUTOINCREMENT`): Task's primary key.
- **`title`** (`TEXT NOT NULL`): Title of the task, validated to prevent empty or whitespace-only inputs.
- **`status`** (`TEXT DEFAULT 'Pending'`): Status of the task (allowed states: `'Pending'`, `'In Progress'`, `'Completed'`).

Raw SQL is executed using a database helper function `get_db_connection()` which sets `conn.row_factory = sqlite3.Row` and enforces foreign keys (`PRAGMA foreign_keys = ON;`).

---

## 🛡️ Key Features Implemented

### 1. Global Custom Exception Handler (`RequestValidationError`)
- Captures FastAPI's native validation exception.
- Standardizes errors with a descriptive log output on the server console containing the error details and the request payload.
- Safely encodes raw request bodies (including cases where the body is not standard JSON) to prevent JSON serialization errors.
- Returns a custom 422 JSON response containing the details and the reflected body for front-end debug assistance.

### 2. Strict Input Validation (Pydantic & Field Validators)
- **Whitespace Stripping & Empty Checks**: Using Pydantic `@field_validator("title")`, any surrounding spaces are stripped, and blank inputs (e.g. `"   "`) are rejected with a validation error.
- **Case-Insensitive Status Normalization**: Using `@field_validator("status")`, inputs are title-cased (`pending` -> `Pending`) and validated against allowed states (`Pending`, `In Progress`, `Completed`).
- **Path Parameter Constraints**: Path parameter `task_id` is restricted to positive integers starting from `1` using FastAPI's `Path(..., ge=1)`.

### 3. Safe DB Operations & Resource Management
- All DB operations utilize `try...except sqlite3.Error...finally` blocks.
- On error, `conn.rollback()` is invoked if applicable.
- Database connections are strictly closed inside the `finally` block to prevent resource leaks.

### 4. Custom Handlers for Fetching & Deleting Tasks
- **GET `/tasks/{task_id}`**: Retrieves a task using `cursor.fetchone()`. If no record is found, it raises a clean `404 Not Found` exception instead of returning `null` or empty dicts.
- **DELETE `/tasks/{task_id}`**: Checks if the record exists by executing a `SELECT` query first. If missing, it immediately throws `404 Not Found`. Otherwise, it performs the `DELETE` query and returns a success confirmation.

---

## 🚀 How to Run & Verify

1. **Start the Application**:
   Navigate to the directory and run Uvicorn:
   ```bash
   cd exercises/Day-10-Input-Validation-Error-Handling
   uvicorn main:app --reload
   ```

2. **Access Swagger Interactive Docs**:
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

3. **Verify Scenarios**:
   - **Scenario A (Invalid Body POST)**:
     Send a POST request to `/tasks` with an empty title `{"title": "   "}`. Observe the custom error structure returned containing `"body"` and `"detail"`.
   - **Scenario B (GET Valid Task & 404)**:
     Send `GET /tasks/1`. If seeded, it returns task details.
     Send `GET /tasks/999` (or a negative ID). Observe the clear `404 Not Found` or `422 Unprocessable Entity` response.
   - **Scenario C (DELETE Valid Task & 404)**:
     Send `DELETE /tasks/999`. Observe it throws `404 Not Found` because the SELECT check fails.
     Send `DELETE /tasks/2`. Observe a success response and verify deletion by querying GET `/tasks`.
