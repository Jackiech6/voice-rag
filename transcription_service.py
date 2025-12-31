"""Transcription service using OpenAI Whisper API."""
from openai import OpenAI
import config
from typing import Optional
import io


class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in .env file.")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "whisper-1"  # OpenAI Whisper model
    
    def transcribe_audio(
        self,
        audio_file: bytes,
        language: Optional[str] = "en"
    ) -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Audio file bytes
            language: Language code (default: "en")
            
        Returns:
            Dict with transcript, confidence, and language
        """
        try:
            # Create a file-like object from bytes
            audio_file_obj = io.BytesIO(audio_file)
            audio_file_obj.name = "audio.webm"  # Set filename for OpenAI API
            
            # Call Whisper API
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file_obj,
                language=language if language else None
            )
            
            return {
                "transcript": transcript.text,
                "confidence": None,  # Whisper API doesn't return confidence scores
                "language": language or "en"
            }
        
        except Exception as e:
            raise ValueError(f"Transcription failed: {str(e)}")

