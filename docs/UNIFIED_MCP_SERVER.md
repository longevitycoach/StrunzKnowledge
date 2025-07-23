# Unified MCP Server Documentation

## Overview

We now have a **single MCP server** (`src/mcp/unified_mcp_server.py`) that works in all environments:
- ✅ Local development
- ✅ Docker containers
- ✅ Railway production
- ✅ Claude Desktop
- ✅ Claude.ai web

## Why We Had Multiple Servers

The multiple servers in `src/scripts/deployment/` evolved due to different compatibility requirements:

1. **railway_claude_ai_compatible.py** - Added Claude.ai specific endpoint
2. **railway_mcp_fixed.py** - Fixed tool execution issues
3. **railway_official_mcp_server.py** - Attempted to use official SDK
4. **claude_compatible_server.py** - Original base server

This created confusion and maintenance overhead.

## The Unified Solution

### Location
`src/mcp/unified_mcp_server.py` - The single source of truth

### Features
- **All 19 Dr. Strunz tools** from enhanced_server.py
- **Claude.ai compatibility** - Special endpoint `/api/organizations/{org_id}/mcp/start-auth/{auth_id}`
- **OAuth2 authentication** - Full OAuth2 flow support
- **SSE transport** - Server-Sent Events for real-time communication
- **Health checks** - Multiple endpoints for monitoring
- **CORS support** - Works in web browsers

## How to Use

### 1. Local Development
```bash
# Use main entry point (start_server.py was removed)
python main.py

# Or directly
python src/mcp/unified_mcp_server.py

# Access at http://localhost:8000
```

### 2. Docker
```bash
# Build
docker build -t strunz-mcp .

# Run
docker run -p 8000:8000 strunz-mcp

# The Dockerfile runs main.py which can use the unified server
```

### 3. Railway Production
- Automatically uses `railway-deploy.py`
- Which now imports `unified_mcp_server.py`
- Deployed at https://strunz.up.railway.app

### 4. Testing
```bash
# Test health
curl http://localhost:8000/

# Test Claude.ai endpoint
curl "http://localhost:8000/api/organizations/test/mcp/start-auth/test123"

# Test MCP discovery
curl http://localhost:8000/.well-known/mcp/resource

# Run full test suite
python src/scripts/testing/test_claude_ai_auth_full.py http://localhost:8000
```

## Architecture

```
unified_mcp_server.py
├── FastAPI Application
├── Enhanced MCP Server (19 tools)
├── OAuth2 Provider
├── SSE Transport
├── Claude.ai Compatibility
└── Health Monitoring
```

## Migration Guide

### From Old Servers
Replace any imports:
```python
# Old
from src.scripts.deployment.railway_claude_ai_compatible import main
from src.mcp.claude_compatible_server import main

# New
from src.mcp.unified_mcp_server import main
```

### Environment Variables
- `PORT` - Server port (default: 8000)
- `RAILWAY_PUBLIC_DOMAIN` - Public domain for Railway
- `RAILWAY_ENVIRONMENT` - Set to "production" for Railway
- `LOG_LEVEL` - Logging level (default: INFO)

## Endpoints

### Core Endpoints
- `/` - Health check
- `/health` - Detailed health
- `/railway-health` - Railway-specific health

### MCP Protocol
- `/.well-known/mcp/resource` - MCP discovery
- `/messages` - MCP message handling
- `/sse` - Server-Sent Events

### OAuth2
- `/.well-known/oauth-authorization-server` - OAuth metadata
- `/oauth/register` - Client registration
- `/oauth/authorize` - Authorization
- `/oauth/token` - Token exchange

### Claude.ai
- `/api/organizations/{org_id}/mcp/start-auth/{auth_id}` - Claude.ai auth

## Benefits

1. **Single Source** - One server to maintain
2. **All Features** - Nothing is missing
3. **Consistent Behavior** - Same in all environments
4. **Easier Testing** - Test once, run everywhere
5. **Clear Architecture** - No deployment scripts doing server logic

## Cleanup Recommendation

After verifying the unified server works, consider:
1. Archive old deployment servers to `src/archive/`
2. Update all documentation to reference unified server
3. Simplify CI/CD to use single server

## Version Management

When updating versions:
1. Update `SERVER_VERSION` in `unified_mcp_server.py`
2. Use the version update script: `python src/scripts/update_version.py X.Y.Z`
3. This will update all other files automatically