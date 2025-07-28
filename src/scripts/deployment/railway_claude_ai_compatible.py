#!/usr/bin/env python3
"""
Claude.ai Compatible MCP Server
This server implements Claude.ai's specific requirements on top of standard MCP
"""

import os
import sys
import asyncio
import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our components
from src.scripts.startup.preload_vector_store import preload_vector_store

# Initialize simple tool registry for testing
def get_mcp_server_purpose():
    """Get information about this MCP server"""
    return {
        "name": "Dr. Strunz Knowledge MCP Server",
        "version": "0.7.9",
        "purpose": "Claude.ai compatible MCP server with health and nutrition tools",
        "endpoint_test": "Claude.ai endpoint working"
    }

def get_dr_strunz_biography():
    """Get Dr. Strunz's biography"""
    return {
        "name": "Dr. Ulrich Strunz",
        "specialty": "Molecular medicine and nutritional therapy",
        "books": "13 books on health, nutrition, and longevity",
        "approach": "Evidence-based preventive medicine"
    }

# Simple tool registry for testing
_tool_registry = {
    "get_mcp_server_purpose": get_mcp_server_purpose,
    "get_dr_strunz_biography": get_dr_strunz_biography,
}

logger.info(f"Loaded {len(_tool_registry)} tools (simple registry for Claude.ai testing)")
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
    title="Dr. Strunz Knowledge MCP Server (Claude.ai Compatible)",
    version="0.7.9",
    description="MCP server with Claude.ai specific compatibility"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client storage
_claude_clients = {}  # Store Claude.ai client registrations
# Note: _tool_registry is already initialized above with simple tools

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info("Starting Claude.ai Compatible MCP Server v0.7.9")
    
    # Preload vector store
    try:
        await preload_vector_store()
        logger.info("Vector store preloaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload vector store: {e}")
    
    # Tool registry already loaded globally
    if _tool_registry is not None:
        logger.info(f"Loaded {len(_tool_registry)} tools")
    else:
        logger.error("Tool registry is None - tools not available")

# Health endpoints
app.get("/")(health_check)
app.get("/health")(health_check)
app.get("/railway-health")(railway_health)

# Standard OAuth endpoints
app.get("/.well-known/oauth-authorization-server")(oauth_metadata)
app.get("/.well-known/oauth-protected-resource")(oauth_protected_resource)
app.post("/oauth/register")(register_client)
app.get("/oauth/authorize")(authorize)
app.post("/oauth/authorize")(authorize_post)
app.post("/oauth/token")(token_endpoint)

# MCP resource discovery - DISABLED for Claude.ai compatibility
# The working bloodtest-mcp-server has NO resource discovery endpoint
# @app.get("/.well-known/mcp/resource")
# async def mcp_resource():
#     """Enhanced MCP resource discovery for Claude.ai"""
#     base_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}"
#     
#     return JSONResponse({
#         "mcpVersion": "2025-03-26",
#         "serverInfo": {
#             "name": "Dr. Strunz Knowledge MCP Server",
#             "version": "0.7.9",
#             "vendor": "Longevity Coach"
#         },
#         "transport": ["sse", "http"],
#         "endpoints": {
#             "sse": f"{base_url}/sse",
#             "messages": f"{base_url}/messages",
#             "tools": f"{base_url}/tools",
#             "prompts": f"{base_url}/prompts"
#         },
#         "authentication": {
#             "type": "oauth2",
#             "required": False,  # Claude.ai might not require auth
#             "oauth2": {
#                 "authorizationUrl": f"{base_url}/oauth/authorize",
#                 "tokenUrl": f"{base_url}/oauth/token",
#                 "registrationUrl": f"{base_url}/oauth/register",
#                 "scopes": {
#                     "read": "Read access to knowledge base",
#                     "write": "Write access (not implemented)"
#                 }
#             }
#         },
#         "capabilities": {
#             "tools": True,
#             "prompts": True,
#             "resources": False,
#             "sampling": False
#         }
#     })

# Claude.ai specific authentication endpoint
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(
    org_id: str, 
    auth_id: str,
    redirect_url: Optional[str] = Query(None),
    open_in_browser: Optional[int] = Query(None)
):
    """Claude.ai specific authentication endpoint"""
    logger.info(f"Claude.ai auth: org={org_id}, auth={auth_id}, redirect={redirect_url}, browser={open_in_browser}")
    
    # Store Claude.ai client info
    client_id = f"claude_{auth_id[:16]}"
    _claude_clients[client_id] = {
        "org_id": org_id,
        "auth_id": auth_id,
        "redirect_url": redirect_url,
        "created_at": datetime.now().isoformat()
    }
    
    # Option 1: Return success directly (no OAuth needed)
    if os.environ.get("CLAUDE_AI_NO_AUTH", "true").lower() == "true":
        return JSONResponse({
            "status": "success",
            "server_url": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}",
            "auth_not_required": True,
            "message": "MCP server ready for use"
        })
    
    # Option 2: Redirect to OAuth flow
    oauth_redirect = redirect_url or "https://claude.ai/api/callback"
    oauth_params = {
        "client_id": client_id,
        "redirect_uri": oauth_redirect,
        "response_type": "code",
        "state": auth_id,
        "scope": "read"
    }
    
    # Build OAuth URL
    oauth_url = f"/oauth/authorize?" + "&".join([f"{k}={v}" for k, v in oauth_params.items()])
    
    return RedirectResponse(url=oauth_url, status_code=302)

# Claude.ai callback endpoint
@app.get("/api/callback")
async def claude_ai_callback(code: str = None, state: str = None, error: str = None):
    """Handle OAuth callback for Claude.ai"""
    if error:
        return JSONResponse({"error": error}, status_code=400)
    
    return JSONResponse({
        "status": "success",
        "code": code,
        "state": state,
        "message": "Authentication successful"
    })

# Enhanced messages endpoint with better error handling
@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle MCP messages with Claude.ai compatibility"""
    try:
        body = await request.json()
        method = body.get("method", "")
        
        # Log Claude.ai requests for debugging
        if "claude" in request.headers.get("user-agent", "").lower():
            logger.info(f"Claude.ai request: {method}")
        
        # Handle different MCP methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "sampling": {}
                    },
                    "serverInfo": {
                        "name": "Dr. Strunz Knowledge MCP Server",
                        "version": "0.7.9",
                        "vendor": "Longevity Coach"
                    }
                },
                "id": body.get("id")
            })
        
        elif method == "tools/list":
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
            params = body.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if _tool_registry and tool_name in _tool_registry:
                try:
                    tool_func = _tool_registry[tool_name]
                    
                    # Execute tool (functions should already be extracted)
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
            # Log unknown methods from Claude.ai
            if "claude" in request.headers.get("user-agent", "").lower():
                logger.warning(f"Unknown Claude.ai method: {method}")
            
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

# SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication"""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        # Send initial connection ready
        session_id = str(uuid.uuid4())
        yield f"event: message\ndata: {json.dumps({'jsonrpc': '2.0', 'method': 'connection/ready', 'params': {'sessionId': session_id}})}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"event: ping\ndata: {json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

async def main():
    """Main entry point"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Public domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    logger.info("Claude.ai compatible MCP server with enhanced endpoints")
    
    # Run server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())