#!/bin/bash
# Startup script for Railway deployment

# Use PORT from Railway or default to 8000
# Railway sets PORT automatically, ensure it's a number
PORT=${PORT:-8000}

# Convert to integer to ensure it's valid
PORT=$(($PORT))

# Debug: Print environment info
echo "Starting application..."
echo "PORT: $PORT"
echo "HOST: 0.0.0.0"

# Verify Python and dependencies
python --version
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn:', uvicorn.__version__)"

# Start the application
echo "Starting uvicorn on port $PORT..."
exec uvicorn api:app --host 0.0.0.0 --port ${PORT}

