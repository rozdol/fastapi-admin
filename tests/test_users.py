import pytest
from fastapi.testclient import TestClient
from app.schemas.user import UserCreate


def test_create_user(client: TestClient):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data


def test_get_users(client: TestClient):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_not_found(client: TestClient):
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
