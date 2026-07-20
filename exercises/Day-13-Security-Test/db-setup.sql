-- Database schema initialization for Day 13 Tasks
-- Creates the tasks and users tables, and seeds them with mock data

-- 1. Tasks Table
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

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);

-- Seed a dummy user (Username: admin, Password: admin123)
-- The password is pre-hashed using bcrypt
INSERT INTO users (username, hashed_password) VALUES 
('admin', '$2b$12$mSvsFlr1I1G1zw02/GDyDOHPtzjPOzP4Ty5WiXO/AyNi9pfUcCsmq');
