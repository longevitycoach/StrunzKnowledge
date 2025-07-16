# Docker Deployment Guide

## 🐳 Docker Image Information

### Current Version: **v0.5.3**

**Registry**: GitHub Container Registry (ghcr.io)  
**Repository**: `ghcr.io/longevitycoach/strunzknowledge`  
**Tags**: `0.5.3`, `latest`  

## 📦 Available Images

### GitHub Container Registry (Recommended)
```bash
# Latest version
docker pull ghcr.io/longevitycoach/strunzknowledge:latest

# Specific version
docker pull ghcr.io/longevitycoach/strunzknowledge:0.5.3
```

### Docker Hub (Legacy)
```bash
# Latest version
docker pull longevitycoach/strunz-mcp:latest

# Specific version
docker pull longevitycoach/strunz-mcp:0.5.3
```

## 🚀 Quick Start

### 1. Pull and Run
```bash
# Pull the latest image
docker pull ghcr.io/longevitycoach/strunzknowledge:latest

# Run the container
docker run -d \
  --name strunz-knowledge \
  -p 8000:8000 \
  --env-file .env \
  ghcr.io/longevitycoach/strunzknowledge:latest
```

### 2. Using Docker Compose
```yaml
version: '3.8'
services:
  strunz-knowledge:
    image: ghcr.io/longevitycoach/strunzknowledge:0.5.3
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    restart: unless-stopped
```

### 3. Development Mode
```bash
# Run with development settings
docker run -d \
  --name strunz-knowledge-dev \
  -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e LOG_LEVEL=debug \
  ghcr.io/longevitycoach/strunzknowledge:latest
```

## 🔧 Configuration

### Environment Variables
```bash
# Server Configuration
ENVIRONMENT=production          # production, development, staging
LOG_LEVEL=info                 # debug, info, warning, error
HOST=0.0.0.0                   # Server host
PORT=8000                      # Server port

# MCP Configuration
MCP_PROTOCOL_VERSION=2025-03-26
MCP_TRANSPORT=sse

# Vector Store Configuration
VECTOR_STORE_PATH=/app/data/faiss_indices
PRELOAD_VECTOR_STORE=true

# Performance Settings
SINGLETON_PATTERN_ENABLED=true
HEALTH_CHECK_TIMEOUT=30
STARTUP_TIMEOUT=120
```

### Volume Mounts
```bash
# Mount data directory for persistence
docker run -d \
  --name strunz-knowledge \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/longevitycoach/strunzknowledge:latest
```

## 🏗️ Building from Source

### 1. Clone Repository
```bash
git clone https://github.com/longevitycoach/StrunzKnowledge.git
cd StrunzKnowledge
```

### 2. Build Docker Image
```bash
# Build locally
docker build -t strunz-knowledge:local .

# Build for GitHub Container Registry
docker build -t ghcr.io/longevitycoach/strunzknowledge:0.5.3 .
```

### 3. Using Build Script
```bash
# Make executable
chmod +x src/scripts/deployment/build_and_push_docker.sh

# Build and push
./src/scripts/deployment/build_and_push_docker.sh
```

## 🔍 Health Checks

### Built-in Health Check
```bash
# Check container health
docker ps

# View health check logs
docker inspect strunz-knowledge | grep Health -A 10
```

### Manual Health Check
```bash
# Test health endpoint
curl -f http://localhost:8000/

# Detailed health information
curl http://localhost:8000/health
```

## 📊 Monitoring

### Container Logs
```bash
# View logs
docker logs strunz-knowledge

# Follow logs
docker logs -f strunz-knowledge

# Last 100 lines
docker logs --tail 100 strunz-knowledge
```

### Resource Usage
```bash
# Container stats
docker stats strunz-knowledge

# Resource usage
docker exec strunz-knowledge ps aux
```

## 🔄 Updates

