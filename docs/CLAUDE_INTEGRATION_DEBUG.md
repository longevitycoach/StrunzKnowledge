# Claude.ai & Claude Desktop Integration Debugging Guide

## Where to Find Logs

### 1. Claude.ai (Web) Logs
Unfortunately, Claude.ai (web version) doesn't provide direct access to MCP connection logs. However, you can:

1. **Browser Developer Console**:
   - Open Chrome/Firefox Developer Tools (F12)
   - Go to the Network tab
   - Look for requests to `strunz.up.railway.app`
   - Check the Console tab for any JavaScript errors

2. **OAuth Flow Inspection**:
   - In Network tab, filter by `oauth`
   - Look for these endpoints:
     - `/.well-known/oauth-authorization-server` (should return 200)
     - `/oauth/authorize` (should return 307 redirect)
     - `/oauth/token` (should return 200)

### 2. Claude Desktop Logs (Better for Debugging)

Claude Desktop provides much better debugging capabilities:

#### macOS Log Location:
```bash
# Claude Desktop logs
~/Library/Logs/Claude/

# Or in Terminal:
tail -f ~/Library/Logs/Claude/main.log
tail -f ~/Library/Logs/Claude/mcp-*.log
```

#### Windows Log Location:
```
%APPDATA%\Claude\logs\
```

#### Linux Log Location:
```
~/.config/Claude/logs/
```

### 3. Enable Debug Logging in Claude Desktop

1. **Edit Claude Desktop Config**:
   ```json
   {
     "mcpServers": {
       "strunz": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-sse", "https://strunz.up.railway.app/sse"],
         "env": {
           "DEBUG": "mcp:*",
           "LOG_LEVEL": "debug"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop** after config changes

## Common Issues & Solutions

### Issue 1: "MCP Server is disabled" in Claude.ai

**Possible Causes**:
1. **Caching**: Claude.ai might cache server status
2. **Session State**: Previous failed connection attempts
3. **OAuth Token**: Expired or invalid OAuth token

**Solutions**:
1. **Clear Claude.ai Cache**:
   - Log out of Claude.ai
   - Clear browser cache/cookies for claude.ai
   - Log back in and try reconnecting

2. **Force Reconnection**:
   - Remove the MCP server from Claude.ai
   - Wait 1-2 minutes
   - Add it again with fresh URL

3. **Test OAuth Flow Manually**:
   ```bash
   # Test OAuth discovery
   curl https://strunz.up.railway.app/.well-known/oauth-authorization-server
   
   # Should show OAuth endpoints
   ```

### Issue 2: SSE Connection Issues

**Test SSE Endpoint**:
```bash
# Test SSE connection
curl -N https://strunz.up.railway.app/sse

# Should show:
# data: {"type": "message", "data": "Connected to Dr. Strunz Knowledge MCP Server"}
```

## Railway Logs Analysis

From your Railway logs, we can see:
1. ✅ OAuth discovery working (200 OK)
2. ✅ OAuth authorize endpoint working (307 redirect - expected)
3. ✅ OAuth token exchange working (200 OK)
4. ✅ Multiple successful connections from Claude.ai

The 307 redirect is **normal** - it's part of the OAuth authorization flow.

## Debug Steps for Claude Desktop

1. **Install SSE Server**:
   ```bash
   npm install -g @modelcontextprotocol/server-sse
   ```

2. **Test Connection Manually**:
   ```bash
   npx @modelcontextprotocol/server-sse https://strunz.up.railway.app/sse
   ```

3. **Add to Claude Desktop Config**:
   ```json
   {
     "mcpServers": {
       "strunz": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-sse", "https://strunz.up.railway.app/sse"]
       }
     }
   }
   ```

4. **Check Logs**:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp-strunz.log
   ```

## What to Look For in Logs

### Successful Connection:
```
[MCP] Connecting to server: strunz
[MCP] Server initialized with capabilities: tools, prompts
[MCP] Available tools: 20
```

### Failed Connection:
```
[MCP] Connection failed: [error details]
[MCP] Server capabilities missing: prompts
```

## Alternative: Direct MCP Connection (No OAuth)

If OAuth continues to cause issues, you can try the SSE endpoint directly in Claude Desktop:

```json
{
  "mcpServers": {
    "strunz-direct": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse",
        "https://strunz.up.railway.app/sse"
      ]
    }
  }
}
```

This bypasses OAuth and connects directly via SSE transport.

## Contact Support

If issues persist:
1. **Claude.ai Support**: Use the feedback option in Claude.ai
2. **GitHub Issues**: Report at https://github.com/anthropics/claude-desktop/issues
3. **MCP Community**: https://modelcontextprotocol.io/community

---

*🤖 Generated with [Claude Code](https://claude.ai/code)*