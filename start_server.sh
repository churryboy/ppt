#!/bin/bash
set -e

echo "🔍 Checking Python version..."
python3 --version

echo "🔍 Checking pip3 version..."
pip3 --version

echo "📦 Verifying uvicorn installation..."
pip3 show uvicorn || {
    echo "❌ uvicorn not found, installing..."
    pip3 install uvicorn
}

echo "🚀 Starting server..."
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

