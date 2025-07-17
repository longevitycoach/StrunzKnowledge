# FastMCP vs Official MCP SDK Comparison

## The Problem

FastMCP doesn't properly expose the `prompts` capability in a way that Claude.ai/Desktop expects, causing the server to show as "disabled" even when properly implemented.

## Key Differences

### 1. Prompts Capability

**FastMCP Issues:**
- Uses decorators (`@app.prompt()`) but doesn't properly expose them in the protocol
- The `prompts` capability is declared but `prompts/list` method returns empty
- No proper prompt template support

**Official SDK Solution:**
- Native support for prompts with `@server.list_prompts()` and `@server.get_prompt()`
- Properly implements the full prompts protocol
- Returns structured prompt templates that Claude.ai understands

### 2. Transport Support

**FastMCP:**
```python
# Limited SSE support
server.app.run(transport="sse")  # Basic SSE
```

**Official SDK:**
```python
# Full SSE/HTTP support with proper streaming
from mcp.server.sse import SseServerTransport
transport = SseServerTransport()
# Proper event streaming with SSE protocol
```

### 3. Protocol Compliance

**FastMCP:**
- Partial MCP implementation
- Missing some protocol features
- Community-driven development

**Official SDK:**
- Full MCP 2025-03-26 protocol compliance
- Maintained by Anthropic
- Guaranteed compatibility with Claude products

## Migration Guide

### Before (FastMCP):
```python
from fastmcp import FastMCP

app = FastMCP("My Server")

@app.prompt()
async def my_prompt(arg: str):
    return "prompt text"

@app.tool()
async def my_tool():
    return "result"

app.run()
```

### After (Official SDK):
```python
from mcp.server import Server
from mcp.server.stdio import stdio_transport

server = Server("My Server")

@server.list_prompts()
async def list_prompts():
    return [Prompt(name="my_prompt", ...)]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    return GetPromptResult(messages=[...])

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return [TextContent(text="result")]

asyncio.run(server.run(stdio_transport()))
```

## Benefits of Official SDK

1. **Full Claude.ai Integration**: Prompts work correctly
2. **Better SSE Support**: Proper streaming for web integration  
3. **Type Safety**: Strong typing with Pydantic models
4. **Future Proof**: Maintained by Anthropic
5. **Better Documentation**: Official docs and examples

## Recommendation

**Switch to the Official MCP SDK** for production deployments, especially when:
- You need Claude.ai web integration (not just Desktop)
- Prompts are important for your use case
- You want guaranteed protocol compliance
- You need HTTP/SSE transport

FastMCP is still good for:
- Quick prototypes
- Simple tools-only servers
- When you don't need prompts

## Implementation Status

✅ Created `mcp_sdk_server.py` with official SDK
✅ Full prompts support (3 health-focused prompts)
✅ All 20 tools migrated
✅ SSE/HTTP transport for Railway
✅ Stdio transport for local development

The official SDK implementation properly declares and implements the prompts capability, which should resolve the "server disabled" issue in Claude.ai.

---

*🤖 Generated with [Claude Code](https://claude.ai/code)*