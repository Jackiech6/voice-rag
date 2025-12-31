"""Tests for LLM service."""
import pytest
from llm_service import LLMService


@pytest.fixture
def llm_service():
    """Create LLM service instance."""
    return LLMService()


def test_generate_answer_with_chunks(llm_service):
    """Test answer generation with retrieved chunks."""
    query = "What is machine learning?"
    
    retrieved_chunks = [
        {
            "id": "chunk_1",
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "metadata": {"document_title": "AI Basics", "page": 1},
            "similarity_score": 0.9
        },
        {
            "id": "chunk_2",
            "text": "There are three main types of machine learning: supervised, unsupervised, and reinforcement learning.",
            "metadata": {"document_title": "AI Basics", "page": 2},
            "similarity_score": 0.85
        }
    ]
    
    result = llm_service.generate_answer(query, retrieved_chunks)
    
    assert "answer" in result, "Result should have answer"
    assert "citations" in result, "Result should have citations"
    assert len(result["answer"]) > 0, "Answer should not be empty"
    
    # Check that answer contains citation markers
    assert "[" in result["answer"] or len(result["citations"]) > 0, "Answer should have citations"


def test_generate_answer_no_chunks(llm_service):
    """Test answer generation with no chunks."""
    query = "What is machine learning?"
    result = llm_service.generate_answer(query, [])
    
    assert "answer" in result
    assert "citations" in result
    assert len(result["citations"]) == 0
    # Should indicate that information is not available
    assert "not" in result["answer"].lower() or "couldn't" in result["answer"].lower()


def test_extract_citations(llm_service):
    """Test citation extraction."""
    answer_text = "Machine learning [1] is important. There are types [2] of ML."
    
    retrieved_chunks = [
        {
            "id": "chunk_1",
            "text": "Machine learning definition",
            "metadata": {"document_title": "Doc1", "page": 1},
            "similarity_score": 0.9
        },
        {
            "id": "chunk_2",
            "text": "Types of ML",
            "metadata": {"document_title": "Doc1", "page": 2},
            "similarity_score": 0.85
        }
    ]
    
    citations = llm_service._extract_citations(answer_text, retrieved_chunks)
    
    assert len(citations) > 0, "Should extract citations"
    assert all("id" in c for c in citations), "Citations should have IDs"
    assert all("document_title" in c for c in citations), "Citations should have document titles"

