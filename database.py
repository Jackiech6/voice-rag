"""SQLite database for metadata storage."""
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import config

Base = declarative_base()


class Document(Base):
    """Document metadata table."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    file_path = Column(String, unique=True, nullable=False)
    file_hash = Column(String)  # For idempotency
    created_at = Column(String)  # ISO format timestamp


class Chunk(Base):
    """Chunk metadata table."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    metadata_json = Column(JSON)  # Store page, section, etc.


def get_db_session():
    """Create database session."""
    engine = create_engine(f"sqlite:///{config.DATABASE_PATH}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize database tables."""
    engine = create_engine(f"sqlite:///{config.DATABASE_PATH}", echo=False)
    Base.metadata.create_all(engine)

