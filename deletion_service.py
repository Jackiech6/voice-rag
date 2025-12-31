"""Document deletion service."""
from typing import Dict, Any
from database import get_db_session, Document, Chunk
from vector_store import VectorStore


class DeletionService:
    """Service for deleting documents from the RAG system."""
    
    def __init__(self):
        """Initialize deletion service."""
        self.vector_store = VectorStore()
    
    def delete_document(self, document_id: int) -> Dict[str, Any]:
        """
        Delete a document and all its chunks from the system.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Dict with deletion results:
            {
                "success": bool,
                "document_id": int,
                "title": str,
                "chunks_deleted": int,
                "message": str,
                "error": Optional[str]
            }
        """
        db_session = get_db_session()
        
        try:
            # Find document
            document = db_session.query(Document).filter_by(id=document_id).first()
            
            if not document:
                return {
                    "success": False,
                    "document_id": document_id,
                    "title": None,
                    "chunks_deleted": 0,
                    "message": f"Document with ID {document_id} not found",
                    "error": "DOCUMENT_NOT_FOUND"
                }
            
            document_title = document.title
            document_id_str = str(document_id)
            
            # Count chunks before deletion
            chunks = db_session.query(Chunk).filter_by(document_id=document_id).all()
            chunk_count = len(chunks)
            
            # Delete chunks from vector store
            try:
                vector_chunks_deleted = self.vector_store.delete_document(document_id_str)
            except Exception as e:
                # Log but don't fail - chunks might already be deleted
                print(f"Warning: Error deleting chunks from vector store: {e}")
                vector_chunks_deleted = 0
            
            # Delete chunks from database
            db_session.query(Chunk).filter_by(document_id=document_id).delete()
            
            # Delete document from database
            db_session.delete(document)
            db_session.commit()
            
            return {
                "success": True,
                "document_id": document_id,
                "title": document_title,
                "chunks_deleted": chunk_count,
                "message": f"Successfully deleted document: {document_title} ({chunk_count} chunks removed)",
                "error": None
            }
        
        except Exception as e:
            db_session.rollback()
            return {
                "success": False,
                "document_id": document_id,
                "title": None,
                "chunks_deleted": 0,
                "message": f"Error deleting document: {str(e)}",
                "error": "DELETION_ERROR"
            }
        finally:
            db_session.close()

