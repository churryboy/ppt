#!/bin/bash
set -e

echo "🚀 Starting PPT Report Repository server..."

# Add backend directory to PYTHONPATH for local imports
export PYTHONPATH="/opt/render/project/src/backend:$PYTHONPATH"

# Start the server immediately (packages already installed during build)
exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"

