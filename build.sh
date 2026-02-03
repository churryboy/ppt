#!/bin/bash

# Build script for Render deployment
# This script installs dependencies and builds the frontend

echo "🔨 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to frontend and build
echo "⚛️  Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
echo "   Frontend built to: frontend/build"
echo "   Ready to deploy!"

