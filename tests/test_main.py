from fastapi.testclient import TestClient
from app.main import app
import pytest
from datetime import datetime

client = TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Storee API"}

@pytest.fixture
def mock_user():
    return {
        "id": "test-user-id",
        "token": "test-token"
    }

def test_create_memory(client, mock_user):
    memory_data = {
        "title": "Test Memory",
        "content": "This is a test memory",
        "date": datetime.now().isoformat()
    }
    response = client.post("/api/memories/", json=memory_data)
    assert response.status_code == 401  # Unauthorized without auth

def test_get_memories(client, mock_user):
    response = client.get("/api/memories/")
    assert response.status_code == 401  # Unauthorized without auth

def test_get_memory_by_id(client, mock_user, mock_memory):
    response = client.get(f"/api/memories/{mock_memory['id']}")
    assert response.status_code == 401  # Unauthorized without auth

def test_update_memory(client, mock_user, mock_memory):
    memory_data = {
        "title": "Updated Memory",
        "content": "This is an updated test memory",
        "date": datetime.now().isoformat()
    }
    response = client.put(f"/api/memories/{mock_memory['id']}", json=memory_data)
    assert response.status_code == 401  # Unauthorized without auth

def test_delete_memory(client, mock_user, mock_memory):
    response = client.delete(f"/api/memories/{mock_memory['id']}")
    assert response.status_code == 401  # Unauthorized without auth

def test_search_memories(client, mock_user):
    response = client.get("/api/memories/search?query=test")
    assert response.status_code == 401  # Unauthorized without auth

def test_get_memory_media(client, mock_user, mock_memory):
    response = client.get(f"/api/memories/{mock_memory['id']}/media")
    assert response.status_code == 401  # Unauthorized without auth
