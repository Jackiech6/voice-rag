"""Simple in-memory cache for query embeddings."""
from typing import Dict, Optional
import hashlib
import time


class EmbeddingCache:
    """Simple LRU-style cache for query embeddings."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live in seconds (default 1 hour)
        """
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query text."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[list]:
        """
        Get cached embedding for query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector or None if not found/expired
        """
        key = self._hash_query(query)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            del self.cache[key]
            return None
        
        return entry["embedding"]
    
    def set(self, query: str, embedding: list) -> None:
        """
        Cache embedding for query.
        
        Args:
            query: Query text
            embedding: Embedding vector
        """
        key = self._hash_query(query)
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest entry (simple approach: remove first)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "embedding": embedding,
            "timestamp": time.time()
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

