-- Database schema initialization for Day 10 tasks
-- Creates the tasks table and seeds it with default values

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'Pending'
);

-- Seed tasks for test database
INSERT INTO tasks (title, status) VALUES 
('Learn FastAPI Validation and Error Handling', 'Pending'),
('Implement global Exception Handlers', 'Pending'),
('Verify SELECT before DELETE operations', 'Pending');
