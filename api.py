"""FastAPI server for the RAG system."""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import os
from embeddings import EmbeddingService
from vector_store import VectorStore
from llm_service import LLMService
from transcription_service import TranscriptionService
from ingestion_service import IngestionService
from deletion_service import DeletionService
from database import init_db
import config
import tempfile
import shutil
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="Voice to RAG API", version="1.0.0")

# CORS middleware
# In production, replace "*" with your actual domain(s)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize services
embedding_service = EmbeddingService()
vector_store = VectorStore()
llm_service = LLMService()
transcription_service = TranscriptionService()
ingestion_service = IngestionService()
deletion_service = DeletionService()

# Initialize database
init_db()


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    text: str


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    citations: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    latency_ms: float


class TranscribeResponse(BaseModel):
    """Response model for transcribe endpoint."""
    transcript: str
    confidence: Optional[float] = None
    language: str = "en"


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint."""
    success: bool
    document_id: Optional[int] = None
    title: Optional[str] = None
    chunks_created: int = 0
    message: str
    error: Optional[str] = None
    already_exists: bool = False


class DocumentInfo(BaseModel):
    """Document information model."""
    id: int
    title: str
    file_name: str  # Just the filename, not full path
    file_path: str
    file_type: str  # pdf, txt, md
    file_size: Optional[int] = None  # In bytes
    chunks_count: int = 0
    created_at: str


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion."""
    success: bool
    document_id: int
    title: Optional[str] = None
    chunks_deleted: int = 0
    message: str
    error: Optional[str] = None


class DocumentsListResponse(BaseModel):
    """Response model for documents list endpoint."""
    documents: List[DocumentInfo]
    total: int


@app.get("/")
async def root():
    """Root endpoint - serve index.html."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            path=index_path,
            media_type="text/html"
        )
    
    # Fallback if static files not found
    return {
        "message": "Voice to RAG API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/query",
            "transcribe": "/transcribe",
            "documents": {
                "upload": "/documents/upload",
                "list": "/documents",
                "delete": "/documents/{document_id}"
            },
            "health": "/health",
            "ui": "/static/index.html"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe audio file to text using OpenAI Whisper API.
    
    Accepts audio files in various formats (webm, mp3, wav, etc.)
    Returns transcribed text with language detection.
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()
        
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        # Transcribe audio
        result = transcription_service.transcribe_audio(audio_bytes)
        
        return TranscribeResponse(
            transcript=result["transcript"],
            confidence=result.get("confidence"),
            language=result.get("language", "en")
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a text query and return a grounded answer with citations.
    
    Flow:
    1. Generate query embedding
    2. Retrieve top-k chunks
    3. Generate answer with citations
    """
    start_time = time.time()
    
    query_text = request.text.strip() if request.text else ""
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty")
    
    try:
        # Step 1: Generate query embedding
        try:
            query_embedding = embedding_service.generate_embedding(query_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embedding: {str(e)}. Please check your OpenAI API key and connection."
            )
        
        # Step 2: Retrieve top-k chunks
        try:
            retrieved_chunks = vector_store.search(query_embedding)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve documents: {str(e)}. Please check the vector database."
            )
        
        if not retrieved_chunks:
            return QueryResponse(
                answer="I couldn't find any relevant information in the documents to answer your question. Please try rephrasing your query or check if relevant documents have been ingested.",
                citations=[],
                retrieved_chunks=[],
                latency_ms=(time.time() - start_time) * 1000
            )
        
        # Filter chunks by similarity threshold
        filtered_chunks = [
            chunk for chunk in retrieved_chunks
            if chunk.get("similarity_score", 0) >= config.SIMILARITY_THRESHOLD
        ]
        
        if not filtered_chunks:
            return QueryResponse(
                answer=f"I found some information, but the relevance is low (similarity < {config.SIMILARITY_THRESHOLD * 100}%). Please try rephrasing your question or check if more relevant documents are available.",
                citations=[],
                retrieved_chunks=retrieved_chunks,
                latency_ms=(time.time() - start_time) * 1000
            )
        
        # Step 3: Generate answer with citations
        try:
            result = llm_service.generate_answer(query_text, filtered_chunks)
        except Exception as e:
            # If LLM fails, return retrieved chunks with error message
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate answer: {str(e)}. Retrieved passages are available but answer generation failed. Please check your OpenAI API key and try again."
            )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=result["answer"],
            citations=result["citations"],
            retrieved_chunks=retrieved_chunks,
            latency_ms=latency_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing query: {str(e)}")


