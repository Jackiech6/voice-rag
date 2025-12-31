"""CLI tool for document ingestion."""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from database import get_db_session, Document, Chunk, init_db
from document_processor import DocumentProcessor
from embeddings import EmbeddingService
from vector_store import VectorStore


def ingest_document(file_path: str) -> None:
    """
    Ingest a document into the system.
    
    Args:
        file_path: Path to document file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Initialize components
    processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    db_session = get_db_session()
    
    try:
        # Check if document already exists (idempotency)
        file_hash = processor.calculate_file_hash(str(file_path))
        existing_doc = db_session.query(Document).filter_by(file_hash=file_hash).first()
        
        if existing_doc:
            print(f"Document already ingested: {existing_doc.title}")
            print(f"  Document ID: {existing_doc.id}")
            print(f"  Skipping ingestion (idempotent)")
            db_session.close()
            return
        
        # Process document
        print(f"Processing document: {file_path.name}")
        
        if file_path.suffix.lower() == '.pdf':
            document_data = processor.process_pdf(str(file_path))
        elif file_path.suffix.lower() in ['.txt', '.md']:
            document_data = processor.process_text_file(str(file_path))
        else:
            print(f"Error: Unsupported file type: {file_path.suffix}")
            sys.exit(1)
        
        print(f"  Title: {document_data['title']}")
        print(f"  Pages: {document_data['total_pages']}")
        
        # Create chunks
        print("Creating chunks...")
        chunks = processor.create_chunks(document_data, document_id=0)  # Will update after DB insert
        print(f"  Created {len(chunks)} chunks")
        
        # Save document to database
        doc = Document(
            title=document_data["title"],
            file_path=str(file_path.absolute()),
            file_hash=file_hash,
            created_at=datetime.now().isoformat()
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        
        document_id = doc.id
        print(f"  Document ID: {document_id}")
        
        # Update chunks with document_id and generate embeddings
        print("Generating embeddings...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
        
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
        print("Indexing in vector database...")
        vector_store.add_chunks(vector_chunks)
        
        print(f"\n✅ Successfully ingested document: {document_data['title']}")
        print(f"   Document ID: {document_id}")
        print(f"   Chunks: {len(chunks)}")
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG system")
    parser.add_argument("file_path", help="Path to document file (PDF or TXT)")
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    # Ingest document
    ingest_document(args.file_path)


if __name__ == "__main__":
    main()

