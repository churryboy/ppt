# Use official Python image with Debian base (for apt-get)
FROM python:3.11-slim

# Install system dependencies (LibreOffice and Poppler)
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-core \
    libreoffice-common \
    poppler-utils \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for frontend build)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend package files and install dependencies
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# Copy entire project
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Back to app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p uploads slides archives

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/backend:$PYTHONPATH
ENV PORT=8000

# Install gunicorn for production server with multiple workers
RUN pip install --no-cache-dir gunicorn

# Start the application with gunicorn + uvicorn workers (4 workers for concurrent requests)
CMD ["sh", "-c", "cd /app && gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}"]
