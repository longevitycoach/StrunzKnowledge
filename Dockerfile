# Use Python 3.11 slim image as base
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

# Copy requirements first for better caching
COPY requirements-prod.txt .
COPY requirements-flexible.txt .

# Install Python dependencies with memory optimization
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies in smaller batches to reduce memory usage
# First install numpy separately as it's a large dependency
RUN pip install --no-cache-dir numpy==1.26.3

# Then install the rest using flexible requirements
RUN pip install --no-cache-dir -r requirements-flexible.txt

# Copy application source code
COPY src/ ./src/
COPY main.py ./
COPY start_server.py ./
COPY simple_server.py ./
COPY scripts/ ./scripts/

# Create config directory (it may be empty)
RUN mkdir -p config

# Copy FAISS index chunks
COPY data/faiss_indices/chunks/ ./data/faiss_indices/chunks/

# Create necessary directories
RUN mkdir -p data/raw data/processed logs

# Reconstruct FAISS indices from chunks
RUN cd /app && bash scripts/reconstruct_indices.sh

# Create a non-root user to run the application
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose the MCP server port
EXPOSE 8000

# Add health check using curl (lighter than Python with requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command to run the MCP server
CMD ["python", "-u", "start_server.py"]

# Labels for container metadata
LABEL maintainer="Strunz Knowledge Base Team" \
      version="1.0.0" \
      description="Dr. Strunz Knowledge Base with MCP Server"