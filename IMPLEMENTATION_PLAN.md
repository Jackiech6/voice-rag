# Voice to RAG System - Implementation Plan (Core Flow Focus)

## Overview

This document outlines a streamlined implementation plan focused exclusively on the core end-to-end flow: **voice input → transcription → retrieval → grounded answer with citations**. All non-essential features are stubbed or removed to enable rapid prototyping and iteration.

---

## Phase 1: Core RAG Pipeline (Weeks 1-2)

### Objectives
- Build text-based RAG system (retrieval + answer generation with citations)
- Set up document ingestion (CLI tool only)
- Create minimal web interface for text queries
- Establish foundation for voice integration

### Technical Components

#### 1. Backend Infrastructure
- **API Server Setup**
  - FastAPI server with REST endpoints
  - Basic error handling and logging
  - Health check endpoint
  - CORS configuration for web client

- **Vector Database Setup**
  - Choose and configure vector DB (Chroma for simplicity, or Pinecone/Qdrant)
  - Set up embedding model (OpenAI text-embedding-3-small or sentence-transformers)
  - Create index schema with minimal metadata: document_id, title, page_number, chunk_index

- **Metadata Store (Stubbed)**
  - SQLite database (simple, no setup required)
  - Minimal schema: documents table (id, title, file_path), chunks table (id, document_id, chunk_index, metadata_json)
  - No collections - single default corpus

#### 2. Document Ingestion Pipeline (CLI Tool)
- **File Processing**
  - PDF text extraction (pymupdf or pdfplumber)
  - Plain text file support
  - Basic error handling

- **Chunking Strategy**
  - Sliding window chunking (300-600 tokens)
  - Preserve metadata: document_id, title, page_number, chunk_index
  - Overlap: 50-100 tokens

- **Embedding & Indexing**
  - Generate embeddings for each chunk
  - Store in vector database with metadata
  - Simple idempotency: skip if document already exists (by filename)

#### 3. Retrieval System
- **Query Processing**
  - Query embedding generation
  - Vector similarity search (top-k=5, configurable)
  - Return chunks with similarity scores and metadata
  - No collection filtering (single corpus)

#### 4. Answer Generation with Citations
- **LLM Integration**
  - Set up LLM API client (OpenAI GPT-4 or Anthropic Claude)
  - Prompt engineering for grounded answers with citations
  - Citation format: [chunk_id] or [1], [2] style
  - Refusal handling: explicitly state when answer not found in documents

- **Citation Mapping**
  - Map citations in answer text to chunk IDs
  - Return citation metadata (document title, page, chunk text)

#### 5. Basic Web Client (Text Input Only)
- **Minimal Interface**
  - Simple HTML/CSS/JavaScript frontend
  - Text input for queries
  - Submit button
  - Display answer with citations (clickable)
  - Show retrieved passages below answer
  - Basic loading and error states

### API Endpoints

```
POST /query
  Input: { "text": "query text" }
  Output: {
    "answer": "answer text with citations",
    "citations": [
      {
        "id": "chunk_123",
        "document_title": "Document Name",
        "page": 5,
        "text": "cited passage...",
        "similarity_score": 0.85
      }
    ],
    "retrieved_chunks": [...],
    "latency_ms": 1234
  }
```

### Deliverables
- ✅ Working text-based RAG system with citations
- ✅ CLI tool for document ingestion: `python ingest.py <file_path>`
- ✅ Basic web interface for text queries
- ✅ Answer generation with proper citation mapping
- ✅ Demo with 3-5 test queries

### Success Criteria
- Can ingest a PDF via CLI and retrieve relevant chunks
- Answers include citations that map to actual chunks
- Citations are clickable and show source passages
- End-to-end latency < 8 seconds for text queries

---

## Phase 2: Voice Integration (Weeks 3-4)

### Objectives
- Add voice capture and transcription
- Integrate voice pipeline with existing RAG system
- Implement transcript editing capability
- Complete the core end-to-end flow

### Technical Components

#### 1. Voice Capture (Client-Side)
- **Audio Recording**
  - Web Audio API / MediaRecorder API for microphone access
  - Permission request handling with clear error states
  - Record button (hold-to-record or click-to-start/stop)
  - Visual feedback: recording indicator (pulsing dot or waveform)
  - Audio format: WebM or WAV, convert to format needed by API

