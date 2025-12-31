#!/bin/bash
# Startup script for Railway deployment

# Use PORT from Railway or default to 8000
# Railway sets PORT automatically, ensure it's a number
PORT=${PORT:-8000}

# Convert to integer to ensure it's valid
PORT=$(($PORT))

# Start the application
exec uvicorn api:app --host 0.0.0.0 --port ${PORT}

