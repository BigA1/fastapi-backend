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

def test_transcribe_audio(client, mock_user):
    # Create a test audio file
    test_file = BytesIO(b"test audio content")
    test_file.name = "test.wav"
    
    # Test audio transcription
    response = client.post(
        "/api/transcription/transcribe",
        files={"file": ("test.wav", test_file, "audio/wav")}
    )
    assert response.status_code == 401  # Unauthorized without auth

def test_get_transcription_status(client, mock_user):
    response = client.get("/api/transcription/status/1")
    assert response.status_code == 401  # Unauthorized without auth 