# Security Checklist for FastAPI Demo

This document outlines key security considerations and rules implemented in this demo application. Use this checklist during code reviews to ensure secure design and coding practices.

## Security Checklist Status
- [x] **Passwords must be hashed** (never stored in plain text).
- [x] **Input must be validated** (using Pydantic).
- [x] **SQL queries must use placeholders** (against SQL Injection).
- [x] **Secret keys must be loaded from environment variables** and kept out of the source code.
- [x] **Ensure correct HTTP error codes** (401, 403, 404, 422) without leaking system stack traces.

## 📂 Project Directory Structure

```text
exercises/Day-13/
├── routers/
│   ├── auth_router.py       # API endpoints for Login & Protected Data
│   └── tasks.py             # API endpoints for Tasks CRUD (Day 10)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and test DB initialization
│   ├── test_api_endpoints.py# Integration API tests
│   └── test_unit_auth.py    # Unit tests for security helper logic
├── .env                     # Local environment secret variables
├── .gitignore               # Excludes python/pytest cache, DB, and environment secrets
├── auth.py                  # Cryptographic/JWT core helper functions & dependencies
├── db-setup.sql             # SQL script for schema setup & admin/tasks seeding
├── main.py                  # App entry point, lifecycle seeding, validation formatting
├── pytest.ini               # Pytest warnings suppression configuration
└── SECURITY.md              # Security policies & Checklist documentation
```

## 1. Password Protection & Storage
- **Requirement:** Passwords must be hashed using a strong cryptographic hash algorithm. Under no circumstances should plain text passwords be stored or logged.
- **Implementation in Demo:** 
  - User passwords are encrypted with `bcrypt` (adaptive salting/hashing scheme).
  - Seed database user password is pre-hashed (`$2b$12$...`).
  - Verification is done using `bcrypt.checkpw()` on the encoded UTF-8 strings.

## 2. Input Validation
- **Requirement:** All inputs from the client (body payload, query variables, headers) must be validated.
- **Implementation in Demo:** 
  - Inputs are structured into Pydantic models (e.g., `TaskCreate`, `UserLogin`).
  - Implemented field validators (e.g., `@field_validator("title")` to strip inputs and raise semantic errors if only whitespace or empty values are provided).
  - FastAPI automatically parses and runs Pydantic validations, rejecting requests that do not conform.

## 3. SQL Injection Prevention
- **Requirement:** Raw SQL queries must use placeholders. String concatenation/formatting (`+` or `f-strings`) inside SQL query parameters is forbidden.
- **Implementation in Demo:** 
  - Standardized parameter placeholders (`?` in SQLite) are used for all queries involving variables.
  - Examples: 
    - User lookup: `SELECT username, hashed_password FROM users WHERE username = ?;`
    - Task lookup: `SELECT id FROM tasks WHERE id = ?;`
    - Task insertion: `INSERT INTO tasks (title, status) VALUES (?, ?);`

## 4. Secrets Management
- **Requirement:** Cryptographic keys, secrets, API tokens, and credentials must be loaded dynamically from environment variables and must never be hardcoded in the codebase.
- **Implementation in Demo:** 
  - Configurations are loaded from an environment file (`.env`) via `python-dotenv`.
  - Secret key `JWT_SECRET` is read via `os.environ.get("JWT_SECRET")`.
  - The `.env` file is excluded from Git (included in `.gitignore` if git is configured).

## 5. Error Handling & API Leaks
- **Requirement:** Handle errors gracefully to provide correct HTTP status codes to clients, without revealing server system internals, file structures, or database stack traces.
- **Implementation in Demo:** 
  - Handled custom `RequestValidationError` globally, capturing error details and logging the input body securely.
  - Return standardized JSON payloads on client error (HTTP 422 for validation, HTTP 401 for unauthorized credentials, HTTP 404 for missing resources).
  - Internal database errors (e.g., `sqlite3.Error`) are logged to the console, and a generic user-friendly HTTP 500 error is returned to the user without disclosing database schema details.
