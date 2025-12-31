"""Tests for document processor."""
import pytest
import tempfile
import os
from pathlib import Path
from document_processor import DocumentProcessor


def test_chunk_text():
    """Test text chunking functionality."""
    processor = DocumentProcessor()
    
    # Create a long text
    long_text = " ".join(["word"] * 1000)
    
    chunks = processor.chunk_text(long_text, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) > 1, "Should create multiple chunks for long text"
    assert all(len(chunk) > 0 for chunk in chunks), "All chunks should have content"


def test_chunk_text_short():
    """Test chunking with short text."""
    processor = DocumentProcessor()
    
    short_text = "This is a short text."
    chunks = processor.chunk_text(short_text, chunk_size=100)
    
    assert len(chunks) == 1, "Short text should create single chunk"
    assert chunks[0] == short_text


def test_process_text_file():
    """Test processing a text file."""
    processor = DocumentProcessor()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\nIt has multiple lines.")
        temp_path = f.name
    
    try:
        result = processor.process_text_file(temp_path)
        
        # Title should be extracted from content or fallback to filename
        assert result["title"] in ["This is a test document.", Path(temp_path).stem]
        assert result["total_pages"] == 1
        assert len(result["pages"]) == 1
        assert "test document" in result["pages"][0]["text"]
    finally:
        os.unlink(temp_path)


def test_calculate_file_hash():
    """Test file hash calculation."""
    processor = DocumentProcessor()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        hash1 = processor.calculate_file_hash(temp_path)
        hash2 = processor.calculate_file_hash(temp_path)
        
        assert hash1 == hash2, "Same file should produce same hash"
        assert len(hash1) == 64, "SHA256 hash should be 64 characters"
    finally:
        os.unlink(temp_path)


def test_create_chunks():
    """Test chunk creation from document data."""
    processor = DocumentProcessor()
    
    document_data = {
        "title": "Test Document",
        "pages": [
            {"page_number": 1, "text": "This is page one. " * 50},
            {"page_number": 2, "text": "This is page two. " * 50}
        ],
        "total_pages": 2
    }
    
    chunks = processor.create_chunks(document_data, document_id=1)
    
    assert len(chunks) > 0, "Should create chunks"
    assert all("chunk_index" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)
    
    # Check metadata
    first_chunk = chunks[0]
    assert first_chunk["metadata"]["document_id"] == "1"
    assert first_chunk["metadata"]["document_title"] == "Test Document"
    assert first_chunk["metadata"]["page"] == 1