@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None
):
    """
    Upload and ingest a document into the RAG system.
    
    Accepts PDF, TXT, and MD files.
    Returns ingestion status and document information.
    """
    # File validation
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    file_extension = Path(file.filename).suffix.lower() if file.filename else ""
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Supported types: PDF, TXT, MD"
        )
    
    # Create temporary file
    temp_path = None
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Create temporary file with proper extension
        suffix = file_extension
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
        
        try:
            # Write file content
            with os.fdopen(temp_fd, 'wb') as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Ensure data is written to disk
        except Exception as e:
            # Clean up if write fails
            if temp_path and Path(temp_path).exists():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Error writing temporary file: {str(e)}")
        
        # Verify file was created and is readable
        if not Path(temp_path).exists():
            raise HTTPException(status_code=500, detail="Temporary file was not created")
        
        # Verify file has content
        if Path(temp_path).stat().st_size == 0:
            if Path(temp_path).exists():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Ingest document (file is guaranteed to exist at this point)
        # Use original filename if no custom title provided
        original_filename = file.filename if file.filename else None
        if not title and original_filename:
            # Use filename without extension as title
            title = Path(original_filename).stem
        
        try:
            result = ingestion_service.ingest_document(temp_path, custom_title=title, original_filename=original_filename)
        except Exception as e:
            # Clean up temp file on ingestion error
            if temp_path and Path(temp_path).exists():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,
                detail=f"Error ingesting document: {str(e)}. Please ensure the file is a valid PDF, TXT, or MD file."
            )
        
        if not result["success"]:
            # Determine appropriate status code
            if result["error"] in ["FILE_NOT_FOUND", "UNSUPPORTED_FILE_TYPE"]:
                status_code = 400
            elif result["error"] == "PROCESSING_ERROR":
                status_code = 400  # Bad file format
            else:
                status_code = 500
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return DocumentUploadResponse(
            success=True,
            document_id=result["document_id"],
            title=result["title"],
            chunks_created=result["chunks_created"],
            message=result["message"],
            error=None,
            already_exists=result.get("already_exists", False)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
            except Exception as cleanup_error:
                # Log but don't fail on cleanup errors
                print(f"Warning: Could not delete temporary file {temp_path}: {cleanup_error}")


@app.get("/documents", response_model=DocumentsListResponse)
async def list_documents():
    """
    List all ingested documents with informative metadata.
    
    Returns list of documents with file names, types, sizes, and chunk counts.
    """
    try:
        from database import get_db_session, Document, Chunk
        import os
        
        db_session = get_db_session()
        try:
            documents = db_session.query(Document).order_by(Document.created_at.desc()).all()
            
            doc_list = []
            for doc in documents:
                # Get file information
                file_path_obj = Path(doc.file_path)
                file_name = file_path_obj.name
                file_type = file_path_obj.suffix.lower().lstrip('.') or 'unknown'
                
                # Get file size if file exists
                file_size = None
                if file_path_obj.exists():
                    try:
                        file_size = file_path_obj.stat().st_size
                    except:
                        pass
                
                # Count chunks for this document
                chunks_count = db_session.query(Chunk).filter_by(document_id=doc.id).count()
                
                doc_list.append(
                    DocumentInfo(
                        id=doc.id,
                        title=doc.title,
                        file_name=file_name,
                        file_path=doc.file_path,
                        file_type=file_type,
                        file_size=file_size,
                        chunks_count=chunks_count,
                        created_at=doc.created_at
                    )
                )
            
            return DocumentsListResponse(
                documents=doc_list,
                total=len(doc_list)
            )
        finally:
            db_session.close()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@app.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: int):
    """
    Delete a document and all its chunks from the RAG system.
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Deletion status and information
    """
    try:
        result = deletion_service.delete_document(document_id)
        
        if not result["success"]:
            status_code = 404 if result["error"] == "DOCUMENT_NOT_FOUND" else 500
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return DocumentDeleteResponse(
            success=True,
            document_id=result["document_id"],
            title=result["title"],
            chunks_deleted=result["chunks_deleted"],
            message=result["message"],
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
