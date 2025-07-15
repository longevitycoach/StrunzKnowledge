#!/usr/bin/env python3
"""
Public MCP SSE Server for Claude.ai Integration
Provides unauthenticated SSE endpoint for testing Claude.ai remote server support
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Dr. Strunz Knowledge MCP Server")

# Add CORS for Claude.ai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import enhanced MCP server
enhanced_mcp_server = None
try:
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    enhanced_mcp_server = StrunzKnowledgeMCP()
    logger.info("Enhanced MCP server initialized")
except Exception as e:
    logger.error(f"Failed to initialize enhanced MCP server: {e}")

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "server": "Dr. Strunz Knowledge MCP Server",
        "version": "0.3.0",
        "timestamp": datetime.now().isoformat(),
        "transport": "sse",
        "mcp_tools": len(enhanced_mcp_server.tool_registry) if enhanced_mcp_server else 0
    })

@app.get("/sse")
async def sse_mcp_endpoint(request: Request):
    """
    SSE endpoint for MCP communication.
    Implements MCP protocol over Server-Sent Events.
    """
    logger.info("SSE connection established")
    
    async def event_generator():
        """Generate SSE events for MCP protocol."""
        try:
            # Send connection event
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "method": "connection.ready",
                    "params": {
                        "server": "Dr. Strunz Knowledge MCP Server",
                        "version": "0.3.0",
                        "capabilities": {
                            "tools": True,
                            "prompts": False,
                            "resources": False
                        }
                    }
                })
            }
            
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield {
                    "event": "ping",
                    "data": json.dumps({"timestamp": datetime.now().isoformat()})
                }
                
        except asyncio.CancelledError:
            logger.info("SSE connection cancelled")
            raise
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP JSON-RPC endpoint."""
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id", 1)
        
        logger.info(f"MCP request: {method}")
        
        # Handle MCP methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    }
                },
                "id": request_id
            })
            
        elif method == "tools/list":
            tools = []
            if enhanced_mcp_server:
                for name, func in enhanced_mcp_server.tool_registry.items():
                    tools.append({
                        "name": name,
                        "description": func.__doc__ or f"Tool: {name}",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {"tools": tools},
                "id": request_id
            })
            
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            
            if enhanced_mcp_server and tool_name in enhanced_mcp_server.tool_registry:
                try:
                    tool_func = enhanced_mcp_server.tool_registry[tool_name]
                    result = await tool_func(**tool_args)
                    
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": request_id
                    })
                except Exception as e:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}"
                        },
                        "id": request_id
                    })
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    },
                    "id": request_id
                })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            })
            
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": 1
        })

async def main():
    """Run the public SSE server."""
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting public MCP SSE server on port {port}")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())