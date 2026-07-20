import pytest
from fastapi import status

def test_root_endpoint(client):
    """
    Test that calling the root URL returns a 200 OK greeting.
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Welcome" in response.json().get("message", "")

def test_login_failure(client):
    """
    Test that logging in with invalid credentials returns HTTP 401 Unauthorized.
    """
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json().get("detail", "")

def test_login_success(client):
    """
    Test that logging in with valid credentials returns a valid JWT access token.
    """
    payload = {"username": "admin", "password": "admin123"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_data_no_auth(client):
    """
    Test that access is denied (HTTP 401) if no Authorization header is provided.
    """
    response = client.get("/protected-data")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Bearer token required" in response.json().get("detail", "")

def test_protected_data_invalid_scheme(client):
    """
    Test that access is denied (HTTP 401) if scheme is not Bearer.
    """
    payload = {"username": "admin", "password": "admin123"}
    login_response = client.post("/login", json=payload)
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Basic {token}"}
    response = client.get("/protected-data", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Bearer token required" in response.json().get("detail", "")

def test_protected_data_valid_auth(client):
    """
    Test that accessing the protected data with a valid JWT succeeds (HTTP 200).
    """
    payload = {"username": "admin", "password": "admin123"}
    login_response = client.post("/login", json=payload)
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected-data", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["user"] == "admin"
    assert "sensitive_info" in data

def test_get_tasks(client):
    """
    Test retrieving task records.
    """
    response = client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 3  # Based on seeded db-setup.sql

def test_create_task_success(client):
    """
    Test successfully creating a new task.
    """
    payload = {"title": "Write unit and integration tests", "status": "In Progress"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["title"] == "Write unit and integration tests"
    assert data["status"] == "In Progress"
    assert "id" in data

def test_create_task_validation_error(client):
    """
    Test that invalid empty/whitespace task titles result in an HTTP 422 validation error.
    """
    payload = {"title": "   ", "status": "Pending"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    data = response.json()
    assert "detail" in data
    assert "body" in data
