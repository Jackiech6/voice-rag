"""Embedding generation using OpenAI."""
from openai import OpenAI
import config
from typing import List, Optional
from cache import EmbeddingCache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class EmbeddingService:
    """Handles embedding generation."""
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize OpenAI client.
        
        Args:
            use_cache: Whether to use embedding cache
        """
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in Railway Variables (Settings → Variables) or in your .env file for local development.")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.EMBEDDING_MODEL
        self.cache = EmbeddingCache() if use_cache else None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, Exception)),
        reraise=True
    )
    def _generate_embedding_with_retry(self, text: str) -> List[float]:
        """Internal method with retry logic for generating embeddings."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(text)
            if cached is not None:
                return cached
        
        # Generate new embedding with retry logic and error handling
        try:
            embedding = self._generate_embedding_with_retry(text)
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower() or isinstance(e, ConnectionError):
                raise ConnectionError(f"Failed to connect to OpenAI API after retries: {error_msg}. Please check your internet connection and API key.")
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise ValueError(f"OpenAI API authentication failed: {error_msg}. Please check your OPENAI_API_KEY.")
            elif "rate limit" in error_msg.lower():
                raise ValueError(f"OpenAI API rate limit exceeded: {error_msg}. Please try again in a moment.")
            else:
                raise ValueError(f"OpenAI API error: {error_msg}")
        
        # Cache the result
        if self.cache:
            self.cache.set(text, embedding)
        
        return embedding
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, Exception)),
        reraise=True
    )
    def _generate_embeddings_batch_with_retry(self, texts: List[str]) -> List[List[float]]:
        """Internal method with retry logic for generating batch embeddings."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            return self._generate_embeddings_batch_with_retry(texts)
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower() or isinstance(e, ConnectionError):
                raise ConnectionError(f"Failed to connect to OpenAI API after retries: {error_msg}. Please check your internet connection and API key.")
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise ValueError(f"OpenAI API authentication failed: {error_msg}. Please check your OPENAI_API_KEY.")
            elif "rate limit" in error_msg.lower():
                raise ValueError(f"OpenAI API rate limit exceeded: {error_msg}. Please try again in a moment.")
            else:
                raise ValueError(f"OpenAI API error: {error_msg}")

