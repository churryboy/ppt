#!/bin/bash
set -e

echo "🚀 Starting PPT Report Repository server..."

# Add backend directory to PYTHONPATH for local imports
export PYTHONPATH="/opt/render/project/src/backend:$PYTHONPATH"

# Use the virtual environment created by Render during build
if [ -d "/opt/render/project/src/.venv" ]; then
    echo "✅ Using virtual environment"
    source /opt/render/project/src/.venv/bin/activate
fi

# Start the server
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

