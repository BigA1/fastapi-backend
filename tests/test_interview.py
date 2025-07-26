import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_interviewer import AIInterviewerService
from unittest.mock import Mock, patch

client = TestClient(app)

@pytest.fixture
def mock_openai():
    with patch('app.services.ai_interviewer.openai') as mock:
        yield mock

@pytest.fixture
def mock_auth():
    with patch('app.core.auth.get_current_user') as mock:
        mock.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "token": "test-token"
        }
        yield mock

def test_start_interview(mock_openai, mock_auth):
    """Test starting an interview session."""
    # Mock OpenAI response
    mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="I'd love to help you capture your memories! What's a memory or experience you'd like to share today?"))
    ]
    
    response = client.post(
        "/api/interview/start",
        json={"initial_context": "My childhood memories"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "current_question" in data
    assert "conversation" in data

def test_continue_interview(mock_openai, mock_auth):
    """Test continuing an interview session."""
    # Mock OpenAI response for continue
    mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="That sounds wonderful! Can you tell me more about that experience?"))
    ]
    
    # First start an interview
    start_response = client.post(
        "/api/interview/start",
        json={"initial_context": "My childhood memories"}
    )
    session_data = start_response.json()
    
    # Then continue it
    continue_response = client.post(
        "/api/interview/continue",
        json={
            "session_id": session_data["session_id"],
            "user_response": "I remember playing in the park with my friends"
        }
    )
    
    assert continue_response.status_code == 200
    data = continue_response.json()
    assert "conversation" in data
    assert len(data["conversation"]) > 0

def test_end_interview(mock_openai, mock_auth):
    """Test ending an interview session."""
    # Mock OpenAI response for end
    mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="Thank you for sharing those memories with me. It sounds like you had a wonderful childhood filled with joy and friendship."))
    ]
    
    # First start an interview
    start_response = client.post(
        "/api/interview/start",
        json={"initial_context": "My childhood memories"}
    )
    session_data = start_response.json()
    
    # Then end it
    end_response = client.post(
        "/api/interview/end",
        json={"session_id": session_data["session_id"]}
    )
    
    assert end_response.status_code == 200
    data = end_response.json()
    assert "summary" in data
    assert data["status"] == "active"  # Should be updated to completed when creating memory

def test_suggest_title(mock_openai, mock_auth):
    """Test suggesting a memory title."""
    # Mock OpenAI response for title suggestion
    mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="Childhood Park Adventures"))
    ]
    
    # First start an interview
    start_response = client.post(
        "/api/interview/start",
        json={"initial_context": "My childhood memories"}
    )
    session_data = start_response.json()
    
    # Then get title suggestion
    title_response = client.get(f"/api/interview/suggest-title/{session_data['session_id']}")
    
    assert title_response.status_code == 200
    data = title_response.json()
    assert "suggested_title" in data
    assert data["suggested_title"] == "Childhood Park Adventures" 