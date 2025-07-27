# MCP SSE Implementation Fix for Claude.ai

## Problem Summary

The StrunzKnowledge MCP server shows "NO PROVIDED TOOLS" in Claude.ai despite the server reporting tools. The issue stems from fundamental implementation errors in how tools are exposed via the SSE transport.

## Root Causes

### 1. Incorrect Tool Registry Pattern

**Current (Wrong):**
```python
# Trying to extract handler methods as tools
for tool_name in dir(server_instance):
    if tool_name.startswith('_handle_'):
        actual_name = tool_name.replace('_handle_', '')
        tool_registry[actual_name] = getattr(server_instance, tool_name)
```

**Issue:** The MCP SDK doesn't expose tools this way. Tools are defined in the `list_tools()` decorator, not as individual handler methods.

### 2. Incorrect Tool Schema Generation

**Current (Wrong):**
```python
tools.append({
    "name": name,
    "description": (func.__doc__ or "").strip() or f"Tool: {name}",
    "inputSchema": {
        "type": "object",
        "properties": {},  # Empty properties!
        "additionalProperties": True
    }
})
```

**Issue:** Empty property schemas prevent Claude.ai from understanding how to call the tools.

### 3. Missing Proper SSE Message Flow

The current implementation doesn't properly handle the SSE initialization flow that Claude.ai expects:
- POST to /sse with initialization request
- Proper JSON-RPC message formatting
- Correct event types and data structure

## Solution

### 1. Proper Tool Definition

Tools must be properly defined with complete schemas:

```python
{
    "name": "knowledge_search",
    "description": "Search through Dr. Strunz's knowledge base",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "limit": {
                "type": "integer",
                "description": "Number of results",
                "default": 10
            }
        },
        "required": ["query"]
    }
}
```

### 2. Correct SSE Implementation

```python
@app.post("/sse")
async def sse_endpoint(request: Request):
    # Handle POST initialization
    init_request = await request.json()
    
    async def event_generator():
        if init_request.get("method") == "initialize":
            # Send proper initialization response
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "id": init_request.get("id"),
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {
                            "tools": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "Server Name",
                            "version": "1.0.0"
                        }
                    }
                })
            }
```

### 3. Proper Tool Extraction from MCP SDK

Instead of trying to extract handler methods, we need to:

1. **Call the SDK's list_tools handler directly**
2. **Convert the SDK's tool format to Claude.ai's expected format**
3. **Ensure all tool schemas are complete**

```python
# Get tools from MCP SDK server
async def get_sdk_tools():
    """Extract tools from the MCP SDK server"""
    if hasattr(server_instance.server, 'list_tools'):
        # Call the list_tools handler
        tools_handler = server_instance.server._tool_list_handler
        if tools_handler:
            sdk_tools = await tools_handler()
            # Convert to Claude.ai format
            return [convert_tool_format(tool) for tool in sdk_tools]
    return []
```

## Testing Steps

### 1. Local Testing with MCP Inspector

```bash
# Run the test server
python src/mcp/test_sse_server.py

# In another terminal, run the test script
python src/scripts/test_mcp_inspector.py
```

Then:
1. Open https://inspector.mcp.run/
2. Select "SSE" transport
3. Enter URL: http://localhost:8000/sse
4. Click "Connect"
5. Verify tools appear

### 2. Claude.ai Testing

1. Deploy the fixed server to Railway
2. Add to Claude.ai with the public URL
3. Tools should now appear properly

## Key Differences from Working Servers

Working MCP servers (like bloodtest-mcp-server) follow these patterns:

1. **Complete tool schemas** with all properties defined
2. **Proper SSE message flow** handling both GET and POST
3. **Correct JSON-RPC formatting** throughout
4. **Tool execution returns proper content structure**

## Implementation Checklist

- [ ] Fix tool extraction from MCP SDK
- [ ] Implement proper SSE message handling
- [ ] Add complete input schemas for all tools
- [ ] Test with MCP Inspector
- [ ] Deploy and test with Claude.ai
- [ ] Verify all 20 tools appear and work

## References

- [MCP Python SDK SSE Transport](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/sse.py)
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs/concepts/transports)
- [Working MCP Server Examples](https://github.com/modelcontextprotocol/servers)