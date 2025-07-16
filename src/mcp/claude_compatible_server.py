#!/usr/bin/env python3
"""
Claude.ai Compatible MCP Server
Uses protocol version 2025-03-26 with SSE transport (2024-11-05 style)
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, Header, Depends, Query, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse
import uvicorn

logger = logging.getLogger(__name__)

# Protocol version that Claude.ai supports
PROTOCOL_VERSION = "2025-03-26"

# Debug: Log when server starts
logger.info("=== CLAUDE COMPATIBLE SERVER v0.5.0 WITH OAUTH ENDPOINTS ===")
logger.info("This version includes OAuth endpoints for Claude.ai")

# Create FastAPI app
app = FastAPI(title="Dr. Strunz Knowledge MCP Server")

# Add CORS for Claude.ai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "https://*.claude.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Session storage
sessions: Dict[str, Dict] = {}

# Import enhanced server tools
enhanced_server = None
tool_registry = {}
try:
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    enhanced_server = StrunzKnowledgeMCP()
    tool_registry = enhanced_server.tool_registry
    logger.info(f"Loaded {len(tool_registry)} tools")
except Exception as e:
    logger.error(f"Failed to load tools: {e}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication"""
    if credentials:
        # In production, validate the token here
        return {"user": "authenticated"}
    return None


@app.get("/")
@app.head("/")
@app.post("/")
async def health_check():
    """Health check endpoint - supports GET, HEAD, and POST"""
    # Debug: Check if OAuth endpoints are registered
    routes = [route.path for route in app.routes]
    oauth_routes = [r for r in routes if 'oauth' in r or 'well-known' in r]
    
    return JSONResponse({
        "status": "healthy",
        "server": "Dr. Strunz Knowledge MCP Server",
        "version": "0.5.0",
        "protocol_version": PROTOCOL_VERSION,
        "transport": "sse",
        "tools": len(tool_registry),
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages"
        },
        "debug": {
            "oauth_endpoints_registered": len(oauth_routes),
            "oauth_routes": oauth_routes[:5]  # Show first 5 OAuth routes
        }
    })


@app.get("/sse")
async def sse_endpoint(request: Request, user=Depends(get_current_user)):
    """
    SSE endpoint for Claude.ai MCP communication.
    Uses the older SSE transport that Claude.ai expects.
    """
    logger.info("SSE connection established")
    
    # Create session
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created": datetime.utcnow().isoformat(),
        "user": user,
        "initialized": False
    }
    
    async def event_generator():
        """Generate SSE events for MCP protocol"""
        try:
            # Send initial connection event
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "method": "connection/ready",
                    "params": {
                        "sessionId": session_id
                    }
                })
            }
            
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield {
                    "event": "ping",
                    "data": json.dumps({
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
                
        except asyncio.CancelledError:
            logger.info(f"SSE connection closed for session {session_id}")
            if session_id in sessions:
                del sessions[session_id]
            raise
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@app.post("/messages")
async def messages_endpoint(request: Request, user=Depends(get_current_user)):
    """
    Messages endpoint for MCP requests.
    Claude.ai sends requests here while maintaining SSE connection.
    """
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id")
        
        logger.info(f"MCP request: {method}")
        
        # Handle different methods
        if method == "initialize":
            result = handle_initialize(params)
        elif method == "initialized":
            result = handle_initialized(params)
        elif method == "tools/list":
            result = handle_tools_list()
        elif method == "tools/call":
            result = await handle_tool_call(params)
        else:
            result = {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        # Build response
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if "error" in result:
            response["error"] = result["error"]
        else:
            response["result"] = result.get("result", result)
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"Messages endpoint error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": body.get("id") if "body" in locals() else None
        })


def handle_initialize(params: Dict) -> Dict:
    """Handle initialize request"""
    client_version = params.get("protocolVersion", "2025-03-26")
    
    # Version negotiation
    if client_version == PROTOCOL_VERSION:
        server_version = PROTOCOL_VERSION
    else:
        # Default to 2025-03-26 which Claude supports
        server_version = "2025-03-26"
    
    return {
        "result": {
            "protocolVersion": server_version,
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "Dr. Strunz Knowledge MCP Server",
                "version": "0.4.0"
            }
        }
    }


def handle_initialized(params: Dict) -> Dict:
    """Handle initialized notification"""
    session_id = params.get("sessionId")
    if session_id and session_id in sessions:
        sessions[session_id]["initialized"] = True
        logger.info(f"Session {session_id} initialized")
    return {}


def handle_tools_list() -> Dict:
    """Handle tools/list request"""
    tools = []
    
    for name, func in tool_registry.items():
        # Build simple input schema
        tools.append({
            "name": name,
            "description": (func.__doc__ or "").strip() or f"Tool: {name}",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": True
            }
        })
    
    return {
        "result": {
            "tools": tools
        }
    }


