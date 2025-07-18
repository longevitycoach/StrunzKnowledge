# Release Notes - v0.7.2

**Release Date**: July 18, 2025  
**Type**: Claude.ai Compatibility Release

## 🎯 Major Enhancement

This release adds a comprehensive Claude.ai compatibility layer to resolve persistent "not_available" errors.

## 🔍 Investigation Findings

Through extensive testing with the official MCP client, we discovered:

1. **Claude.ai uses proprietary endpoints** not documented in the MCP specification:
   - `/api/organizations/{org_id}/mcp/start-auth/{auth_id}`
   - This endpoint receives requests from Claude.ai but returns 404 on standard MCP servers

2. **Standard MCP functionality works perfectly**:
   - ✅ OAuth2 flow: Client registration, authorization, token exchange
   - ✅ MCP protocol: Initialize, tools/list, tools/call
   - ✅ Tool execution: All 20 tools execute correctly
   - ✅ SSE transport: Streaming connection established

3. **Version inconsistency fixed**: Some endpoints were reporting v0.6.1

## 🚀 New Features

### Claude.ai Compatibility Layer (`railway_claude_ai_compatible.py`)
- **Proprietary endpoint support**: `/api/organizations/{org_id}/mcp/start-auth/{auth_id}`
- **Enhanced MCP discovery**: Additional metadata in `.well-known/mcp/resource`
- **Flexible authentication**: Option to bypass OAuth with `CLAUDE_AI_NO_AUTH=true`
- **Request logging**: Special logging for Claude.ai user agent
- **Fallback handling**: Graceful degradation if OAuth not required

### Testing Infrastructure
- **Official MCP client test**: `test_official_mcp_client.py`
- **Authentication flow test**: `test_mcp_auth_flow.py`
- **Comprehensive test plan**: Added to CLAUDE.md

## 📊 Test Results

### Production Server (v0.7.1)
```
✅ Health Check: Server v0.7.1 is healthy
✅ MCP Discovery: Version: 2025-03-26, Transport: ['sse']
✅ OAuth Discovery: Issuer: https://strunz.up.railway.app
✅ Client Registration: Client ID generated
❌ Claude.ai Endpoint: HTTP 404 (pending deployment)
✅ MCP Initialize: Server ready
✅ Tools List: Found 20 tools
✅ Tool Execution: Tools working perfectly
```

**Success Rate**: 87.5% (7/8 tests passed)

## 🔧 Technical Changes

### Files Modified
- `railway-deploy.py` - Uses Claude.ai compatible server
- `src/mcp/claude_compatible_server.py` - Fixed version to 0.7.1
- `src/scripts/deployment/railway_mcp_fixed.py` - Added Claude.ai endpoint
- `src/scripts/deployment/railway_claude_ai_compatible.py` - Full compatibility layer

### Configuration Options
- `CLAUDE_AI_NO_AUTH=true` - Bypass OAuth for Claude.ai
- `RAILWAY_PUBLIC_DOMAIN` - Set public domain for URLs

## 🎬 Next Steps

1. **Monitor deployment**: The Claude.ai compatibility layer is deploying
2. **Test with Claude.ai**: Once deployed, the proprietary endpoint will be available
3. **Fallback plan**: If OAuth is the issue, `CLAUDE_AI_NO_AUTH=true` will bypass it

## 📝 Developer Notes

The investigation revealed that Claude.ai expects a specific authentication flow that differs from standard MCP. This release provides multiple strategies to accommodate Claude.ai's requirements while maintaining standard MCP compatibility.

### Key Insight
Standard MCP servers work perfectly with the protocol, but Claude.ai adds proprietary endpoints that must be implemented separately. This is likely for their internal authentication and routing system.

---

**Full Changelog**: [v0.7.1...v0.7.2](https://github.com/longevitycoach/StrunzKnowledge/compare/v0.7.1...v0.7.2)