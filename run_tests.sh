#!/bin/bash
# Test runner script

echo "Running Phase 1 tests..."
echo "========================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run tests
echo ""
echo "Running pytest..."
pytest -v

echo ""
echo "Tests complete!"

