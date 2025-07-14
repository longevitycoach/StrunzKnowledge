#!/usr/bin/env python3
"""
Simple test server for running the enhanced MCP server without FastMCP dependency
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Create the enhanced server directly
from src.mcp.enhanced_server import StrunzKnowledgeMCP

# Create FastAPI app
app = FastAPI()

# Create the MCP server instance
mcp_server = StrunzKnowledgeMCP()

@app.get("/")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "Enhanced Dr. Strunz Knowledge MCP Server",
        "version": "1.0.0",
        "mcp_tools": len(mcp_server.tool_registry),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint for monitoring"""
    async def event_generator():
        while True:
            yield f"data: {json.dumps({'status': 'alive', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(30)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP endpoint for tool calls"""
    try:
        data = await request.json()
        
        if data.get("method") == "tools/call":
            tool_name = data["params"]["name"]
            args = data["params"].get("arguments", {})
            
            # Call the tool using the registry
            if tool_name in mcp_server.tool_registry:
                tool_func = mcp_server.tool_registry[tool_name]
                result = await tool_func(**args)
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": data.get("id")
                })
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    },
                    "id": data.get("id")
                })
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method '{data.get('method')}' not supported"
                },
                "id": data.get("id")
            })
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": data.get("id") if "data" in locals() else None
        })

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting Enhanced MCP server on port {port}...")
    print("Available endpoints:")
    print(f"  - Health: http://localhost:{port}/")
    print(f"  - SSE: http://localhost:{port}/sse")
    print(f"  - MCP: http://localhost:{port}/mcp")
    print(f"  - Tools available: {len(mcp_server.tool_registry)}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)