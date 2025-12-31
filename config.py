"""Configuration settings for the Voice to RAG system."""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Note: API key validation happens when services are initialized, not here

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval Configuration
TOP_K = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score for retrieval

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "metadata.db")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "chroma_db")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

