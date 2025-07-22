# Docker Image Registry Management Guide

## Important: Docker Hub vs GitHub Container Registry

Based on the investigation, the Docker images are published to **Docker Hub**, not GitHub Container Registry:
- **Docker Hub URL**: https://hub.docker.com/r/longevitycoach/strunz-mcp
- **GitHub Packages**: Currently not used for this project

## Understanding Package Versions

### Why Multiple Entries Per Version?
When you see multiple entries for each version in GitHub Container Registry, it's because Docker images are composed of layers:

1. **Base Layers**: Python 3.11 base image
2. **System Dependencies**: apt packages (gcc, g++, etc.)
3. **Python Dependencies**: pip packages (numpy, fastapi, etc.)
4. **Application Code**: Your source code
5. **Metadata**: Configuration and manifests

Each layer gets its own SHA256 digest, which is why you see entries like:
- `sha256:1234abcd...` - Base Python layer
- `sha256:5678efgh...` - Dependencies layer
- `sha256:9012ijkl...` - Application layer
- `latest` or `v0.7.8` - Tagged complete image

### GitHub Free Account Limits

| Feature | Private Packages | Public Packages |
|---------|-----------------|-----------------|
| Storage | 500 MB | Unlimited |
| Bandwidth | 1 GB/month | Unlimited |
| Retention | Unlimited | Unlimited |

Since your repository is **public**, you have:
- ✅ **Unlimited storage**
- ✅ **Unlimited bandwidth**
- ✅ **No cost**

## Cleaning Up Old Versions

### Manual Cleanup (GitHub UI)
1. Go to: https://github.com/longevitycoach/StrunzKnowledge/pkgs/container/strunzknowledge
2. Click on a version
3. Click "Delete" button
4. Confirm deletion

### Automated Cleanup Script
Use the provided script to keep only the latest versions:

```bash
# Make executable
chmod +x src/scripts/cleanup_docker_versions.sh

# Run cleanup (keeps latest 3 versions by default)
./src/scripts/cleanup_docker_versions.sh

# Or keep only 1 latest version
KEEP_LATEST=1 ./src/scripts/cleanup_docker_versions.sh
```

### GitHub CLI Commands
```bash
# List all versions
gh api /user/packages/container/strunzknowledge/versions | jq '.[] | {id, created_at, tags: .metadata.container.tags}'

# Delete specific version
gh api --method DELETE /user/packages/container/strunzknowledge/versions/VERSION_ID

# Delete all untagged versions
gh api /user/packages/container/strunzknowledge/versions | \
  jq -r '.[] | select(.metadata.container.tags | length == 0) | .id' | \
  xargs -I {} gh api --method DELETE /user/packages/container/strunzknowledge/versions/{}
```

## Best Practices

### 1. Tag Management
- Always tag production releases: `v0.7.8`
- Use `latest` for the most recent stable version
- Delete untagged versions regularly

### 2. Retention Policy
- Keep last 3-5 tagged versions
- Delete all untagged versions
- Archive old versions locally if needed

### 3. Automated Cleanup
Add to your CI/CD pipeline:
```yaml
- name: Cleanup old versions
  run: |
    gh api /user/packages/container/strunzknowledge/versions | \
    jq -r '.[] | select(.metadata.container.tags | length == 0) | .id' | \
    xargs -I {} gh api --method DELETE /user/packages/container/strunzknowledge/versions/{}
```

### 4. Docker Build Optimization
Reduce layer count by combining commands:
```dockerfile
# Bad - creates multiple layers
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y g++

# Good - creates single layer
RUN apt-get update && \
    apt-get install -y gcc g++ && \
    rm -rf /var/lib/apt/lists/*
```

## Current Status
- **Repository**: Public (unlimited storage)
- **No cost or limits** for your usage
- **Recommendation**: Clean up untagged versions to reduce clutter

## Security Note
- Public packages are visible to everyone
- Don't include secrets in Docker images
- Use GitHub Secrets for sensitive data