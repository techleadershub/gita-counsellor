FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (from backend directory)
COPY backend/ .

# Copy EPUB file (from project root)
# Railway: Set Root Directory to project root (not backend), Dockerfile Path to backend/Dockerfile
COPY epubs/BhagavadGitaAsItIs.epub /app/epubs/BhagavadGitaAsItIs.epub

# Create data directory
RUN mkdir -p /app/data /app/epubs

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application (Railway sets PORT env var automatically)
# Use sh -c to allow environment variable substitution
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

