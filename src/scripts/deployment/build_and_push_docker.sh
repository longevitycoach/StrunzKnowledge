#!/bin/bash

# Build and Push Docker Image Script
# This script builds and pushes the Docker image to GitHub Container Registry

set -e

# Configuration
REGISTRY="ghcr.io"
REPO_NAME="longevitycoach/strunzknowledge"
VERSION="0.5.3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Building and Pushing Docker Image v${VERSION}${NC}"
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Get current directory (should be project root)
PROJECT_ROOT=$(pwd)
echo -e "${YELLOW}📁 Project root: ${PROJECT_ROOT}${NC}"

# Build the Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t ${REGISTRY}/${REPO_NAME}:${VERSION} -t ${REGISTRY}/${REPO_NAME}:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Login to GitHub Container Registry
echo -e "${YELLOW}🔑 Logging in to GitHub Container Registry...${NC}"
echo "Please ensure you have a GitHub token with package:write permissions"
echo "You can create one at: https://github.com/settings/tokens"

# Check if already logged in
if docker info | grep -q "Username.*longevitycoach"; then
    echo -e "${GREEN}✅ Already logged in to GitHub Container Registry${NC}"
else
    echo -e "${YELLOW}Please log in to GitHub Container Registry:${NC}"
    docker login ${REGISTRY}
fi

# Push the images
echo -e "${YELLOW}📤 Pushing Docker image v${VERSION}...${NC}"
docker push ${REGISTRY}/${REPO_NAME}:${VERSION}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image v${VERSION} pushed successfully${NC}"
else
    echo -e "${RED}❌ Failed to push Docker image v${VERSION}${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Pushing Docker image latest...${NC}"
docker push ${REGISTRY}/${REPO_NAME}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image latest pushed successfully${NC}"
else
    echo -e "${RED}❌ Failed to push Docker image latest${NC}"
    exit 1
fi

# Display image information
echo -e "${GREEN}🎉 Docker images pushed successfully!${NC}"
echo "============================================"
echo -e "${YELLOW}📋 Image Details:${NC}"
echo "Repository: ${REGISTRY}/${REPO_NAME}"
echo "Tags: ${VERSION}, latest"
echo "Size: $(docker images ${REGISTRY}/${REPO_NAME}:${VERSION} --format 'table {{.Size}}' | tail -1)"
echo ""
echo -e "${YELLOW}📖 Usage:${NC}"
echo "docker pull ${REGISTRY}/${REPO_NAME}:${VERSION}"
echo "docker pull ${REGISTRY}/${REPO_NAME}:latest"
echo ""
echo -e "${YELLOW}🔗 GitHub Packages:${NC}"
echo "https://github.com/longevitycoach/StrunzKnowledge/pkgs/container/strunzknowledge"
echo ""
echo -e "${GREEN}✅ Docker image deployment complete!${NC}"