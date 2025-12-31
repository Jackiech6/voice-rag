#!/bin/bash
# Helper script to set up .env file

if [ -f ".env" ]; then
    echo ".env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "Setting up .env file..."
echo ""
read -p "Enter your OpenAI API key: " api_key

if [ -z "$api_key" ]; then
    echo "Error: API key cannot be empty"
    exit 1
fi

cat > .env << EOF
# OpenAI API Key (required for embeddings, LLM, and transcription)
OPENAI_API_KEY=$api_key

# Optional: Custom configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K=5
EOF

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "You can now:"
echo "  1. Verify setup: python verify_setup.py"
echo "  2. Ingest a document: python ingest.py sample_document.txt"
echo "  3. Start the server: python api.py"

