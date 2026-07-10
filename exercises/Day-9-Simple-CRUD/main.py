from contextlib import asynccontextmanager
import sqlite3
import os
from fastapi import FastAPI
from routers.tasks import router as tasks_router

# Database path setup
sql_file_path = os.path.join(os.path.dirname(__file__), 'db-setup.sql')
db_file_path = os.path.join(os.path.dirname(__file__), 'tasks.db')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the database schema and seeds mock data on server startup."""
    conn = None
    try:
        db_exists = os.path.exists(db_file_path)
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        
        if not db_exists or os.path.getsize(db_file_path) == 0:
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            cursor.executescript(sql_script)
            conn.commit()
            print("Database initialized and seeded successfully!")
        else:
            print("Database already exists. Skipping seeding.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    finally:
        if conn:
            conn.close()
    
    yield  # Control is handed over to the FastAPI app

app = FastAPI(
    title="Day 9: Tasks CRUD API",
    description="A simple CRUD API for managing tasks using FastAPI and SQLite with raw SQL.",
    version="1.0.0",
    lifespan=lifespan
)

# Include task router
app.include_router(tasks_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Tasks CRUD API. Go to /docs to view the interactive API documentation."}
