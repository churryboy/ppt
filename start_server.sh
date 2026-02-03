#!/bin/bash
set -e

echo "🔍 Checking Python version..."
python3 --version

# Add common package installation directories to PYTHONPATH
export PYTHONPATH="/opt/render/project/src/.venv/lib/python3.11/site-packages:$PYTHONPATH"
export PYTHONPATH="/opt/render/.local/lib/python3.11/site-packages:$PYTHONPATH"
export PYTHONPATH="/usr/local/lib/python3.11/site-packages:$PYTHONPATH"
export PATH="/opt/render/.local/bin:$PATH"

# Add backend directory to PYTHONPATH for local imports
export PYTHONPATH="/opt/render/project/src/backend:$PYTHONPATH"

echo "📦 Installing all requirements to user directory..."
pip3 install --user -r requirements.txt

echo "🔍 Verifying packages..."
python3 -c "import fastapi, uvicorn; print('✅ All packages found')"

echo "🚀 Starting server..."
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

