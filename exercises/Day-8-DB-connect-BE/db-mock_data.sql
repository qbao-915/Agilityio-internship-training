DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS teams;

-- 1. Create Teams Table
CREATE TABLE teams (
    teamID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    foundation_date DATE DEFAULT CURRENT_DATE
);

-- 2. Create Members Table
CREATE TABLE members (
    memberID INTEGER PRIMARY KEY AUTOINCREMENT,
    teamID INTEGER NOT NULL,
    name TEXT,
    email TEXT UNIQUE,
    role TEXT,
    FOREIGN KEY (teamID) REFERENCES teams(teamID)
);

-- 3. Insert Sample Data
INSERT INTO teams (name, foundation_date) VALUES ('Cloud/DB Division','2025-01-01');
INSERT INTO teams (name) VALUES ('Frontend Team');
INSERT INTO teams (name) VALUES ('Mobile App Team');

INSERT INTO members (teamID, name, email, role) VALUES (1, 'Bao Nguyen', 'bao@example.com', 'Intern');
INSERT INTO members (teamID, name, email, role) VALUES (1, 'Tung Tran', 'tung.tran@example.com', 'Lead Engineer');
INSERT INTO members (teamID, name, email, role) VALUES (2, 'Minh Nguyen', 'minh@example.com', 'Frontend Developer');
INSERT INTO members (teamID, name, email, role) VALUES (2, 'An Tran', 'an.tran@example.com', 'UI/UX Designer');
INSERT INTO members (teamID, name, email, role) VALUES (3, 'Binh Le', 'binh.le@example.com', 'iOS Developer');

-- 4. Sample Queries for Validation & Learning

-- Query A: Get all members with their corresponding team names
-- Demonstrates 1-to-Many relation retrieval.
SELECT 
    m.memberID, 
    m.name AS member_name, 
    m.role, 
    t.name AS team_name 
FROM members m
JOIN teams t ON m.teamID = t.teamID;

-- Query B: Find details of a specific team and its members
-- Demonstrates filtering with a WHERE clause.
SELECT 
    t.name AS team_name, 
    m.name AS member_name, 
    m.role
FROM teams t
LEFT JOIN members m ON t.teamID = m.teamID
WHERE t.name = 'Cloud/DB Division';

-- Query C: Count the number of members in each team
-- Demonstrates aggregation using GROUP BY and COUNT().
SELECT 
    t.name AS team_name, 
    COUNT(m.memberID) AS member_count
FROM teams t
LEFT JOIN members m ON t.teamID = m.teamID
GROUP BY t.teamID;