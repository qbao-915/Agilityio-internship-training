import sqlite3
import os

# Using SQLite in Python

sql_file_path = os.path.join(os.path.dirname(__file__), 'Sample.sql')
db_file_path = os.path.join(os.path.dirname(__file__), 'my_sample.db')

try:
    # 1. Read
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()

    # 2. Connect
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # 3. Execute the SQL script
    cursor.executescript(sql_script)
    print("Database initialized successfully!")

    # 4. Insert sample data
    cursor.execute("INSERT INTO teams (name, foundation_date) VALUES ('Cloud/DB Division','2025-01-01');")
    cursor.execute("INSERT INTO teams (name) VALUES ('Frontend Team');")
    cursor.execute("INSERT INTO teams (name) VALUES ('Mobile App Team');")

    cursor.execute("INSERT INTO members (teamID, name, email, role) VALUES (1, 'Bao Nguyen', 'bao@example.com', 'Intern');")
    cursor.execute("INSERT INTO members (teamID, name, email, role) VALUES (1, 'Tung Tran', 'tung.tran@example.com', 'Lead Engineer');")
    cursor.execute("INSERT INTO members (teamID, name, email, role) VALUES (2, 'Minh Nguyen', 'minh@example.com', 'Frontend Developer');")
    cursor.execute("INSERT INTO members (teamID, name, email, role) VALUES (2, 'An Tran', 'an.tran@example.com', 'UI/UX Designer');")
    cursor.execute("INSERT INTO members (teamID, name, email, role) VALUES (3, 'Binh Le', 'binh.le@example.com', 'iOS Developer');")
    conn.commit()
    print("Sample data inserted successfully!")    

    # 5. Query for sample data
        # ---- TEAMS ----
    cursor.execute("SELECT * FROM teams;")
    team_rows = cursor.fetchall()
    print("\n--- Sample data in TEAMS table ---")
    print("(teamID | name | foundation_date)")
    for row in team_rows:
        print(row)

        # ---- MEMBERS ----
    cursor.execute("SELECT * FROM members;")
    member_rows = cursor.fetchall()
    print("\n--- Sample data in MEMBERS table ---")
    print("(memberID | teamID | name | email | role)")
    for row in member_rows:
        print(row)

    cursor.execute("""
    SELECT members.name, members.role, teams.name 
    FROM members 
    JOIN teams ON members.teamID = teams.teamID;
    """)
    print("\n--- JOIN MEMBERS & TEAMS ---")
    for row in cursor.fetchall():
        print(f"Name: {row[0]} | Role: {row[1]} | Team: {row[2]}")
        
except sqlite3.Error as e:
    print(f"Database error: {e}")

finally:
    if conn:
        conn.close()