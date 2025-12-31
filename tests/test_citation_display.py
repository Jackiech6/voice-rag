"""Tests for citation display and mapping."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_citation_mapping_in_answer(client):
    """Test that citations in answer text map to actual citation objects."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store, \
         patch('api.llm_service') as mock_llm:
        
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = [
            {
                "id": "chunk_1",
                "text": "Machine learning is a subset of AI.",
                "metadata": {"document_title": "AI Basics", "page": 1},
                "similarity_score": 0.9
            },
            {
                "id": "chunk_2",
                "text": "There are three types of ML.",
                "metadata": {"document_title": "AI Basics", "page": 2},
                "similarity_score": 0.85
            }
        ]
        
        # Mock LLM response with citations
        mock_llm.generate_answer.return_value = {
            "answer": "Machine learning [1] is important. There are types [2] of ML.",
            "citations": [
                {
                    "id": "chunk_1",
                    "document_title": "AI Basics",
                    "page": 1,
                    "text": "Machine learning is a subset of AI.",
                    "similarity_score": 0.9
                },
                {
                    "id": "chunk_2",
                    "document_title": "AI Basics",
                    "page": 2,
                    "text": "There are three types of ML.",
                    "similarity_score": 0.85
                }
            ]
        }
        
        response = client.post("/query", json={"text": "What is machine learning?"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Check answer contains citation markers
        assert "[" in data["answer"] and "]" in data["answer"]
        
        # Check citations are returned
        assert len(data["citations"]) > 0
        
        # Check citation IDs match chunks
        citation_ids = {c["id"] for c in data["citations"]}
        chunk_ids = {c["id"] for c in data["retrieved_chunks"]}
        assert citation_ids.issubset(chunk_ids)


def test_citation_with_no_matches(client):
    """Test citation handling when no chunks match."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store:
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = []
        
        response = client.post("/query", json={"text": "completely unrelated query"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["citations"]) == 0
        assert len(data["retrieved_chunks"]) == 0


def test_retrieved_chunks_highlighting(client):
    """Test that cited chunks are identifiable in retrieved chunks."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store, \
         patch('api.llm_service') as mock_llm:
        
        chunk_1 = {
            "id": "chunk_1",
            "text": "Test chunk 1",
            "metadata": {"document_title": "Test Doc", "page": 1},
            "similarity_score": 0.9
        }
        
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = [chunk_1]
        
        mock_llm.generate_answer.return_value = {
            "answer": "Test answer [1]",
            "citations": [
                {
                    "id": "chunk_1",
                    "document_title": "Test Doc",
                    "page": 1,
                    "text": "Test chunk 1",
                    "similarity_score": 0.9
                }
            ]
        }
        
        response = client.post("/query", json={"text": "test"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that cited chunk is in retrieved chunks
        cited_ids = {c["id"] for c in data["citations"]}
        retrieved_ids = {c["id"] for c in data["retrieved_chunks"]}
        assert cited_ids.issubset(retrieved_ids)

