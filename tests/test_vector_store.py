"""Tests for vector store."""
import pytest
import tempfile
import shutil
from vector_store import VectorStore
import config


@pytest.fixture
def temp_vector_db():
    """Create temporary vector database."""
    temp_dir = tempfile.mkdtemp()
    original_path = config.VECTOR_DB_PATH
    config.VECTOR_DB_PATH = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    config.VECTOR_DB_PATH = original_path


def test_vector_store_init(temp_vector_db):
    """Test vector store initialization."""
    store = VectorStore()
    assert store.client is not None
    assert store.collection is not None


def test_add_and_search_chunks(temp_vector_db):
    """Test adding chunks and searching."""
    store = VectorStore()
    
    # Create test chunks with embeddings
    # Using simple test embeddings (1536 dims for text-embedding-3-small)
    test_embedding = [0.1] * 1536
    test_embedding2 = [0.2] * 1536
    
    chunks = [
        {
            "id": "test_chunk_1",
            "text": "This is about machine learning",
            "embedding": test_embedding,
            "metadata": {"document_title": "Test Doc", "page": 1}
        },
        {
            "id": "test_chunk_2",
            "text": "This is about natural language processing",
            "embedding": test_embedding2,
            "metadata": {"document_title": "Test Doc", "page": 2}
        }
    ]
    
    store.add_chunks(chunks)
    
    # Search with first embedding
    results = store.search(test_embedding, top_k=2)
    
    assert len(results) > 0, "Should return search results"
    assert all("id" in r for r in results), "Results should have IDs"
    assert all("text" in r for r in results), "Results should have text"
    assert all("metadata" in r for r in results), "Results should have metadata"
    assert all("similarity_score" in r for r in results), "Results should have similarity scores"

