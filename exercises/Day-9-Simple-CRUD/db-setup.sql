-- Enable foreign keys if needed, though tasks is standalone here.
PRAGMA foreign_keys = ON;

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    taskID INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert starting seed tasks for testing
INSERT INTO tasks (title, description, status) VALUES
('Learn FastAPI Router', 'Study how to group API endpoints using APIRouter in FastAPI.', 'completed'),
('Understand SQLite connection', 'Explore sqlite3 module in Python and raw SQL query execution.', 'completed'),
('Build API Tasks CRUD', 'Combine FastAPI and raw SQL SQLite connection to build a complete tasks CRUD API.', 'pending'),
('Write integration tests', 'Write manual tests or automated tests to verify the tasks API.', 'pending');