#### 2. Transcription Service
- **Backend Integration**
  - Integrate transcription API (OpenAI Whisper API recommended)
  - POST /transcribe endpoint
  - Audio file upload handling (multipart/form-data)
  - Language: English (hardcoded for v1, configurable later)
  - Error handling for transcription failures

#### 3. UI Enhancements
- **Transcript Display**
  - Show transcription after recording stops
  - Editable transcript text area (pre-filled with transcription)
  - Submit button to send edited transcript to /query
  - Loading states: "Transcribing...", "Retrieving...", "Generating answer..."

- **Voice-Specific UX**
  - Clear recording states: idle, recording, processing
  - Microphone permission error: show message with instructions
  - Fallback: text input always available if microphone unavailable
  - Visual flow: Record → Transcript → Edit → Submit → Answer

#### 4. Error Handling
- **Graceful Degradation**
  - If transcription fails: show error, allow text input
  - If retrieval fails: show error message
  - If generation fails: show retrieved passages and transcript

### API Endpoints

```
POST /transcribe
  Input: multipart/form-data with audio file
  Output: {
    "transcript": "transcribed text",
    "confidence": 0.95,
    "language": "en"
  }

POST /query (existing, now accepts transcript)
  Input: { "text": "transcript or edited text" }
  Output: (same as Phase 1)
```

### Deliverables
- ✅ Voice recording functionality in web client
- ✅ Transcription API endpoint
- ✅ Transcript editing before submission
- ✅ Complete voice-to-answer flow
- ✅ Error handling and text fallback

### Success Criteria
- User can record 5-30 seconds of audio and see transcript within 5 seconds
- Transcript can be edited and submitted successfully
- End-to-end voice-to-answer latency < 8 seconds for small corpus
- System degrades gracefully if transcription fails

---

## Phase 3: Essential Polish (Week 5)

### Objectives
- Ensure core flow is reliable and meets latency targets
- Basic UI improvements for citations
- Essential error handling
- Minimal testing

### Technical Components

#### 1. Citation Display Enhancement
- **UI Improvements**
  - Clickable citations in answer text
  - Modal or expandable section showing cited passages
  - Highlight retrieved chunks below answer
  - Show document title and page for each citation

#### 2. Performance Optimization (Essential Only)
- **Latency Improvements**
  - Basic caching: cache query embeddings (simple in-memory cache)
  - Optimize chunk retrieval (ensure vector DB is properly indexed)
  - No complex optimizations - keep it simple

#### 3. Error Handling
- **Essential Error States**
  - Microphone permission denied
  - Transcription timeout/failure
  - No chunks retrieved (similarity too low)
  - LLM API failure
  - Clear error messages for each case

#### 4. Basic Testing
- **Minimal Test Suite**
  - End-to-end test: voice → transcript → answer
  - Test citation mapping
  - Test error handling paths
  - Manual testing with demo script

### Deliverables
- ✅ Improved citation display
- ✅ Essential error handling
- ✅ Basic performance optimizations
- ✅ End-to-end test suite
- ✅ Demo script with 5+ queries

### Success Criteria
- All latency targets met (transcription <5s, retrieval <500ms/2s, generation <6s)
- Citations are clearly visible and clickable
- Error states are handled gracefully
- Demo script passes reliably

---

## Stubbed/Removed Features

### Stubbed (Minimal Implementation)
- **Document Management**: CLI tool only, no web UI
- **Collections**: Single default corpus, no collection management
- **Conversation/Memory**: Single-turn only, no conversation history
- **Feedback**: Stub endpoint that logs to file, no UI
- **Analytics**: Basic console logging only, no dashboard
- **Authentication**: None in v1
- **Multi-language**: English only

### Removed (Not in Core Flow)
- Admin dashboard
- Document upload web UI
- Collection management
- Multi-turn conversations
- Feedback UI
- Analytics dashboard
- Advanced chunking strategies
- Query rewriting
- Reranking models

---

## Technology Stack (Simplified)

### Backend
- **Framework**: FastAPI (Python)
- **Vector DB**: Chroma (local, simple) or Pinecone (cloud)
- **Metadata DB**: SQLite
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4 or GPT-3.5-turbo
- **Transcription**: OpenAI Whisper API

