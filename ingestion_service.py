"""Document ingestion service for API use."""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import os
from database import get_db_session, Document, Chunk
from document_processor import DocumentProcessor
from embeddings import EmbeddingService
from vector_store import VectorStore


class IngestionService:
    """Service for ingesting documents into the RAG system."""
    
    def __init__(self):
        """Initialize ingestion service."""
        self.processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    def ingest_document(
        self,
        file_path: str,
        custom_title: Optional[str] = None,
        original_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document into the system.
        
        Args:
            file_path: Path to document file
            custom_title: Optional custom title for the document
            
        Returns:
            Dict with ingestion results:
            {
                "success": bool,
                "document_id": int,
                "title": str,
                "chunks_created": int,
                "message": str,
                "error": Optional[str]
            }
        """
        # Convert to Path object but keep original string for processing
        file_path_obj = Path(file_path)
        file_path_str = str(file_path_obj.absolute())  # Use absolute path
        db_session = get_db_session()
        
        try:
            # Validate file exists
            if not file_path_obj.exists():
                return {
                    "success": False,
                    "document_id": None,
                    "title": None,
                    "chunks_created": 0,
                    "message": f"File not found: {file_path_str}",
                    "error": "FILE_NOT_FOUND"
                }
            
            # Verify file is readable
            if not os.access(file_path_str, os.R_OK):
                return {
                    "success": False,
                    "document_id": None,
                    "title": None,
                    "chunks_created": 0,
                    "message": f"File is not readable: {file_path_str}",
                    "error": "FILE_NOT_READABLE"
                }
            
            # Check if document already exists (idempotency)
            file_hash = self.processor.calculate_file_hash(file_path_str)
            existing_doc = db_session.query(Document).filter_by(file_hash=file_hash).first()
            
            if existing_doc:
                return {
                    "success": True,
                    "document_id": existing_doc.id,
                    "title": existing_doc.title,
                    "chunks_created": 0,
                    "message": f"Document already ingested (ID: {existing_doc.id})",
                    "error": None,
                    "already_exists": True
                }
            
            # Validate file type
            if file_path_obj.suffix.lower() not in ['.pdf', '.txt', '.md']:
                return {
                    "success": False,
                    "document_id": None,
                    "title": None,
                    "chunks_created": 0,
                    "message": f"Unsupported file type: {file_path.suffix}. Supported: PDF, TXT, MD",
                    "error": "UNSUPPORTED_FILE_TYPE"
                }
            
            # Process document
            try:
                if file_path_obj.suffix.lower() == '.pdf':
                    document_data = self.processor.process_pdf(file_path_str)
                else:
                    document_data = self.processor.process_text_file(file_path_str)
            except Exception as e:
                return {
                    "success": False,
                    "document_id": None,
                    "title": None,
                    "chunks_created": 0,
                    "message": f"Error processing document: {str(e)}. The file may be corrupted or in an unsupported format.",
                    "error": "PROCESSING_ERROR"
                }
            
            # Determine document title
            if custom_title:
                # Use provided custom title
                document_data["title"] = custom_title
            elif original_filename:
                # Use original filename (without extension) as title
                document_data["title"] = Path(original_filename).stem
            else:
                # Try to extract title from content, fallback to filename
                extracted_title = self.processor.extract_title_from_content(document_data)
                if extracted_title:
                    document_data["title"] = extracted_title
                else:
                    # Fallback to filename stem
                    document_data["title"] = file_path_obj.stem
            
            # Create chunks
            chunks = self.processor.create_chunks(document_data, document_id=0)
            
            # Save document to database
            doc = Document(
                title=document_data["title"],
                file_path=file_path_str,
                file_hash=file_hash,
                created_at=datetime.now().isoformat()
            )
            db_session.add(doc)
            db_session.commit()
            db_session.refresh(doc)
            
            document_id = doc.id
            
            # Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings_batch(chunk_texts)
            
            # Prepare chunks for vector store
            vector_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"doc_{document_id}_chunk_{chunk['chunk_index']}"
                chunk["id"] = chunk_id
                chunk["embedding"] = embeddings[i]
                chunk["metadata"]["document_id"] = str(document_id)
                
                vector_chunks.append({
                    "id": chunk_id,
                    "text": chunk["text"],
                    "embedding": chunk["embedding"],
                    "metadata": chunk["metadata"]
                })
                
                # Save chunk metadata to database
                db_chunk = Chunk(
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    metadata_json=chunk["metadata"]
                )
                db_session.add(db_chunk)
            
            db_session.commit()
            
            # Add to vector store
            self.vector_store.add_chunks(vector_chunks)
            
            return {
                "success": True,
                "document_id": document_id,
                "title": document_data["title"],
                "chunks_created": len(chunks),
                "message": f"Successfully ingested document: {document_data['title']}",
                "error": None,
                "already_exists": False
            }
        
        except Exception as e:
            db_session.rollback()
            return {
                "success": False,
                "document_id": None,
                "title": None,
                "chunks_created": 0,
                "message": f"Error during ingestion: {str(e)}",
                "error": "INGESTION_ERROR"
            }
        finally:
            db_session.close()

