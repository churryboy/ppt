#!/bin/bash

echo "🚀 Starting Backend Server..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Run the backend
cd "$(dirname "$0")"
python backend/main.py

