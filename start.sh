#!/bin/bash

# PowerPoint Search Platform - Startup Script

echo "🚀 Starting PowerPoint Search Platform..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14 or higher."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo "✅ Node.js found: $(node --version)"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Python dependencies installed"
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
else
    echo "✅ Frontend dependencies already installed"
fi
cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Backend:  python backend/main.py"
echo "  2. Frontend: cd frontend && npm start"
echo ""
echo "Or run each command in separate terminals."