### Update to Latest
```bash
# Pull latest image
docker pull ghcr.io/longevitycoach/strunzknowledge:latest

# Stop and remove old container
docker stop strunz-knowledge
docker rm strunz-knowledge

# Run new container
docker run -d \
  --name strunz-knowledge \
  -p 8000:8000 \
  ghcr.io/longevitycoach/strunzknowledge:latest
```

### Zero-Downtime Update
```bash
# Pull new image
docker pull ghcr.io/longevitycoach/strunzknowledge:0.5.3

# Start new container on different port
docker run -d \
  --name strunz-knowledge-new \
  -p 8001:8000 \
  ghcr.io/longevitycoach/strunzknowledge:0.5.3

# Test new container
curl http://localhost:8001/health

# Switch containers (update load balancer/proxy)
# Then remove old container
docker stop strunz-knowledge
docker rm strunz-knowledge
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker logs strunz-knowledge

# Check resource usage
docker system df
docker system prune
```

#### 2. Health Check Failures
```bash
# Check health endpoint
curl -v http://localhost:8000/

# Check container resources
docker stats strunz-knowledge
```

#### 3. Performance Issues
```bash
# Check if singleton pattern is working
docker logs strunz-knowledge | grep -i singleton

# Monitor memory usage
docker exec strunz-knowledge ps aux | grep python
```

### Debug Mode
```bash
# Run with debug logging
docker run -d \
  --name strunz-knowledge-debug \
  -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e ENVIRONMENT=development \
  ghcr.io/longevitycoach/strunzknowledge:latest
```

## 📋 Container Specifications

### System Requirements
- **CPU**: 1 core minimum, 2 cores recommended
- **Memory**: 2GB minimum, 4GB recommended
- **Storage**: 1GB minimum, 2GB recommended
- **Network**: Internet access for model downloads

### Performance Optimizations
- **Singleton Pattern**: Vector store loads once at startup
- **Health Checks**: <100ms response time
- **Memory Management**: Stable usage after initialization
- **Startup Time**: ~30-60 seconds with preloading

### Security Features
- **Non-root user**: Runs as dedicated application user
- **Minimal base image**: Python 3.11 slim
- **No package caches**: Cleaned during build
- **Health checks**: Built-in container health monitoring

## 🔗 Links

### GitHub
- **Repository**: https://github.com/longevitycoach/StrunzKnowledge
- **Releases**: https://github.com/longevitycoach/StrunzKnowledge/releases
- **Issues**: https://github.com/longevitycoach/StrunzKnowledge/issues

### Docker Registries
- **GitHub Container Registry**: https://ghcr.io/longevitycoach/strunzknowledge
- **Docker Hub**: https://hub.docker.com/r/longevitycoach/strunz-mcp

### Documentation
- **API Documentation**: Available at `/docs` endpoint
- **Release Notes**: [docs/RELEASE_NOTES_v0.5.3.md](RELEASE_NOTES_v0.5.3.md)
- **Performance Guide**: [docs/test-reports/](test-reports/)

## 📝 Example Deployment

### Railway (Production)
```bash
# Railway automatically builds and deploys from GitHub
# Health check endpoint: /railway-health
# Deployment URL: https://strunz.up.railway.app
```

### AWS ECS/Fargate
```json
{
  "family": "strunz-knowledge",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "strunz-knowledge",
      "image": "ghcr.io/longevitycoach/strunzknowledge:0.5.3",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 120
      }
    }
  ]
}
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: strunz-knowledge
spec:
  replicas: 1
  selector:
    matchLabels:
      app: strunz-knowledge
  template:
    metadata:
      labels:
        app: strunz-knowledge
    spec:
      containers:
      - name: strunz-knowledge
        image: ghcr.io/longevitycoach/strunzknowledge:0.5.3
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: strunz-knowledge-service
spec:
  selector:
    app: strunz-knowledge
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

**🎉 Docker deployment guide for Dr. Strunz Knowledge Base MCP Server v0.5.3**