async def handle_tool_call(params: Dict) -> Dict:
    """Handle tools/call request"""
    tool_name = params.get("name", "")
    tool_args = params.get("arguments", {})
    
    if tool_name not in tool_registry:
        return {
            "error": {
                "code": -32602,
                "message": f"Unknown tool: {tool_name}"
            }
        }
    
    try:
        tool_func = tool_registry[tool_name]
        result = await tool_func(**tool_args)
        
        # Format result for Claude
        if isinstance(result, dict):
            text = json.dumps(result, indent=2)
        else:
            text = str(result)
        
        return {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return {
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }
        }


# OAuth Endpoints
@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth 2.1 Authorization Server Metadata (RFC 8414)"""
    base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "scopes_supported": ["read", "write"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"]
    }

@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    """OAuth 2.0 Protected Resource Metadata (RFC 8705)"""
    base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
    return {
        "resource": base_url,
        "authorization_servers": [base_url],
        "scopes_supported": ["read", "write"],
        "bearer_methods_supported": ["header", "query"]
    }

@app.post("/oauth/register")
async def register_client(request: Request):
    """Dynamic Client Registration (RFC 7591)"""
    try:
        data = await request.json()
        client_id = f"client_{uuid.uuid4().hex[:16]}"
        
        # For Claude.ai, we accept minimal registration
        return JSONResponse({
            "client_id": client_id,
            "client_secret": None,  # Public client
            "client_name": data.get("client_name", "Claude.ai"),
            "redirect_uris": data.get("redirect_uris", ["claude://claude.ai/callback"]),
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read",
            "token_endpoint_auth_method": "none"
        })
    except Exception as e:
        logger.error(f"Client registration error: {e}")
        return JSONResponse({"error": "invalid_request"}, status_code=400)

@app.get("/oauth/authorize")
async def authorize(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="read"),
    response_type: str = Query(default="code"),
    state: Optional[str] = Query(default=None),
    code_challenge: Optional[str] = Query(default=None),
    code_challenge_method: Optional[str] = Query(default=None)
):
    """OAuth Authorization Endpoint"""
    # For simplicity, auto-approve for known clients
    if "claude" in client_id.lower() or "claude.ai" in redirect_uri:
        # Generate authorization code
        auth_code = f"auth_{uuid.uuid4().hex[:16]}"
        
        # Build redirect URL
        redirect_url = f"{redirect_uri}?code={auth_code}"
        if state:
            redirect_url += f"&state={state}"
        
        return RedirectResponse(url=redirect_url)
    
    # For other clients, show consent screen
    return HTMLResponse(f"""
    <html><body>
    <h2>Authorize Access</h2>
    <p>Do you want to grant access to this application?</p>
    <form method="post" action="/oauth/authorize">
        <input type="hidden" name="client_id" value="{client_id}">
        <input type="hidden" name="redirect_uri" value="{redirect_uri}">
        <input type="hidden" name="scope" value="{scope}">
        <input type="hidden" name="state" value="{state or ''}">
        <button type="submit" name="action" value="allow">Allow</button>
        <button type="submit" name="action" value="deny">Deny</button>
    </form>
    </body></html>
    """)

@app.post("/oauth/authorize")
async def authorize_post(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(default="read"),
    state: Optional[str] = Form(default=None),
    action: str = Form(...)
):
    """Handle authorization consent"""
    if action == "allow":
        auth_code = f"auth_{uuid.uuid4().hex[:16]}"
        redirect_url = f"{redirect_uri}?code={auth_code}"
        if state:
            redirect_url += f"&state={state}"
        return RedirectResponse(url=redirect_url)
    else:
        return RedirectResponse(url=f"{redirect_uri}?error=access_denied")

@app.post("/oauth/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(default=None),
    client_id: Optional[str] = Form(default=None),
    redirect_uri: Optional[str] = Form(default=None)
):
    """OAuth Token Endpoint"""
    try:
        if grant_type == "authorization_code":
            # Generate access token
            access_token = f"access_{uuid.uuid4().hex}"
            
            return JSONResponse({
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "read"
            })
        else:
            return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)
    except Exception as e:
        logger.error(f"Token endpoint error: {e}")
        return JSONResponse({"error": "invalid_request"}, status_code=400)

@app.get("/oauth/userinfo")
async def userinfo(user=Depends(get_current_user)):
    """User Info Endpoint"""
    return {"sub": "user", "name": "Dr. Strunz Knowledge User"}

# MCP Resource Discovery
@app.get("/.well-known/mcp/resource")
async def mcp_resource_metadata():
    """MCP resource metadata for discovery"""
    base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
    return {
        "mcpVersion": PROTOCOL_VERSION,
        "transport": ["sse"],
        "endpoints": {
            "sse": f"{base_url}/sse",
            "messages": f"{base_url}/messages"
        },
        "authentication": {
            "type": "oauth2",
            "oauth2": {
                "authorizationUrl": f"{base_url}/oauth/authorize",
                "tokenUrl": f"{base_url}/oauth/token",
                "scopes": {
                    "read": "Read access to knowledge base",
                    "write": "Write access (not implemented)"
                }
            }
        }
    }


async def main():
    """Run the server"""
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting Claude.ai compatible MCP server on port {port}")
    logger.info(f"Protocol version: {PROTOCOL_VERSION}")
    logger.info(f"Tools available: {len(tool_registry)}")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())