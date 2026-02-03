#!/bin/bash
# Install system dependencies for PPT processing

echo "📦 Installing system dependencies..."

# Update package list
apt-get update -qq

# Install LibreOffice (for PPTX to PDF conversion)
echo "📦 Installing LibreOffice..."
apt-get install -y -qq libreoffice libreoffice-core libreoffice-common

# Install Poppler (for PDF to image conversion)
echo "📦 Installing Poppler..."
apt-get install -y -qq poppler-utils

echo "✅ System dependencies installed successfully!"

