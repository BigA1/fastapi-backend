from fastapi.testclient import TestClient
from app.main import app
import pytest
import os
from io import BytesIO

client = TestClient(app)

@pytest.fixture
def mock_user():
    return {
        "id": "test-user-id",
        "token": "test-token"
    }

@pytest.fixture
def mock_memory():
    return {
        "id": 1
    }

@pytest.fixture
def mock_media():
    return {
        "id": 1
    }

def test_get_memory_media(client, mock_user, mock_memory):
    response = client.get(f"/api/media/memory/{mock_memory['id']}")
    assert response.status_code == 401  # Unauthorized without auth

def test_upload_media(client, mock_user, mock_memory):
    # Create a test file
    test_file = BytesIO(b"test file content")
    test_file.name = "test.txt"
    
    # Test file upload
    response = client.post(
        "/api/media/upload",
        files={"file": ("test.txt", test_file, "text/plain")},
        data={
            "memory_id": str(mock_memory["id"]),
            "media_type": "image",
            "label": "Test Image"
        }
    )
    assert response.status_code == 401  # Unauthorized without auth

def test_delete_media(client, mock_user, mock_media):
    response = client.delete(f"/api/media/{mock_media['id']}")
def test_delete_media(mock_user):
    response = client.delete("/api/media/1")
    assert response.status_code == 401  # Unauthorized without auth 