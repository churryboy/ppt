#!/bin/bash

echo "🚀 Starting Frontend..."
echo ""

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

npm start

