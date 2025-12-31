# Voice to RAG System - Phase 1

A Retrieval-Augmented Generation (RAG) system that answers questions based on ingested documents with citations.

## Phase 1 & 2: Core RAG Pipeline with Voice Integration

This implementation includes:
- Document ingestion (CLI tool)
- Vector-based retrieval
- Answer generation with citations
- **Voice recording and transcription (Phase 2)**
- Web interface with voice and text input

**Status**: ✅ Phase 1 & 2 Complete

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (for embeddings, LLM, and future transcription)

## Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd WRDS
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Usage

### 1. Ingest Documents

#### Option A: Web Interface (Recommended)
1. Start the server: `python api.py`
2. Open `http://localhost:8000/static/index.html`
3. Use the "Upload Documents" section
4. Click to upload or drag and drop PDF/TXT/MD files
5. View uploaded documents in the list below

#### Option B: CLI Tool
Use the CLI tool to ingest PDF or text files:

```bash
python ingest.py path/to/document.pdf
python ingest.py path/to/document.txt
```

The tool will:
- Extract text from the document
- Create chunks with metadata
- Generate embeddings
- Store in vector database and metadata store

**Example:**
```bash
python ingest.py sample_document.pdf
```

### 2. Start the API Server

```bash
python api.py
```

Or using uvicorn directly:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 3. Use the Web Interface

Open your browser and navigate to:
```
http://localhost:8000/static/index.html
```

Or access the API directly:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 4. Query the System

**Via Web Interface:**
1. Type your question in the text input
2. Click "Submit"
3. View the answer with citations and retrieved passages

**Via API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is machine learning?"}'
```

## API Endpoints

### `POST /query`
Process a text query and return a grounded answer with citations.

**Request:**
```json
{
  "text": "Your question here"
}
```

**Response:**
```json
{
  "answer": "Answer text with citations [1], [2]...",
  "citations": [
    {
      "id": "chunk_id",
      "document_title": "Document Name",
      "page": 1,
      "text": "Cited passage...",
      "similarity_score": 0.85
    }
  ],
  "retrieved_chunks": [...],
  "latency_ms": 1234.5
}
```

### `GET /health`
Health check endpoint.

### `POST /transcribe`
Transcribe audio file to text using OpenAI Whisper API.

**Request**: Multipart form data with audio file
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "audio=@recording.webm"
```

**Response**:
```json
{
  "transcript": "Transcribed text here",
  "confidence": null,
  "language": "en"
}
```

### `POST /documents/upload`
Upload and ingest a document into the RAG system.

**Request**: Multipart form data with document file
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "success": true,
  "document_id": 1,
  "title": "document",
  "chunks_created": 5,
  "message": "Successfully ingested document: document",
  "error": null,
  "already_exists": false
}
```

**Supported formats**: PDF, TXT, MD  
**Maximum file size**: 50MB

### `GET /documents`
List all ingested documents with detailed metadata.

**Response**:
```json
{
  "documents": [
    {
      "id": 1,
      "title": "document",
      "file_name": "document.pdf",
      "file_path": "/path/to/document.pdf",
      "file_type": "pdf",
      "file_size": 102400,
      "chunks_count": 5,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

### `DELETE /documents/{document_id}`
Delete a document and all its chunks from the RAG system.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/documents/1"
```

**Response**:
```json
{
  "success": true,
  "document_id": 1,
  "title": "document",
  "chunks_deleted": 5,
  "message": "Successfully deleted document: document (5 chunks removed)",
  "error": null
}
```

## Testing

Run the test suite:

```bash
pytest
```

**Current Status**: 41 tests passing ✅

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_document_processor.py
```

Run demo script (requires server running):
```bash
python demo_script.py
```

## Project Structure

```
WRDS/
├── api.py                 # FastAPI server
├── config.py             # Configuration
├── database.py            # SQLite metadata store
├── document_processor.py  # Document processing and chunking
├── embeddings.py          # Embedding generation
├── llm_service.py         # Answer generation with citations
├── vector_store.py        # Vector database integration
├── transcription_service.py # Audio transcription
├── ingestion_service.py   # Document ingestion service
├── cache.py              # Embedding cache
├── ingest.py              # CLI ingestion tool
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── static/
│   └── index.html        # Web interface
└── tests/
    ├── test_api.py
    ├── test_api_transcription.py
    ├── test_document_processor.py
    ├── test_embeddings.py
    ├── test_llm_service.py
    ├── test_vector_store.py
    ├── test_transcription.py
    ├── test_voice_integration.py
    ├── test_error_handling.py
    ├── test_citation_display.py
    ├── test_document_upload.py
    └── test_integration.py
```

## Configuration

Edit `config.py` or set environment variables:

- `OPENAI_API_KEY`: Required - Your OpenAI API key
- `EMBEDDING_MODEL`: Default `text-embedding-3-small`
- `LLM_MODEL`: Default `gpt-4` (can use `gpt-3.5-turbo` for faster/cheaper)
- `CHUNK_SIZE`: Default `500` tokens
- `CHUNK_OVERLAP`: Default `100` tokens
- `TOP_K`: Default `5` retrieved chunks

## Troubleshooting

### "OPENAI_API_KEY environment variable is required"
- Make sure you've created `.env` file with your API key
- Check that `python-dotenv` is installed

### "No module named 'fitz'"
- PyMuPDF package name is `pymupdf` but imports as `fitz`
- Reinstall: `pip install pymupdf`

### No results from queries
- Make sure documents have been ingested: `python ingest.py <file>`
- Check that vector database files exist in `chroma_db/`
- Verify documents contain relevant content

### API connection errors
- Ensure the server is running: `python api.py`
- Check the port (default 8000) is not in use
- Verify CORS settings if accessing from different origin

## Phase 2 & 3 Complete ✅

### Phase 2: Voice Integration
- ✅ Voice recording and transcription
- ✅ Transcript editing UI
- ✅ Integration of voice pipeline with RAG system
- ✅ Error handling and graceful degradation

### Phase 3: Essential Polish
- ✅ Interactive citation display with modals
- ✅ Performance optimizations (embedding cache)
- ✅ Comprehensive error handling
- ✅ Enhanced UI/UX

See `PHASE2_VALIDATION.md` and `PHASE3_VALIDATION.md` for complete validation reports.

## License

This project is for internal use.

