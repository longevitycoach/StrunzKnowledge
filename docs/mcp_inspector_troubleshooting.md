# MCP Inspector Troubleshooting Guide

## 🎯 Correct Configuration

**MCP Inspector URL:**
```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=d6a442c759152a62ecdf2b9c938db670695864ea1b0c99d592f0dfe1ecd2d6e9
```

**Connection Settings:**
- **Transport**: `sse`
- **URL**: `http://localhost:8000/sse`
- **Authentication**: Leave empty

## 🔧 If Connection Fails

### Option 1: Try Different URLs
- `http://127.0.0.1:8000/sse`
- `http://localhost:8000/messages`

### Option 2: Check Server Status
```bash
curl http://localhost:8000/
```
Should return health check with version 1.0.1

### Option 3: Test SSE Manually
```bash
curl -H "Accept: text/event-stream" http://localhost:8000/sse
```
Should start streaming events

### Option 4: Use HTTP Transport
If SSE doesn't work:
- **Transport**: `http`
- **URL**: `http://localhost:8000`

## 🧪 Manual Testing Alternative

If MCP Inspector keeps failing, you can test manually with our script:
```bash
python test_local_http_mcp.py
```

This will show you exactly what the MCP Inspector should see:
- ✅ Version 1.0.1 (vs Railway's 1.0.0)
- ✅ Resources capability: {'subscribe': False, 'listChanged': False}
- ✅ All 24 tools working

## 🎯 What We're Testing

The key difference between local and Railway:
- **Local v1.0.1**: Has `resources` capability
- **Railway v1.0.0**: Missing `resources` capability

This is likely why Claude.ai shows "NO PROVIDED TOOLS"!