"""End-to-end integration tests for voice pipeline."""
import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, MagicMock
import tempfile
import os
from database import init_db, get_db_session, Document
from document_processor import DocumentProcessor
from embeddings import EmbeddingService
from vector_store import VectorStore
import config


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


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
    import shutil
    shutil.rmtree(temp_vector)
    config.DATABASE_PATH = original_db
    config.VECTOR_DB_PATH = original_vector


def test_voice_to_answer_flow(client, temp_environment):
    """Test complete flow: voice -> transcription -> query -> answer."""
    # Step 1: Ingest a test document
    test_doc_path = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    test_doc_path.write("Machine learning is a subset of artificial intelligence.")
    test_doc_path.close()
    
    try:
        processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        db_session = get_db_session()
        
        doc_data = processor.process_text_file(test_doc_path.name)
        chunks = processor.create_chunks(doc_data, document_id=1)
        
        doc = Document(
            title=doc_data["title"],
            file_path=test_doc_path.name,
            file_hash=processor.calculate_file_hash(test_doc_path.name),
            created_at="2024-01-01T00:00:00"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        
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
        db_session.close()
        
        # Step 2: Mock transcription
        with patch('api.transcription_service') as mock_transcription:
            mock_transcription.transcribe_audio.return_value = {
                "transcript": "What is machine learning?",
                "confidence": None,
                "language": "en"
            }
            
            # Simulate voice transcription
            audio_content = b"fake audio data"
            transcribe_response = client.post(
                "/transcribe",
                files={"audio": ("test.webm", audio_content, "audio/webm")}
            )
            
            assert transcribe_response.status_code == 200
            transcript_data = transcribe_response.json()
            assert "transcript" in transcript_data
            query_text = transcript_data["transcript"]
            
            # Step 3: Query with transcribed text
            query_response = client.post(
                "/query",
                json={"text": query_text}
            )
            
            assert query_response.status_code == 200
            query_data = query_response.json()
            assert "answer" in query_data
            assert "citations" in query_data
            assert len(query_data["answer"]) > 0
            
    finally:
        os.unlink(test_doc_path.name)


def test_voice_error_handling(client):
    """Test error handling in voice pipeline."""
    # Test transcription error
    with patch('api.transcription_service') as mock_transcription:
        mock_transcription.transcribe_audio.side_effect = ValueError("Transcription failed")
        
        audio_content = b"fake audio data"
        response = client.post(
            "/transcribe",
            files={"audio": ("test.webm", audio_content, "audio/webm")}
        )
        
        assert response.status_code == 400
        assert "Transcription failed" in response.json()["detail"]

