"""Vector database integration using ChromaDB."""
import chromadb
from chromadb.config import Settings
import config
from typing import List, Dict, Any
import uuid


class VectorStore:
    """Manages vector storage and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(
            path=config.VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add chunks to vector store.
        
        Args:
            chunks: List of dicts with keys: id, text, embedding, metadata
        """
        if not chunks:
            return
        
        ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        embeddings = [chunk["embedding"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query_embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of chunks with similarity scores
        """
        if top_k is None:
            top_k = config.TOP_K
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                chunk = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                }
                chunks.append(chunk)
        
        return chunks
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            document_id: Document ID to delete chunks for
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Get all chunks and filter by document_id
            all_results = self.collection.get()
            
            if not all_results["ids"]:
                return 0
            
            ids_to_delete = []
            for id, metadata in zip(all_results["ids"], all_results["metadatas"]):
                if metadata and metadata.get("document_id") == str(document_id):
                    ids_to_delete.append(id)
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                return len(ids_to_delete)
            
            return 0
        except Exception as e:
            print(f"Error deleting document chunks: {e}")
            raise

