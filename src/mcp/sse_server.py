#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - SSE Transport
Using official MCP SDK with Starlette for web deployment
Version: 3.0.0
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Starlette
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, JSONResponse
from starlette.middleware.cors import CORSMiddleware

# Import MCP SDK
from mcp.server.sse import SseServerTransport

# Import our server implementation (final version without feature flags)
from src.mcp.mcp_server_final import app as mcp_app, initialize_vector_store
from mcp.server import NotificationOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create SSE transport
sse_transport = SseServerTransport("/messages/")

async def handle_sse(request):
    """Handle SSE connections according to MCP documentation"""
    logger.info(f"SSE connection from {request.headers.get('user-agent', 'unknown')}")
    
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_app.run(
            streams[0], 
            streams[1], 
            mcp_app.create_initialization_options(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
    
    # Return empty response as documented to avoid NoneType error
    return Response()

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "3.0.0",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/"
        },
        "mcp_implementation": "Official MCP Python SDK",
        "protocol_version": "2025-11-05"
    })

async def oauth_protected_resource(request):
    """OAuth 2.0 Protected Resource Metadata (RFC9728) for MCP discovery"""
    return JSONResponse({
        "resource": "https://strunz.up.railway.app",
        "authorization_servers": ["https://strunz.up.railway.app"],
        "bearertokentype": "bearer",
        "scopes_supported": ["mcp:read", "mcp:write"],
        "mcp_version": "2025-11-05"
    })

async def oauth_authorization_server(request):
    """OAuth 2.0 Authorization Server Metadata (RFC8414) for MCP"""
    base_url = "https://strunz.up.railway.app"
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "registration_endpoint": f"{base_url}/register",
        "response_types_supported": ["code", "token"],
        "grant_types_supported": ["authorization_code", "implicit", "refresh_token"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["mcp:read", "mcp:write"],
        "service_documentation": f"{base_url}/docs",
        "mcp_implementation": {
            "version": "2025-11-05",
            "transport": "sse",
            "features": ["tools", "resources"]
        }
    })

async def mcp_discovery(request):
    """MCP-specific discovery endpoint"""
    return JSONResponse({
        "mcp_version": "2025-11-05",
        "server_name": "Dr. Strunz Knowledge Base",
        "server_description": "Comprehensive health knowledge based on Dr. Ulrich Strunz's work",
        "server_url": "https://strunz.up.railway.app",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/"
        },
        "oauth_required": False,
        "authentication": {
            "type": "none",
            "description": "No authentication required"
        },
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        }
    })

async def claude_ai_start_auth(request):
    """Claude.ai specific auth endpoint"""
    org_id = request.path_params.get('org_id', 'unknown')
    auth_id = request.path_params.get('auth_id', 'unknown')
    redirect_url = request.query_params.get('redirect_url', None)
    
    logger.info(f"Claude.ai auth request: org={org_id}, auth={auth_id}, redirect={redirect_url}")
    
    # Skip OAuth for now (simplified mode)
    if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        return JSONResponse({
            "status": "success",
            "auth_not_required": True,
            "server_url": "https://strunz.up.railway.app",
            "message": "MCP server ready for use"
        })
    
    # If OAuth is needed in the future
    return JSONResponse({"error": "OAuth not implemented"}, status_code=501)

# Create Starlette routes
routes = [
    Route("/", endpoint=health_check, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", endpoint=oauth_protected_resource, methods=["GET"]),
    Route("/.well-known/oauth-authorization-server", endpoint=oauth_authorization_server, methods=["GET"]),
    Route("/.well-known/mcp", endpoint=mcp_discovery, methods=["GET"]),
    Route("/api/organizations/{org_id}/mcp/start-auth/{auth_id}", endpoint=claude_ai_start_auth, methods=["GET"]),
]

# Add the messages endpoint separately after creating the app
# This will be done below after app creation

# Create Starlette app
app = Starlette(routes=routes, debug=False)

# Add CORS middleware for browser compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add the messages endpoint handler
@app.route("/messages/", methods=["POST"])
async def handle_messages(request):
    """Handle POST requests to messages endpoint"""
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)
    # Return empty response after handling
    return Response(status_code=200)

# OAuth placeholder endpoints for Claude.ai compatibility
@app.route("/authorize", methods=["GET"])
async def oauth_authorize(request):
    """OAuth authorization endpoint (simplified for no-auth mode)"""
    # Since we don't require authentication, immediately redirect with success
    redirect_uri = request.query_params.get("redirect_uri", "https://claude.ai/callback")
    state = request.query_params.get("state", "")
    code = "no_auth_required"
    
    from starlette.responses import RedirectResponse
    return RedirectResponse(url=f"{redirect_uri}?code={code}&state={state}")

@app.route("/token", methods=["POST"])
async def oauth_token(request):
    """OAuth token endpoint (simplified for no-auth mode)"""
    return JSONResponse({
        "access_token": "no_auth_required",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "mcp:read mcp:write"
    })

@app.route("/register", methods=["POST"])
async def oauth_register(request):
    """OAuth dynamic client registration (simplified)"""
    try:
        data = await request.json()
    except:
        data = {}
    
    return JSONResponse({
        "client_id": data.get("client_name", "claude_ai"),
        "client_secret": "not_required",
        "grant_types": ["authorization_code", "implicit"],
        "redirect_uris": data.get("redirect_uris", ["https://claude.ai/callback"]),
        "client_name": data.get("client_name", "Claude AI"),
        "scope": "mcp:read mcp:write"
    })

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v3.0.0 (SSE Transport)")
    logger.info("Using official MCP Python SDK")
    await initialize_vector_store()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting SSE server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)