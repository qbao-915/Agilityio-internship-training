import sqlite3
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Day 8: Teams & Members API")

sql_file_path = os.path.join(os.path.dirname(__file__), 'db-mock_data.sql')
db_file_path = os.path.join(os.path.dirname(__file__), 'my_sample.db')

# --- 1. DATABASE INITIALIZATION ---
@app.on_event("startup")
def startup_event():
    """Reads db-mock_data.sql and initializes the database when the server starts."""
    conn = None
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        print("Database initialized and seeded successfully!")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    finally:
        if conn:
            conn.close()

# --- 2. PYDANTIC SCHEMAS ---
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Tên của team không được để trống")

class TeamUpdate(BaseModel):
    name: str = Field(..., min_length=1, description="Tên của team không được để trống")

# --- 3. API ENDPOINTS (READ & WRITE) ---

def get_db_connection():
    conn = sqlite3.connect(db_file_path)
    conn.row_factory = sqlite3.Row  # Returns dict-like rows
    conn.execute("PRAGMA foreign_keys = ON;") # Kích hoạt bảo vệ Khóa ngoại (Foreign Key)
    return conn

@app.get("/teams/", summary="Read all teams")
def get_teams():
    """Fetches all teams from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams;")
    teams = cursor.fetchall()
    conn.close()
    return [dict(team) for team in teams]

@app.post("/teams/", summary="Write a new team")
def create_team(team: TeamCreate):
    """Inserts a new team into the database."""
    team_name = team.name.strip()
    if not team_name:
        raise HTTPException(status_code=400, detail="Tên của team không được để trống hoặc chỉ chứa khoảng trắng.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO teams (name) VALUES (?);", (team_name,))
        conn.commit()
        new_id = cursor.lastrowid
        return {"message": "Team created successfully!", "teamID": new_id, "name": team_name}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Team name already exists.")
    finally:
        conn.close()

@app.put("/teams/{team_id}", summary="Update an existing team")
def update_team(team_id: int, team: TeamUpdate):
    """Cập nhật tên của một team dựa vào ID."""
    team_name = team.name.strip()
    if not team_name:
        raise HTTPException(status_code=400, detail="Tên của team không được để trống hoặc chỉ chứa khoảng trắng.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE teams SET name = ? WHERE teamID = ?;", (team_name, team_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy Team với ID này.")
        conn.commit()
        return {"message": "Cập nhật Team thành công!", "teamID": team_id, "new_name": team_name}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Tên Team đã tồn tại, vui lòng chọn tên khác.")
    finally:
        conn.close()

@app.delete("/teams/{team_id}", summary="Delete a team")
def delete_team(team_id: int):
    """Xóa một team khỏi database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM teams WHERE teamID = ?;", (team_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy Team với ID này để xóa.")
        conn.commit()
        return {"message": "Xóa Team thành công!", "teamID": team_id}
    except sqlite3.IntegrityError:
        conn.rollback()
        # Bắt lỗi khi cố xóa Team đang có Member (Vi phạm Foreign Key)
        raise HTTPException(status_code=400, detail="Không thể xóa! Team này hiện vẫn đang có thành viên.")
    finally:
        conn.close()

@app.get("/members/", summary="Read all members with team names")
def get_members():
    """Demonstrates a JOIN query returning members and their team names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.memberID, m.name, m.role, t.name as team_name 
        FROM members m
        JOIN teams t ON m.teamID = t.teamID;
    """
    cursor.execute(query)
    members = cursor.fetchall()
    conn.close()
    return [dict(member) for member in members]