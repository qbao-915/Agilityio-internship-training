import os
import sys
import sqlite3
import warnings
import pytest

# Suppress deprecation warnings from external packages
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi.testclient import TestClient

# Ensure the parent directory (Day-13) is in sys.path
DAY13_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if DAY13_DIR not in sys.path:
    sys.path.append(DAY13_DIR)

from main import app, get_db_connection, DB_PATH, SQL_SETUP_PATH

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Session-scoped fixture to delete any previous tasks.db database
    and run db-setup.sql to ensure a fresh, seeded database for testing.
    """
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Warning: Could not remove old database: {e}")
            
    # Connect and run setup script
    conn = get_db_connection()
    try:
        if os.path.exists(SQL_SETUP_PATH):
            with open(SQL_SETUP_PATH, "r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            conn.commit()
        else:
            raise FileNotFoundError(f"SQL Setup script not found at {SQL_SETUP_PATH}")
    finally:
        conn.close()
    
    yield

@pytest.fixture(scope="function")
def db_conn():
    """
    Function-scoped database connection helper for checking DB entries directly.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

@pytest.fixture(scope="module")
def client():
    """
    Module-scoped FastAPI TestClient for integration endpoint testing.
    """
    with TestClient(app) as c:
        yield c
