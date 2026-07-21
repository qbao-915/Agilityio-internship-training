# Security Guidelines & Reference (FastAPI Security Demo)

This document outlines the security architecture, tech stack, directory structure, setup instructions, and the comprehensive API reference for the Day 13 Security Test application.

---

## 🛠️ Tech Stack Details

The application is built using a modern, lightweight Python stack with security best practices:
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (high performance, asynchronous web framework based on ASGI, using Pydantic for schema verification and data parsing)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/) (used to serve the FastAPI application locally)
- **Database Engine:** [SQLite 3](https://sqlite.org/) (a self-contained, serverless SQL database engine accessed using Python's standard `sqlite3` driver)
- **Security & Cryptography:**
  - `bcrypt` (used for secure, adaptive salted hashing of passwords)
  - `PyJWT` (used for generating, signing, decoding, and verifying JSON Web Tokens (JWT) for secure authentication)
- **Configuration Management:** `python-dotenv` (loads configurations and secret keys from a local `.env` file into the application environment)
- **Testing Framework:**
  - `pytest` (used for unit testing cryptographic helpers and integration testing HTTP endpoints)
  - `HTTPX` (as FastAPI's `TestClient` uses HTTPX under the hood to send request payloads to test endpoints)

---

## 📂 Project Structure

Below is the directory layout of the `exercises/Day-13-Security-Test` workspace, detailing the responsibility of each file:

```text
exercises/Day-13-Security-Test/
├── routers/
│   ├── auth_router.py       # API endpoints for Login (`/login`) & Protected Data (`/protected-data`)
│   └── tasks_router.py      # API endpoints for Tasks CRUD (`/tasks`) with parameter validation
├── tests/
│   ├── __init__.py          # Marks the tests directory as a Python package
│   ├── conftest.py          # Pytest configuration, fixtures (client, clean DB setup/teardown)
│   ├── test_api_endpoints.py# Integration tests verifying HTTP status codes and responses
│   └── test_unit_auth.py    # Unit tests for password hashing & JWT generation/verification
├── .env                     # Local environment variables containing private keys (ignored by Git)
├── .env.example             # Template file showing environment configuration without secrets
├── auth.py                  # Cryptographic helper functions (bcrypt, JWT) and FastAPI dependency injectables
├── db-setup.sql             # SQL script definitions for seeding schemas (users and tasks table)
├── main.py                  # Main application entry point, lifecycle context manager, and error handlers
├── pytest.ini               # Pytest command-line options and deprecation warning filters
├── SECURITY.md              # Project documentation covering security rules, setup instructions, and API endpoints
└── tasks.db                 # Local SQLite database file (dynamically created on runtime)
```

---

## ⚙️ Setup and Installation Instructions

Follow these step-by-step instructions to set up, run, and test the Day 13 application from a fresh clone.

### Prerequisites
- Python 3.10 or higher installed.

### 1. Navigate to the Exercise Directory
```bash
cd exercises/Day-13-Security-Test
```

### 2. Create and Activate a Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
Install all required libraries using `pip`:
```bash
pip install fastapi uvicorn PyJWT bcrypt python-dotenv pytest httpx
```

### 4. Configure Environment Variables
Copy the `.env.example` file to `.env`:
- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```
*Note: Open `.env` and verify the values. You can change `JWT_SECRET` to a custom secret string.*

### 5. Running the Application
Launch the Uvicorn local development server:
```bash
uvicorn main:app --reload
```
By default, the server will run on `http://127.0.0.1:8000`. You can access the interactive API documentation at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 6. Database Seeding
The database (`tasks.db`) is automatically initialized and seeded with mock data using the SQL schema from `db-setup.sql` on the first application startup (using FastAPI's lifespan system). If you wish to reset or manually recreate the database, simply delete `tasks.db` and restart the application.

### 7. Running the Tests
Execute the pytest suite to verify all core security behaviors and endpoint controls are functioning correctly:
```bash
pytest
```
Pytest will run 13 tests checking JWT creation, JWT expiration, password hashing, and API authentication/validation errors.

---

## 🔒 Security Policy & Checklist Status

- [x] **Passwords must be hashed:** Never store passwords in plain text. Verified to be using `bcrypt`.
- [x] **Input must be validated:** All client requests are strictly parsed and validated using Pydantic models.
- [x] **SQL queries must use placeholders:** Protect against SQL Injection by utilizing SQLite parameter placeholder substitution (`?`) rather than string concatenation/formatting.
- [x] **Secrets Management:** Cryptographic keys, token expirations, and environment variables are loaded dynamically from `.env` and excluded from source control.
- [x] **Secure Exception Handling:** Global handlers capture errors (like `RequestValidationError`) to format clean responses without leaking system stack traces or internal schemas to clients.

---

## 📑 API Endpoint Table

| HTTP Method | Endpoint | Description | Auth Required? | Request / Parameters Schema | Success Response (Status & Example) | Error Responses |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Root welcoming page. | No | None | **200 OK**<br>`{"message": "Welcome to the Day 13..."}` | None |
| **POST** | `/login` | Authenticate username/password and issue JWT token. | No | **Body (JSON)**:<br>- `username`: string (min 1)<br>- `password`: string (min 1) | **200 OK**<br>`{"access_token": "...", "token_type": "bearer"}` | - **401 Unauthorized** (invalid credentials)<br>- **422 Unprocessable Content** (invalid schema)<br>- **500 Internal Server Error** (DB query error) |
| **GET** | `/protected-data` | Retrieve confidential metadata reserved for authorized users. | Yes (Bearer Token) | **Header**:<br>- `Authorization: Bearer <JWT>` | **200 OK**<br>`{"message": "Access granted...", "user": "admin", "sensitive_info": {...}}` | - **401 Unauthorized** (missing, invalid, or expired token) |
| **GET** | `/tasks` | List all tasks from the SQLite database. | No | None | **200 OK**<br>`[{"id": 1, "title": "Review Security...", "status": "In Progress"}]` | - **500 Internal Server Error** (DB lookup error) |
| **POST** | `/tasks` | Create a new task item with validation rules. | No | **Body (JSON)**:<br>- `title`: string (1-100, trimmed, non-empty)<br>- `status`: string (optional, default: "Pending", must be 'Pending', 'In Progress', or 'Completed') | **201 Created**<br>`{"id": 4, "title": "Clean code...", "status": "Pending"}` | - **422 Unprocessable Content** (empty title, invalid status value)<br>- **500 Internal Server Error** (DB insert error) |
| **GET** | `/tasks/{task_id}` | Retrieve details of a specific task item. | No | **Path Parameter**:<br>- `task_id`: integer (>= 1) | **200 OK**<br>`{"id": 1, "title": "Review Security...", "status": "In Progress"}` | - **404 Not Found** (task ID does not exist)<br>- **422 Unprocessable Content** (ID < 1 or invalid format)<br>- **500 Internal Server Error** (DB select error) |
| **DELETE** | `/tasks/{task_id}` | Delete a specific task from the database. | No | **Path Parameter**:<br>- `task_id`: integer (>= 1) | **200 OK**<br>`{"message": "Task with ID 1 was successfully deleted."}` | - **404 Not Found** (task ID does not exist)<br>- **422 Unprocessable Content** (ID < 1 or invalid format)<br>- **500 Internal Server Error** (DB delete error) |

