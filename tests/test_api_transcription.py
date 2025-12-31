"""Tests for transcription API endpoint."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_transcribe_endpoint_success(client):
    """Test successful transcription."""
    # Mock the transcription service
    with patch('api.transcription_service') as mock_service:
        mock_service.transcribe_audio.return_value = {
            "transcript": "This is a test transcription",
            "confidence": None,
            "language": "en"
        }
        
        # Create a fake audio file
        audio_content = b"fake audio data"
        files = {"audio": ("test.webm", audio_content, "audio/webm")}
        
        response = client.post("/transcribe", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        assert data["transcript"] == "This is a test transcription"
        assert data["language"] == "en"


def test_transcribe_endpoint_empty_file(client):
    """Test transcription with empty file."""
    files = {"audio": ("empty.webm", b"", "audio/webm")}
    
    response = client.post("/transcribe", files=files)
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_transcribe_endpoint_missing_file(client):
    """Test transcription without file."""
    response = client.post("/transcribe")
    
    assert response.status_code == 422  # Validation error


def test_transcribe_endpoint_error(client):
    """Test transcription error handling."""
    with patch('api.transcription_service') as mock_service:
        mock_service.transcribe_audio.side_effect = ValueError("Transcription failed")
        
        audio_content = b"fake audio data"
        files = {"audio": ("test.webm", audio_content, "audio/webm")}
        
        response = client.post("/transcribe", files=files)
        
        assert response.status_code == 400
        assert "Transcription failed" in response.json()["detail"]

