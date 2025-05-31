import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return {
        "id": "test-user-id",
        "token": "test-token"
    }

@pytest.fixture
def mock_memory():
    return {
        "id": 1,
        "title": "Test Memory",
        "content": "This is a test memory",
        "date": "2024-05-26",
        "user_id": "test-user-id",
        "created_at": "2024-05-26T12:00:00",
        "updated_at": "2024-05-26T12:00:00"
    }

@pytest.fixture
def mock_media():
    return {
        "id": 1,
        "memory_id": 1,
        "file_path": "test-user-id/test.jpg",
        "media_type": "image",
        "user_id": "test-user-id",
        "created_at": "2024-05-26T12:00:00",
        "label": "Test Image"
    } 