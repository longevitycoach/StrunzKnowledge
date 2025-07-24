# Use Python 3.11 slim image as base
# Rebuild trigger: v0.7.10 deployment fix
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    POETRY_VERSION=1.7.1

# Install system dependencies in smaller chunks to reduce memory usage
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install build dependencies separately
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR $APP_HOME

# Copy unified requirements for better caching
COPY requirements-unified.txt .

# Install Python dependencies with memory optimization
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies in smaller batches to reduce memory usage
# First install numpy separately as it's a large dependency
RUN pip install --no-cache-dir numpy==1.26.3

# Then install the rest using unified requirements
RUN pip install --no-cache-dir -r requirements-unified.txt

# Copy application source code
COPY src/ ./src/
COPY main.py ./
COPY railway-deploy.py ./

# Create config directory (it may be empty)
RUN mkdir -p config

# Copy FAISS index chunks
COPY data/faiss_indices/chunks/ ./data/faiss_indices/chunks/

# Create necessary directories
RUN mkdir -p data/raw data/processed logs

# Reconstruct FAISS indices from chunks
RUN cd /app && bash src/scripts/data/reconstruct_indices.sh

# Create a non-root user to run the application
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose the MCP server port
EXPOSE 8000

# Enhanced health check with extended startup time for FAISS loading
HEALTHCHECK --interval=30s --timeout=20s --start-period=120s --retries=10 \
    CMD curl -f -H "Accept: application/json" http://localhost:8000/ || \
        (echo "Health check failed - checking detailed health:" && \
         curl -s http://localhost:8000/health | head -20 && \
         exit 1)

# Default command to run the MCP server
CMD ["python", "-u", "main.py"]

# Labels for container metadata (OCI compliant)
LABEL maintainer="Strunz Knowledge Base Team" \
      version="0.9.0" \
      org.opencontainers.image.title="StrunzKnowledge MCP Server" \
      org.opencontainers.image.description="Dr. Strunz Knowledge Base MCP Server - A comprehensive health and nutrition knowledge system based on Dr. Ulrich Strunz's work. Provides semantic search across 13 books, 6,953 news articles, and forum content via the Model Context Protocol (MCP) for Claude Desktop and Claude.ai integration." \
      org.opencontainers.image.authors="longevitycoach" \
      org.opencontainers.image.source="https://github.com/longevitycoach/StrunzKnowledge" \
      org.opencontainers.image.documentation="https://github.com/longevitycoach/StrunzKnowledge/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="longevitycoach" \
      org.opencontainers.image.url="https://strunz.up.railway.app" \
      org.opencontainers.image.created="2025-07-24" \
      org.opencontainers.image.version="0.9.0"