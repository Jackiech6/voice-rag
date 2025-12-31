#!/bin/bash
# Startup script for Railway deployment

# Use PORT from Railway or default to 8000
PORT=${PORT:-8000}

# Start the application
exec uvicorn api:app --host 0.0.0.0 --port $PORT

