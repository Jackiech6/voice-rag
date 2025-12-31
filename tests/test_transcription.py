"""Tests for transcription service."""
import pytest
from unittest.mock import patch, MagicMock, Mock
import io


@patch('transcription_service.OpenAI')
def test_transcription_service_init(mock_openai_class):
    """Test transcription service initialization."""
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    from transcription_service import TranscriptionService
    service = TranscriptionService()
    
    assert service.client is not None
    assert service.model == "whisper-1"


@patch('transcription_service.OpenAI')
def test_transcribe_audio_success(mock_openai_class):
    """Test successful audio transcription."""
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # Mock transcription response
    mock_transcription = MagicMock()
    mock_transcription.text = "This is a test transcription"
    mock_client.audio.transcriptions.create.return_value = mock_transcription
    
    from transcription_service import TranscriptionService
    service = TranscriptionService()
    audio_bytes = b"fake audio data"
    
    result = service.transcribe_audio(audio_bytes, language="en")
    
    assert result["transcript"] == "This is a test transcription"
    assert result["language"] == "en"
    mock_client.audio.transcriptions.create.assert_called_once()


@patch('transcription_service.OpenAI')
def test_transcribe_audio_error(mock_openai_class):
    """Test transcription error handling."""
    # Mock OpenAI client to raise error
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
    
    from transcription_service import TranscriptionService
    service = TranscriptionService()
    audio_bytes = b"fake audio data"
    
    with pytest.raises(ValueError, match="Transcription failed"):
        service.transcribe_audio(audio_bytes)


@patch('transcription_service.OpenAI')
def test_transcribe_audio_empty(mock_openai_class):
    """Test transcription with empty audio."""
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.audio.transcriptions.create.side_effect = Exception("Empty file")
    
    from transcription_service import TranscriptionService
    service = TranscriptionService()
    
    with pytest.raises(ValueError):
        service.transcribe_audio(b"", language="en")

