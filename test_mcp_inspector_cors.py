#!/usr/bin/env python3
"""
Test MCP server with CORS headers for Inspector
"""

import os
import sys
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="MCP Test Server with CORS")

# Add CORS middleware - this is what's missing!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Session management
sessions = {}

# Simple tool for testing
TOOLS = [
    {
        "name": "test_tool",
        "description": "A simple test tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Test message"}
            },
            "required": ["message"]
        }
    }
]

@app.get("/")
async def health_check():
    """Health check"""
    return JSONResponse({
        "status": "ok",
        "service": "MCP Test Server with CORS",
        "cors": "enabled"
    })

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint with CORS support"""
    
    logger.info(f"SSE connection from: {request.headers.get('origin', 'unknown')}")
    logger.info(f"User-Agent: {request.headers.get('user-agent', 'unknown')}")
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created": datetime.utcnow().isoformat(),
        "initialized": False
    }
    
    async def event_generator():
        """Generate SSE events"""
        try:
            # Send endpoint event
            yield {
                "event": "endpoint",
                "data": f"/messages/?session_id={session_id}"
            }
            
            # Keep alive
            while True:
                await asyncio.sleep(15)
                yield {
                    "event": "ping",
                    "data": datetime.utcnow().isoformat()
                }
                
        except asyncio.CancelledError:
            logger.info(f"SSE connection closed: {session_id}")
            if session_id in sessions:
                del sessions[session_id]
            raise
    
    # Important: Set headers for SSE
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # Disable Nginx buffering
        "Access-Control-Allow-Origin": "*"  # Explicit CORS header
    }
    
    return EventSourceResponse(event_generator(), headers=headers)

@app.post("/messages")
@app.post("/messages/")
async def messages_endpoint(request: Request, session_id: Optional[str] = Query(None)):
    """Handle MCP messages"""
    
    try:
        data = await request.json()
        method = data.get("method")
        msg_id = data.get("id", "1")
        
        logger.info(f"MCP request: {method}")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": "MCP Test Server",
                        "version": "1.0.0"
                    }
                }
            }
            return JSONResponse(response)
            
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            }
            return JSONResponse(response)
            
        elif method == "tools/call":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": "Test response"}]
                }
            }
            return JSONResponse(response)
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id", "1"),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        })

# Add OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MCP test server with CORS support on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)