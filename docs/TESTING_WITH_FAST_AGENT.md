# Testing Strunz Knowledge MCP Server with Fast Agent

## Overview

Fast Agent is a robust MCP client that provides comprehensive testing capabilities for MCP servers. This guide explains how to test the Strunz Knowledge MCP server using Fast Agent.

## Prerequisites

1. **Install Fast Agent**:
```bash
uv pip install fast-agent-mcp
# or with pip
pip install fast-agent-mcp
```

2. **MCP Inspector** (for debugging):
```bash
npm install -g @modelcontextprotocol/inspector
```

## Testing Configurations

### 1. Local Testing with stdio Transport

```python
# test_fast_agent_stdio.py
import fast_agent as fast

@fast.agent(
    instruction="You have access to Dr. Strunz's knowledge base. Help users with health questions.",
    mcp_servers={
        "strunz": {
            "command": "python",
            "args": ["-m", "src.mcp.fastmcp_server"]
        }
    }
)
async def health_assistant():
    async with fast.run() as agent:
        # Test knowledge search
        result = await agent.use_mcp_tool(
            server="strunz",
            tool="knowledge_search",
            arguments={"query": "Vitamin D", "limit": 5}
        )
        print(f"Search results: {result}")
        
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    import asyncio
    asyncio.run(health_assistant())
```

### 2. Remote Testing with SSE Transport

```python
# test_fast_agent_sse.py
import fast_agent as fast

@fast.agent(
    instruction="You have access to Dr. Strunz's knowledge base via SSE.",
    mcp_servers={
        "strunz-remote": {
            "transport": "sse",
            "url": "https://strunz.up.railway.app/sse",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN"  # If auth is required
            }
        }
    }
)
async def remote_health_assistant():
    async with fast.run() as agent:
        # Test connection
        status = await agent.use_mcp_tool(
            server="strunz-remote",
            tool="test_connection"
        )
        print(f"Connection status: {status}")
        
        # Test biography tool
        bio = await agent.use_mcp_tool(
            server="strunz-remote",
            tool="get_dr_strunz_biography"
        )
        print(f"Biography: {bio}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(remote_health_assistant())
```

### 3. Testing with HTTP Transport

```python
# test_fast_agent_http.py
import fast_agent as fast

@fast.agent(
    instruction="Test HTTP transport for MCP server",
    mcp_servers={
        "strunz-http": {
            "transport": "http",
            "url": "http://localhost:8000/mcp"
        }
    }
)
async def http_test():
    async with fast.run() as agent:
        # List available tools
        await agent.interactive()

if __name__ == "__main__":
    import asyncio
    asyncio.run(http_test())
```

## Testing Workflows

### 1. Chain Workflow for Health Analysis

```python
# test_health_workflow.py
import fast_agent as fast

@fast.agent(
    name="symptom_analyzer",
    instruction="Analyze symptoms using Dr. Strunz knowledge base",
    mcp_servers={
        "strunz": {
            "command": "python",
            "args": ["-m", "src.mcp.fastmcp_server"]
        }
    }
)
async def analyze_symptoms(symptoms: str):
    # Search for related information
    return await agent.use_mcp_tool(
        server="strunz",
        tool="knowledge_search",
        arguments={"query": symptoms}
    )

@fast.agent(
    name="protocol_creator",
    instruction="Create health protocol based on analysis"
)
async def create_protocol(analysis: dict):
    return await agent.use_mcp_tool(
        server="strunz",
        tool="create_health_protocol",
        arguments={"condition": analysis.get("condition")}
    )

@fast.chain(
    name="health_advisor",
    sequence=["symptom_analyzer", "protocol_creator"]
)
async def health_advisor_workflow():
    async with fast.run() as workflow:
        result = await workflow.run("fatigue and low energy")
        print(result)
```

### 2. Parallel Testing

```python
# test_parallel.py
import fast_agent as fast

@fast.parallel(
    name="comprehensive_test",
    agents={
        "search_test": lambda: test_search(),
        "protocol_test": lambda: test_protocols(),
        "bio_test": lambda: test_biography()
    }
)
async def run_all_tests():
    async with fast.run() as parallel:
        results = await parallel.run()
        for name, result in results.items():
            print(f"{name}: {result}")
```

## MCP Inspector Testing

1. **Start MCP Inspector**:
```bash
mcp-inspector
```

2. **Configure for SSE**:
```json
{
  "mcpServers": {
    "strunz-sse": {
      "transport": "sse",
      "url": "https://strunz.up.railway.app/sse"
    }
  }
}
```

3. **Test Tools**:
- Use the inspector UI to test individual tools
- Monitor SSE events
- Debug protocol messages

## Running Tests

### Local Development
```bash
# Start local FastMCP server
MCP_TRANSPORT=sse PORT=8000 python -m src.mcp.fastmcp_server

# In another terminal, run Fast Agent tests
python test_fast_agent_sse.py
```

### Production Testing
```bash
# Test against Railway deployment
python test_fast_agent_sse.py
```

## Debugging Tips

1. **Enable Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Check Server Status**:
```bash
curl https://strunz.up.railway.app/
```

3. **Monitor SSE Events**:
```bash
curl -N -H "Accept: text/event-stream" https://strunz.up.railway.app/sse
```

## Expected Results

- ✅ Connection established via SSE
- ✅ Tools listed correctly
- ✅ Knowledge search returns results
- ✅ Protocol generation works
- ✅ Biography retrieval successful

## Troubleshooting

1. **Connection Refused**: Check if server is running and port is correct
2. **Authentication Error**: Verify Bearer token if required
3. **Tool Not Found**: Ensure FastMCP server has all tools registered
4. **SSE Timeout**: Check firewall and CORS settings