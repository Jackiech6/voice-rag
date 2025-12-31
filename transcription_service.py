"""Transcription service using OpenAI Whisper API."""
from openai import OpenAI, APIConnectionError, APITimeoutError, APIError
import config
from typing import Optional
import io


class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in Railway Variables (Settings → Variables) or in your .env file for local development.")
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
        
        except (APIConnectionError, APITimeoutError) as e:
            raise ConnectionError(f"Failed to connect to OpenAI API: {str(e)}. Please check your internet connection and API key.")
        except APIError as e:
            error_msg = str(e)
            if "api key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                raise ValueError(f"OpenAI API authentication failed: {error_msg}. Please check your OPENAI_API_KEY.")
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                raise ValueError(f"OpenAI API rate limit exceeded: {error_msg}. Please try again in a moment.")
            else:
                raise ValueError(f"OpenAI API error: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                raise ConnectionError(f"Failed to connect to OpenAI API: {error_msg}. Please check your internet connection and API key.")
            else:
                raise ValueError(f"Transcription failed: {error_msg}")

