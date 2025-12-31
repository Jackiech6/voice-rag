"""Tests for error handling across the system."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, MagicMock
from embeddings import EmbeddingService
from llm_service import LLMService
from transcription_service import TranscriptionService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_query_embedding_error(client):
    """Test error handling when embedding generation fails."""
    with patch('api.embedding_service') as mock_service:
        mock_service.generate_embedding.side_effect = Exception("API Error")
        
        response = client.post("/query", json={"text": "test query"})
        
        assert response.status_code == 500
        assert "embedding" in response.json()["detail"].lower()
        assert "API" in response.json()["detail"]


def test_query_retrieval_error(client):
    """Test error handling when retrieval fails."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store:
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.side_effect = Exception("Database error")
        
        response = client.post("/query", json={"text": "test query"})
        
        assert response.status_code == 500
        assert "retrieve" in response.json()["detail"].lower()


def test_query_llm_error(client):
    """Test error handling when LLM generation fails."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store, \
         patch('api.llm_service') as mock_llm:
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = [
            {
                "id": "chunk_1",
                "text": "Test chunk",
                "metadata": {"document_title": "Test", "page": 1},
                "similarity_score": 0.8
            }
        ]
        mock_llm.generate_answer.side_effect = Exception("LLM API Error")
        
        response = client.post("/query", json={"text": "test query"})
        
        assert response.status_code == 500
        assert "answer" in response.json()["detail"].lower()


def test_query_no_chunks(client):
    """Test handling when no chunks are retrieved."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store:
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = []
        
        response = client.post("/query", json={"text": "test query"})
        
        assert response.status_code == 200
        data = response.json()
        assert "couldn't find" in data["answer"].lower() or "not found" in data["answer"].lower()
        assert len(data["citations"]) == 0


def test_query_low_similarity(client):
    """Test handling when chunks have low similarity."""
    with patch('api.embedding_service') as mock_emb, \
         patch('api.vector_store') as mock_store:
        mock_emb.generate_embedding.return_value = [0.1] * 1536
        mock_store.search.return_value = [
            {
                "id": "chunk_1",
                "text": "Test chunk",
                "metadata": {"document_title": "Test", "page": 1},
                "similarity_score": 0.3  # Below threshold
            }
        ]
        
        response = client.post("/query", json={"text": "test query"})
        
        assert response.status_code == 200
        data = response.json()
        assert "relevance is low" in data["answer"].lower() or "similarity" in data["answer"].lower()


def test_transcription_empty_file(client):
    """Test transcription with empty file."""
    files = {"audio": ("empty.webm", b"", "audio/webm")}
    response = client.post("/transcribe", files=files)
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_transcription_api_error(client):
    """Test transcription error handling."""
    with patch('api.transcription_service') as mock_service:
        mock_service.transcribe_audio.side_effect = ValueError("Transcription failed")
        
        audio_content = b"fake audio data"
        files = {"audio": ("test.webm", audio_content, "audio/webm")}
        response = client.post("/transcribe", files=files)
        
        assert response.status_code == 400
        assert "transcription" in response.json()["detail"].lower()


def test_cache_functionality():
    """Test embedding cache."""
    from cache import EmbeddingCache
    
    cache = EmbeddingCache(max_size=10, ttl_seconds=3600)
    
    # Test set and get
    cache.set("test query", [0.1, 0.2, 0.3])
    result = cache.get("test query")
    
    assert result == [0.1, 0.2, 0.3]
    
    # Test cache miss
    assert cache.get("different query") is None
    
    # Test clear
    cache.clear()
    assert cache.get("test query") is None
    assert cache.size() == 0


def test_embedding_service_with_cache():
    """Test embedding service uses cache."""
    from unittest.mock import patch, MagicMock
    
    with patch('embeddings.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock embedding response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        service = EmbeddingService(use_cache=True)
        
        # First call - should hit API
        embedding1 = service.generate_embedding("test query")
        assert mock_client.embeddings.create.call_count == 1
        
        # Second call - should use cache
        embedding2 = service.generate_embedding("test query")
        assert mock_client.embeddings.create.call_count == 1  # No additional call
        assert embedding1 == embedding2

