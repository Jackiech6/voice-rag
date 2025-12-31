# Quick Start Guide - Phase 1

## Prerequisites

You need an **OpenAI API key** to run this system. Get one at: https://platform.openai.com/api-keys

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   # Create .env file with your API key
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```
   
   Or manually create `.env` with:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Verify setup:**
   ```bash
   python verify_setup.py
   ```

## Usage

### Step 1: Ingest a Document

```bash
# Use the sample document
python ingest.py sample_document.txt

# Or use your own PDF
python ingest.py path/to/your/document.pdf
```

You should see output like:
```
Processing document: sample_document.txt
  Title: sample_document
  Pages: 1
Creating chunks...
  Created 3 chunks
  Document ID: 1
Generating embeddings...
Indexing in vector database...

✅ Successfully ingested document: sample_document
   Document ID: 1
   Chunks: 3
```

### Step 2: Start the Server

```bash
python api.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Use the Web Interface

Open your browser and go to:
```
http://localhost:8000/static/index.html
```

Type a question like:
- "What is machine learning?"
- "What are the types of machine learning?"
- "Explain deep learning"

Click Submit and see the answer with citations!

## Testing

Run tests (some tests require API key):
```bash
pytest
```

Run tests without API calls (unit tests only):
```bash
pytest tests/test_document_processor.py tests/test_vector_store.py
```

## Troubleshooting

### "OPENAI_API_KEY environment variable is required"
- Make sure you created `.env` file in the project root
- Check that the file contains: `OPENAI_API_KEY=your_key_here`
- No quotes around the key value

### "No module named 'fitz'"
- Install PyMuPDF: `pip install pymupdf`

### No results from queries
- Make sure you ingested at least one document
- Check that the document content is relevant to your question
- Verify the vector database was created (check `chroma_db/` directory)

### Port 8000 already in use
- Change port in `config.py` or set `PORT=8001` in `.env`
- Or stop the other service using port 8000

## Next Steps

Once Phase 1 is working:
- Try ingesting multiple documents
- Test with different types of questions
- Check the citations to verify grounding
- Review the retrieved chunks to understand retrieval quality

Phase 2 will add voice transcription!

