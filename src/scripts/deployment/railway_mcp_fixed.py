#!/usr/bin/env python3
"""
Fixed Railway MCP Server with Proper Tool Handling
Combines OAuth/SSE from claude_compatible_server with proper MCP tool execution
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our components
from src.scripts.startup.preload_vector_store import preload_vector_store
from src.mcp.enhanced_server import tool_registry
from src.mcp.claude_compatible_server import (
    health_check,
    oauth_metadata,
    oauth_protected_resource,
    register_client,
    authorize,
    authorize_post,
    token_endpoint,
    railway_health
)

# Create FastAPI app
app = FastAPI(
    title="Dr. Strunz Knowledge MCP Server",
    version="0.7.1",
    description="Fixed MCP server with proper tool handling"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global tool registry reference
_tool_registry = None

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    global _tool_registry
    logger.info("Starting Fixed Railway MCP Server v0.7.1")
    
    # Preload vector store
    try:
        await preload_vector_store()
        logger.info("Vector store preloaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload vector store: {e}")
    
    # Store tool registry
    _tool_registry = tool_registry
    logger.info(f"Loaded {len(tool_registry)} tools")

# Health endpoints
app.get("/")(health_check)
app.get("/health")(health_check)
app.get("/railway-health")(railway_health)

# OAuth endpoints
app.get("/.well-known/oauth-authorization-server")(oauth_metadata)
app.get("/.well-known/oauth-protected-resource")(oauth_protected_resource)
app.post("/oauth/register")(register_client)
app.get("/oauth/authorize")(authorize)
app.post("/oauth/authorize")(authorize_post)
app.post("/oauth/token")(token_endpoint)

# MCP resource discovery
@app.get("/.well-known/mcp/resource")
async def mcp_resource():
    """MCP resource discovery endpoint"""
    return JSONResponse({
        "mcpVersion": "2025-03-26",
        "transport": ["sse"],
        "endpoints": {
            "sse": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}/sse",
            "messages": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}/messages"
        },
        "authentication": {
            "type": "oauth2",
            "oauth2": {
                "authorizationUrl": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}/oauth/authorize",
                "tokenUrl": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}/oauth/token",
                "scopes": {
                    "read": "Read access to knowledge base",
                    "write": "Write access (not implemented)"
                }
            }
        }
    })

# SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication"""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        # Send initial connection ready
        yield f"event: message\ndata: {json.dumps({'jsonrpc': '2.0', 'method': 'connection/ready', 'params': {'sessionId': 'fixed-session'}})}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Messages endpoint with proper tool handling
@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle MCP messages via HTTP POST with tool execution"""
    try:
        body = await request.json()
        method = body.get("method", "")
        
        # Handle different MCP methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": "Dr. Strunz Knowledge MCP Server",
                        "version": "0.7.1"
                    }
                },
                "id": body.get("id")
            })
        
        elif method == "tools/list":
            # List all available tools
            tools = []
            for name, func in _tool_registry.items():
                tools.append({
                    "name": name,
                    "description": (func.__doc__ or "").strip() or f"Tool: {name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": True
                    }
                })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {"tools": tools},
                "id": body.get("id")
            })
        
        elif method == "tools/call":
            # Execute tool
            params = body.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name in _tool_registry:
                try:
                    # Execute the tool
                    tool_func = _tool_registry[tool_name]
                    
                    # Handle async functions
                    if asyncio.iscoroutinefunction(tool_func):
                        result = await tool_func(**tool_args)
                    else:
                        result = tool_func(**tool_args)
                    
                    # Format result
                    if isinstance(result, dict):
                        content = [{
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }]
                    else:
                        content = [{
                            "type": "text",
                            "text": str(result)
                        }]
                    
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "result": {"content": content},
                        "id": body.get("id")
                    })
                    
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}"
                        },
                        "id": body.get("id")
                    })
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    },
                    "id": body.get("id")
                })
        
        elif method == "prompts/list":
            # List prompts
            prompts = [
                {
                    "name": "health_assessment",
                    "description": "Comprehensive health assessment questionnaire",
                    "arguments": [
                        {"name": "symptoms", "description": "Current symptoms", "required": True},
                        {"name": "history", "description": "Medical history", "required": False}
                    ]
                },
                {
                    "name": "supplement_protocol",
                    "description": "Create personalized supplement protocol",
                    "arguments": [
                        {"name": "goals", "description": "Health goals", "required": True},
                        {"name": "conditions", "description": "Existing conditions", "required": False}
                    ]
                },
                {
                    "name": "nutrition_optimization",
                    "description": "Optimize nutrition based on Dr. Strunz principles",
                    "arguments": [
                        {"name": "current_diet", "description": "Current dietary habits", "required": True},
                        {"name": "objectives", "description": "Nutrition objectives", "required": True}
                    ]
                }
            ]
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {"prompts": prompts},
                "id": body.get("id")
            })
        
        else:
            # Unknown method
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": body.get("id")
            })
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": body.get("id") if "body" in locals() else None
        }, status_code=500)

def main():
    """Main entry point"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Public domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    logger.info("Fixed MCP server with proper tool execution")
    
    # Run server
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()