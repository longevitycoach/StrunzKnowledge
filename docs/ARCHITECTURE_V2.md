# StrunzKnowledge MCP Server v2.0.0 Architecture

## 🚨 Major Architecture Change (July 2025)

We have completely rewritten the MCP server implementation to use **ONLY** the official MCP Python SDK. This fixes fundamental issues with our previous custom implementation.

## What Changed

### ❌ Old Architecture (v1.x - DEPRECATED)
- Custom FastAPI/SSE implementation (`claude_compatible_server.py`)
- Manual JSON-RPC protocol handling
- Mixed implementations across multiple files
- **Result**: Didn't work with MCP Inspector or Claude.ai

### ✅ New Architecture (v2.0.0)
- Official MCP Python SDK for ALL transports
- Single unified codebase
- Proper protocol compliance
- **Result**: Works with MCP Inspector, Claude.ai, and Claude Desktop

## File Structure

```
src/mcp/
├── mcp_server_clean.py    # Core MCP server using official SDK
├── sse_server.py          # SSE transport wrapper using Starlette
└── [old files]            # To be deleted after deployment
```

## How It Works

### 1. Core Server (`mcp_server_clean.py`)
```python
from mcp.server import Server
import mcp.types as types

# Create server
app = Server("strunz-knowledge")

# Define tools
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [...]

# Handle tool calls
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # Tool implementation
```

### 2. SSE Transport (`sse_server.py`)
```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette

# Create SSE transport
sse_transport = SseServerTransport("/messages/")

# Handle SSE connections
async def handle_sse(request):
    async with sse_transport.connect_sse(...) as streams:
        await app.run(streams[0], streams[1], options)
```

### 3. Main Entry Point (`main.py`)
- Detects environment (local vs Railway)
- Chooses transport (stdio vs SSE)
- Runs appropriate server

## Key Differences

| Aspect | Old (v1.x) | New (v2.0.0) |
|--------|------------|--------------|
| **Protocol** | Custom implementation | Official MCP SDK |
| **SSE Handling** | Manual EventSourceResponse | MCP SseServerTransport |
| **Message Routing** | Manual JSON parsing | SDK handles everything |
| **Session Management** | Custom session dict | SDK managed |
| **Error Handling** | Manual try/catch | SDK error protocols |

## Deployment

### Local (Claude Desktop)
```bash
python main.py  # Uses stdio transport
```

### Railway (Claude.ai)
```bash
MCP_TRANSPORT=sse python main.py  # Uses SSE transport
```

## Testing

### With MCP Inspector
```bash
npx @modelcontextprotocol/inspector http://localhost:8000/sse
```

### With Claude.ai
1. Add server URL: `https://strunz.up.railway.app/sse`
2. Server should connect without errors
3. Tools should be available

## Migration Notes

### For Developers
1. Delete all old MCP implementations after v2.0.0 is stable
2. Use only official MCP SDK going forward
3. Don't try to implement custom transports

### For Users
- No changes needed
- Server URL remains the same
- All tools work as before

## Lessons Learned

1. **Use the official SDK** - Don't reinvent the wheel
2. **Follow the documentation** - MCP has specific requirements
3. **Test with official tools** - MCP Inspector is the reference
4. **Keep it simple** - Let the SDK handle protocol details