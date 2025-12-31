"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from api import app
import tempfile
import os


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_query_endpoint_empty(client):
    """Test query endpoint with empty text."""
    response = client.post("/query", json={"text": ""})
    assert response.status_code == 400


def test_query_endpoint_no_documents(client):
    """Test query endpoint when no documents are ingested."""
    # This will likely return "no relevant information" message
    response = client.post("/query", json={"text": "What is machine learning?"})
    
    # Should return 200 even if no chunks found
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "retrieved_chunks" in data
    assert "latency_ms" in data


def test_transcribe_endpoint_implementation(client):
    """Test transcribe endpoint (implemented in Phase 2)."""
    # Mock the transcription service to avoid actual API calls
    from unittest.mock import patch
    
    with patch('api.transcription_service') as mock_service:
        mock_service.transcribe_audio.return_value = {
            "transcript": "test transcription",
            "confidence": None,
            "language": "en"
        }
        
        audio_content = b"fake audio content"
        response = client.post(
            "/transcribe",
            files={"audio": ("test.webm", audio_content, "audio/webm")}
        )
        
        # Should return 200 with transcription in Phase 2
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data

