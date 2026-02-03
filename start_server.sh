#!/bin/bash
set -e

echo "🔍 Checking Python version..."
python3 --version

echo "🔍 Checking installed packages location..."
python3 -c "import sys; print('Python path:', sys.path)"

echo "🔍 Looking for uvicorn..."
python3 -c "import uvicorn; print('✅ uvicorn found:', uvicorn.__version__)" || {
    echo "❌ uvicorn not found in Python path"
    echo "📦 Attempting to install with --break-system-packages..."
    pip3 install --break-system-packages uvicorn
}

echo "🚀 Starting server..."
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

