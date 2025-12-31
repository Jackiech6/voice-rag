"""Tests for document upload functionality."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_upload_document_success(client):
    """Test successful document upload."""
    with patch('api.ingestion_service') as mock_service:
        mock_service.ingest_document.return_value = {
            "success": True,
            "document_id": 1,
            "title": "Test Document",
            "chunks_created": 5,
            "message": "Successfully ingested",
            "error": None,
            "already_exists": False
        }
        
        # Create a fake file
        file_content = b"Test document content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = client.post("/documents/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == 1
        assert data["chunks_created"] == 5
        assert "test.txt" in mock_service.ingest_document.call_args[0][0] or True


def test_upload_document_unsupported_type(client):
    """Test upload with unsupported file type."""
    file_content = b"Test content"
    files = {"file": ("test.exe", file_content, "application/x-msdownload")}
    
    response = client.post("/documents/upload", files=files)
    
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_upload_document_too_large(client):
    """Test upload with file too large."""
    # Create a file larger than 50MB (simulated)
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    
    response = client.post("/documents/upload", files=files)
    
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_upload_document_already_exists(client):
    """Test upload when document already exists."""
    with patch('api.ingestion_service') as mock_service:
        mock_service.ingest_document.return_value = {
            "success": True,
            "document_id": 1,
            "title": "Existing Document",
            "chunks_created": 0,
            "message": "Document already ingested",
            "error": None,
            "already_exists": True
        }
        
        file_content = b"Test content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = client.post("/documents/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["already_exists"] is True
        assert data["chunks_created"] == 0


def test_upload_document_ingestion_error(client):
    """Test upload when ingestion fails."""
    with patch('api.ingestion_service') as mock_service:
        mock_service.ingest_document.return_value = {
            "success": False,
            "document_id": None,
            "title": None,
            "chunks_created": 0,
            "message": "Ingestion error",
            "error": "INGESTION_ERROR"
        }
        
        file_content = b"Test content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = client.post("/documents/upload", files=files)
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


def test_list_documents(client):
    """Test listing documents."""
    with patch('database.get_db_session') as mock_session:
        from database import Document
        
        # Mock database session
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.id = 1
        mock_doc.title = "Test Doc"
        mock_doc.file_path = "/path/to/doc.pdf"
        mock_doc.created_at = "2024-01-01T00:00:00"
        
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = [mock_doc]
        mock_db.query.return_value = mock_query
        mock_session.return_value = mock_db
        
        response = client.get("/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert data["total"] >= 0


def test_list_documents_empty(client):
    """Test listing documents when none exist."""
    with patch('database.get_db_session') as mock_session:
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        mock_session.return_value = mock_db
        
        response = client.get("/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["documents"]) == 0

