"""Integration tests for the complete RAG pipeline."""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from database import init_db, get_db_session, Document
from document_processor import DocumentProcessor
from embeddings import EmbeddingService
from vector_store import VectorStore
from llm_service import LLMService
import config


@pytest.fixture
def temp_environment():
    """Set up temporary environment for testing."""
    # Create temp directories
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    temp_vector = tempfile.mkdtemp()
    
    # Save original config
    original_db = config.DATABASE_PATH
    original_vector = config.VECTOR_DB_PATH
    
    # Set temp paths
    config.DATABASE_PATH = temp_db.name
    config.VECTOR_DB_PATH = temp_vector
    
    # Initialize
    init_db()
    
    yield
    
    # Cleanup
    os.unlink(temp_db.name)
    shutil.rmtree(temp_vector)
    config.DATABASE_PATH = original_db
    config.VECTOR_DB_PATH = original_vector


def test_end_to_end_ingestion_and_query(temp_environment):
    """Test complete flow: ingest document and query it."""
    # Create a test document
    test_doc_path = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    test_doc_path.write("""
    Machine Learning Basics
    
    Machine learning is a subset of artificial intelligence that enables 
    systems to learn and improve from experience without being explicitly 
    programmed. There are three main types:
    
    1. Supervised Learning: Uses labeled data to train models
    2. Unsupervised Learning: Finds patterns in unlabeled data
    3. Reinforcement Learning: Learns through trial and error with rewards
    
    Deep learning is a subset of machine learning that uses neural networks 
    with multiple layers to learn complex patterns in data.
    """)
    test_doc_path.close()
    
    try:
        # Process document
        processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        db_session = get_db_session()
        
        # Process
        doc_data = processor.process_text_file(test_doc_path.name)
        chunks = processor.create_chunks(doc_data, document_id=1)
        
        # Save to DB
        doc = Document(
            title=doc_data["title"],
            file_path=test_doc_path.name,
            file_hash=processor.calculate_file_hash(test_doc_path.name),
            created_at="2024-01-01T00:00:00"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        
        # Generate embeddings and add to vector store
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
        
        vector_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"doc_{doc.id}_chunk_{chunk['chunk_index']}"
            vector_chunks.append({
                "id": chunk_id,
                "text": chunk["text"],
                "embedding": embeddings[i],
                "metadata": chunk["metadata"]
            })
        
        vector_store.add_chunks(vector_chunks)
        
        # Query
        query = "What is machine learning?"
        query_embedding = embedding_service.generate_embedding(query)
        retrieved = vector_store.search(query_embedding, top_k=3)
        
        assert len(retrieved) > 0, "Should retrieve relevant chunks"
        
        # Generate answer
        llm_service = LLMService()
        result = llm_service.generate_answer(query, retrieved)
        
        assert "answer" in result
        assert len(result["answer"]) > 0
        assert "machine learning" in result["answer"].lower() or "ML" in result["answer"]
        
        db_session.close()
        
    finally:
        os.unlink(test_doc_path.name)

