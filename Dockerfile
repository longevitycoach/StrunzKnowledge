# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials for some Python packages
    build-essential \
    # For web scraping
    libxml2-dev \
    libxslt-dev \
    # For SSL/TLS
    ca-certificates \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR $APP_HOME

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY main.py ./
COPY start_server.py ./
COPY config/ ./config/ 2>/dev/null || true

# Create necessary directories
RUN mkdir -p data/raw data/processed data/faiss_indices logs

# Copy FAISS index chunks and reconstruction scripts
COPY data/faiss_indices/chunks/ ./data/faiss_indices/chunks/
COPY scripts/reconstruct_indices.sh ./scripts/

# Reconstruct FAISS indices from chunks
RUN cd /app && bash scripts/reconstruct_indices.sh

# Create a non-root user to run the application
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose the MCP server port
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/').raise_for_status()"

# Default command to run the MCP server
CMD ["python", "-u", "start_server.py"]

# Labels for container metadata
LABEL maintainer="Strunz Knowledge Base Team" \
      version="1.0.0" \
      description="Dr. Strunz Knowledge Base with MCP Server"