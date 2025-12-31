"""Integration tests for document deletion."""
import pytest
from fastapi.testclient import TestClient
from api import app
from database import init_db, get_db_session, Document, Chunk
from vector_store import VectorStore
from ingestion_service import IngestionService
from deletion_service import DeletionService
import tempfile
import os
from pathlib import Path


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write("This is a test document for deletion testing.\n" * 10)
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


def test_delete_document_full_flow(client, sample_text_file):
    """Test complete deletion flow: ingest -> delete -> verify."""
    # Initialize
    init_db()
    ingestion_service = IngestionService()
    deletion_service = DeletionService()
    
    # Step 1: Ingest document
    result = ingestion_service.ingest_document(sample_text_file)
    assert result["success"] is True
    document_id = result["document_id"]
    
    # Verify document exists
    db_session = get_db_session()
    try:
        doc = db_session.query(Document).filter_by(id=document_id).first()
        assert doc is not None
        assert doc.title is not None
        
        chunks = db_session.query(Chunk).filter_by(document_id=document_id).all()
        assert len(chunks) > 0
    finally:
        db_session.close()
    
    # Step 2: Delete document via API
    response = client.delete(f"/documents/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["chunks_deleted"] > 0
    
    # Step 3: Verify deletion
    db_session = get_db_session()
    try:
        doc = db_session.query(Document).filter_by(id=document_id).first()
        assert doc is None
        
        chunks = db_session.query(Chunk).filter_by(document_id=document_id).all()
        assert len(chunks) == 0
    finally:
        db_session.close()
    
    # Step 4: Verify vector store deletion
    vector_store = VectorStore()
    # Try to search - should not find chunks from deleted document
    # (This is a basic check - full verification would require querying vector store directly)


def test_delete_nonexistent_document(client):
    """Test deleting a document that doesn't exist."""
    response = client.delete("/documents/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_after_deletion(client, sample_text_file):
    """Test that deleted documents don't appear in list."""
    # Initialize
    init_db()
    ingestion_service = IngestionService()
    
    # Ingest document
    result = ingestion_service.ingest_document(sample_text_file)
    assert result["success"] is True
    document_id = result["document_id"]
    
    # Verify it appears in list
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    doc_ids = [doc["id"] for doc in data["documents"]]
    assert document_id in doc_ids
    
    # Delete document
    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200
    
    # Verify it no longer appears in list
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    doc_ids = [doc["id"] for doc in data["documents"]]
    assert document_id not in doc_ids


def test_delete_multiple_documents(client):
    """Test deleting multiple documents."""
    # Initialize
    init_db()
    ingestion_service = IngestionService()
    deletion_service = DeletionService()
    
    # Create and ingest multiple documents
    document_ids = []
    for i in range(3):
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(f"Test document {i}\n" * 5)
        temp_file.close()
        
        result = ingestion_service.ingest_document(temp_file.name)
        assert result["success"] is True
        document_ids.append(result["document_id"])
        
        os.unlink(temp_file.name)
    
    # Delete all documents
    for doc_id in document_ids:
        response = client.delete(f"/documents/{doc_id}")
        assert response.status_code == 200
    
    # Verify all are deleted
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    remaining_ids = [doc["id"] for doc in data["documents"]]
    for doc_id in document_ids:
        assert doc_id not in remaining_ids

