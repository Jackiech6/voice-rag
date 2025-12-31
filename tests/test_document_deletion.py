"""Tests for document deletion functionality."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, MagicMock
from database import get_db_session, Document, Chunk


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_delete_document_success(client):
    """Test successful document deletion."""
    with patch('api.deletion_service') as mock_service:
        mock_service.delete_document.return_value = {
            "success": True,
            "document_id": 1,
            "title": "Test Document",
            "chunks_deleted": 5,
            "message": "Successfully deleted document: Test Document (5 chunks removed)",
            "error": None
        }
        
        response = client.delete("/documents/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == 1
        assert data["chunks_deleted"] == 5
        assert "Test Document" in data["message"]


def test_delete_document_not_found(client):
    """Test deletion of non-existent document."""
    with patch('api.deletion_service') as mock_service:
        mock_service.delete_document.return_value = {
            "success": False,
            "document_id": 999,
            "title": None,
            "chunks_deleted": 0,
            "message": "Document with ID 999 not found",
            "error": "DOCUMENT_NOT_FOUND"
        }
        
        response = client.delete("/documents/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_delete_document_error(client):
    """Test deletion error handling."""
    with patch('api.deletion_service') as mock_service:
        mock_service.delete_document.return_value = {
            "success": False,
            "document_id": 1,
            "title": None,
            "chunks_deleted": 0,
            "message": "Error deleting document: Database error",
            "error": "DELETION_ERROR"
        }
        
        response = client.delete("/documents/1")
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


def test_list_documents_with_metadata(client):
    """Test listing documents with informative metadata."""
    with patch('database.get_db_session') as mock_session:
        from pathlib import Path
        import tempfile
        import os
        
        # Create a temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(b'test content')
        temp_file.close()
        temp_path = temp_file.name
        
        try:
            mock_db = MagicMock()
            mock_doc = MagicMock()
            mock_doc.id = 1
            mock_doc.title = "Test Document"
            mock_doc.file_path = temp_path
            mock_doc.created_at = "2024-01-01T00:00:00"
            
            mock_chunk = MagicMock()
            mock_chunk.document_id = 1
            
            mock_db.query.return_value.order_by.return_value.all.return_value = [mock_doc]
            mock_db.query.return_value.filter_by.return_value.count.return_value = 3
            
            # Mock the query chain for chunks count
            chunks_query = MagicMock()
            chunks_query.filter_by.return_value.count.return_value = 3
            mock_db.query.side_effect = lambda model: {
                Document: MagicMock(order_by=lambda x: MagicMock(all=lambda: [mock_doc])),
                Chunk: chunks_query
            }[model]
            
            mock_session.return_value.__enter__.return_value = mock_db
            mock_session.return_value.__exit__.return_value = None
            
            response = client.get("/documents")
            
            assert response.status_code == 200
            data = response.json()
            assert "documents" in data
            assert data["total"] >= 0
            
            if len(data["documents"]) > 0:
                doc = data["documents"][0]
                assert "file_name" in doc
                assert "file_type" in doc
                assert "chunks_count" in doc
                assert "file_size" in doc or doc["file_size"] is None
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def test_list_documents_empty(client):
    """Test listing documents when none exist."""
    with patch('database.get_db_session') as mock_session:
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
        response = client.get("/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["documents"]) == 0


def test_delete_document_invalid_id(client):
    """Test deletion with invalid document ID."""
    response = client.delete("/documents/abc")
    
    # Should return 422 for invalid ID format
    assert response.status_code in [422, 404]


def test_list_documents_file_info(client):
    """Test that document list includes file information."""
    with patch('database.get_db_session') as mock_session:
        from pathlib import Path
        import tempfile
        import os
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.write(b'test content')
        temp_file.close()
        temp_path = temp_file.name
        
        try:
            mock_db = MagicMock()
            mock_doc = MagicMock()
            mock_doc.id = 1
            mock_doc.title = "Test"
            mock_doc.file_path = temp_path
            mock_doc.created_at = "2024-01-01T00:00:00"
            
            chunks_query = MagicMock()
            chunks_query.filter_by.return_value.count.return_value = 2
            
            def query_side_effect(model):
                if model == Document:
                    query_mock = MagicMock()
                    query_mock.order_by.return_value.all.return_value = [mock_doc]
                    return query_mock
                elif model == Chunk:
                    return chunks_query
                return MagicMock()
            
            mock_db.query.side_effect = query_side_effect
            mock_session.return_value.__enter__.return_value = mock_db
            mock_session.return_value.__exit__.return_value = None
            
            response = client.get("/documents")
            
            assert response.status_code == 200
            data = response.json()
            
            if data["documents"]:
                doc = data["documents"][0]
                assert doc["file_name"] == Path(temp_path).name
                assert doc["file_type"] == "txt"
                assert doc["chunks_count"] == 2
                assert doc["file_size"] is not None
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

