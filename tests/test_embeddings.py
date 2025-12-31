"""Tests for embedding service."""
import pytest
from embeddings import EmbeddingService
import config


@pytest.fixture
def embedding_service():
    """Create embedding service instance."""
    return EmbeddingService()


def test_generate_embedding(embedding_service):
    """Test single embedding generation."""
    text = "This is a test query"
    embedding = embedding_service.generate_embedding(text)
    
    assert isinstance(embedding, list), "Embedding should be a list"
    assert len(embedding) > 0, "Embedding should have dimensions"
    assert all(isinstance(x, (int, float)) for x in embedding), "All values should be numbers"


def test_generate_embeddings_batch(embedding_service):
    """Test batch embedding generation."""
    texts = ["First text", "Second text", "Third text"]
    embeddings = embedding_service.generate_embeddings_batch(texts)
    
    assert len(embeddings) == len(texts), "Should generate one embedding per text"
    assert all(len(emb) > 0 for emb in embeddings), "All embeddings should have dimensions"
    
    # Check that embeddings are different
    assert embeddings[0] != embeddings[1], "Different texts should produce different embeddings"


def test_generate_embeddings_batch_empty(embedding_service):
    """Test batch embedding with empty list."""
    embeddings = embedding_service.generate_embeddings_batch([])
    assert embeddings == [], "Empty list should return empty list"