### Frontend
- **Framework**: Vanilla JavaScript (or React if preferred)
- **Styling**: Tailwind CSS or simple CSS
- **Audio**: Web Audio API, MediaRecorder API

### Infrastructure
- **Deployment**: Docker (optional, can run locally for v1)
- **Hosting**: Local development or simple cloud deployment

---

## Timeline Summary

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | 2 weeks | Core RAG pipeline |
| Phase 2 | 2 weeks | Voice integration |
| Phase 3 | 1 week | Essential polish |
| **Total** | **5 weeks** | **Core Flow Complete** |

---

## Core Flow Diagram

```
User Action          System Component          Output
─────────────────────────────────────────────────────────
Press Record  →  [Web Client]              →  Audio captured
Stop Record   →  [Web Client]              →  Audio file
              →  POST /transcribe          →  Transcript text
Edit (optional)→ [Web Client]              →  Edited text
Submit        →  POST /query              →  Query embedding
              →  [Vector DB]              →  Top-k chunks
              →  [LLM]                    →  Answer + citations
              →  [Web Client]             →  Display answer
```

---

## Success Metrics (Core Flow Only)

- End-to-end latency: voice → answer < 8 seconds (small corpus)
- Citation accuracy: all citations map to retrieved chunks
- Transcription accuracy: >90% word accuracy on test audio
- Retrieval quality: top-5 contains relevant chunk for test queries
- Error rate: <5% failures in core flow

---

## Dependencies & Prerequisites

### Required
- Python 3.9+
- API keys: OpenAI (for embeddings, LLM, transcription)
- Vector database (Chroma local or cloud service)
- Modern web browser with microphone support

### Optional
- Docker (for containerization)
- Cloud hosting (for deployment)

---

## Next Steps After Core Flow

Once the core flow is working:
1. Add conversation/memory if needed
2. Build document management UI if needed
3. Add feedback mechanisms
4. Implement analytics
5. Add multi-collection support
6. Performance optimizations

---

## Technology Stack Recommendations

### Backend
- **Framework**: FastAPI (Python) or Express.js (Node.js)
- **Vector DB**: Pinecone, Weaviate, Qdrant, or Chroma
- **Metadata DB**: PostgreSQL or SQLite (Phase 0-1), PostgreSQL (Phase 2+)
- **Embeddings**: OpenAI text-embedding-3-small/3-large, Cohere, or sentence-transformers
- **LLM**: OpenAI GPT-4, Anthropic Claude, or local model (Llama 2/3)
- **Transcription**: OpenAI Whisper API, Google Speech-to-Text, or AssemblyAI

### Frontend
- **Framework**: React, Vue, or vanilla JavaScript
- **Styling**: Tailwind CSS or Material-UI
- **Audio**: Web Audio API, MediaRecorder API

### Infrastructure
- **Deployment**: Docker containers
- **Hosting**: AWS, GCP, or Azure
- **Queue**: Celery (Python) or Bull (Node.js) for async jobs
- **Monitoring**: Prometheus + Grafana or cloud-native solutions

---

## Risk Mitigation

### Core Flow Risks
- **Poor retrieval quality**: Start with small corpus (5-10 documents), iterate on chunking strategy
- **High latency**: Use efficient embedding model, basic caching, optimize vector search
- **Transcription errors**: Provide edit capability, use high-quality API (Whisper)
- **Citation mapping failures**: Simple regex-based citation extraction, validate against retrieved chunks
- **LLM hallucination**: Strict prompting for grounding, refusal when insufficient context

---

## Development Approach

### Iterative Development
- Build Phase 1 (text RAG) first, validate retrieval quality
- Add voice in Phase 2, test end-to-end flow
- Polish in Phase 3 based on testing

### Testing Strategy
- Manual testing with demo script after each phase
- End-to-end test: record → transcribe → query → answer
- Validate citations map correctly to chunks
- Test error handling paths

### Demo Script Requirements
- 5+ representative queries covering:
  - Factual questions
  - Definition requests
  - Summary requests
  - Questions requiring multiple chunks
- All queries should have known good answers in corpus

---

## Notes

- Focus on getting core flow working end-to-end before adding features
- Keep architecture simple - can refactor later if needed
- Document ingestion via CLI is sufficient for v1
- Single-turn conversations are fine for initial prototype
- Prioritize reliability of core flow over feature completeness

