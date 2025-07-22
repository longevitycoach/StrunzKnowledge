#!/usr/bin/env python3
"""
Unified MCP Server - Single server for all environments
Combines all features: Claude.ai compatibility, full tools, OAuth2, SSE

Works in:
- Local development
- Docker containers  
- Railway production
- Claude Desktop
- Claude.ai web
"""

import os
import sys
import asyncio
import logging
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import urllib.parse

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI components
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our components
from src.scripts.startup.preload_vector_store import preload_vector_store
from src.mcp.enhanced_server import StrunzKnowledgeMCP
# Simple OAuth implementation (no Jinja2 dependency)
class SimpleOAuthProvider:
    def __init__(self):
        self.clients = {}
        self.authorization_codes = {}
        self.access_tokens = {}
    
    def register_client(self, client_name, redirect_uris, grant_types, response_types, scope):
        client_id = f"client_{uuid.uuid4().hex[:16]}"
        client = {
            "client_id": client_id,
            "client_secret": None,  # Public client
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "grant_types": grant_types,
            "response_types": response_types,
            "scope": scope,
            "token_endpoint_auth_method": "none"
        }
        self.clients[client_id] = client
        return client
    
    def get_metadata(self, base_url):
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

# Server configuration
SERVER_NAME = "Dr. Strunz Knowledge MCP Server"
SERVER_VERSION = "0.7.9"
PROTOCOL_VERSION = "2025-03-26"

# Initialize components
app = FastAPI(
    title=SERVER_NAME,
    version=SERVER_VERSION,
    description="Unified MCP server with full tools, Claude.ai compatibility, OAuth2, and SSE"
)

# Add CORS middleware for web compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
_enhanced_server: Optional[StrunzKnowledgeMCP] = None
_oauth_provider = SimpleOAuthProvider()
_claude_clients = {}  # Claude.ai client storage
_start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    global _enhanced_server
    
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"Public domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    
    # Preload vector store
    try:
        await preload_vector_store()
        logger.info("Vector store preloaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload vector store: {e}")
    
    # Initialize enhanced server with all tools
    try:
        _enhanced_server = StrunzKnowledgeMCP()
        logger.info(f"✅ Loaded enhanced server with {len(_enhanced_server.tool_registry)} tools")
        
        # Verify all tools are available
        tool_names = list(_enhanced_server.tool_registry.keys())
        logger.info(f"📋 Available tools: {tool_names}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced server: {e}")
        import traceback
        traceback.print_exc()
        
        # Still set _enhanced_server to None for fallback, but log the issue
        logger.error("🚨 FALLING BACK TO MINIMAL SERVER - Production will have limited functionality!")
        _enhanced_server = None


# Health check endpoints
@app.get("/")
@app.get("/health")
@app.post("/")  # Handle Claude.ai POST requests after OAuth
async def health_check():
    """Basic health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "transport": ["sse", "http"],
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(time.time() - _start_time, 2),
        "tools_available": len(_enhanced_server.tool_registry) if _enhanced_server else 0,
        "enhanced_server_loaded": _enhanced_server is not None,
        "available_tool_names": list(_enhanced_server.tool_registry.keys()) if _enhanced_server else ["get_mcp_server_purpose"],
        "environment": {
            "railway": os.environ.get('RAILWAY_ENVIRONMENT') is not None,
            "public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost'),
            "port": os.environ.get('PORT', '8000')
        }
    })


@app.get("/railway-health")
async def railway_health():
    """Railway-specific health check"""
    return JSONResponse({
        "status": "healthy",
        "version": SERVER_VERSION,
        "ready_for_traffic": True,
        "deployment_timestamp": datetime.now().isoformat()
    })


# MCP Protocol endpoints
@app.get("/.well-known/mcp/resource")
async def mcp_resource():
    """MCP resource discovery"""
    base_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}"
    if os.environ.get('RAILWAY_ENVIRONMENT') is None:
        base_url = f"http://localhost:{os.environ.get('PORT', '8000')}"
    
    return JSONResponse({
        "mcpVersion": PROTOCOL_VERSION,
        "serverInfo": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "vendor": "Longevity Coach"
        },
        "transport": ["sse", "http"],
        "endpoints": {
            "sse": f"{base_url}/sse",
            "messages": f"{base_url}/messages",
            "tools": f"{base_url}/tools",
            "prompts": f"{base_url}/prompts"
        },
        "authentication": {
            "type": "oauth2",
            "required": False,
            "oauth2": {
                "authorizationUrl": f"{base_url}/oauth/authorize",
                "tokenUrl": f"{base_url}/oauth/token",
                "registrationUrl": f"{base_url}/oauth/register",
                "scopes": {
                    "read": "Read access to knowledge base",
                    "write": "Write access (not implemented)"
                }
            }
        },
        "capabilities": {
            "tools": True,
            "prompts": True,
            "resources": False,
            "sampling": False
        }
    })


# OAuth2 endpoints
@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth2 authorization server metadata"""
    base_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}"
    if os.environ.get('RAILWAY_ENVIRONMENT') is None:
        base_url = f"http://localhost:{os.environ.get('PORT', '8000')}"
    
    return JSONResponse(_oauth_provider.get_metadata(base_url))


@app.post("/oauth/register")
async def register_client(request: Request):
    """OAuth2 dynamic client registration"""
    data = await request.json()
    client = _oauth_provider.register_client(
        client_name=data.get("client_name", "Unknown Client"),
        redirect_uris=data.get("redirect_uris", []),
        grant_types=data.get("grant_types", ["authorization_code"]),
        response_types=data.get("response_types", ["code"]),
        scope=data.get("scope", "read")
    )
    return JSONResponse(client, status_code=201)


@app.get("/oauth/authorize")
async def authorize(request: Request):
    """OAuth2 authorization endpoint"""
    params = dict(request.query_params)
    
    # Auto-approve for simplicity
    redirect_uri = params.get("redirect_uri", "http://localhost:3000/callback")
    code = str(uuid.uuid4())
    state = params.get("state", "")
    
    # Store authorization code
    _oauth_provider.authorization_codes[code] = {
        "client_id": params.get("client_id"),
        "redirect_uri": redirect_uri,
        "scope": params.get("scope", "read"),
        "created_at": datetime.now().isoformat()
    }
    
    # Redirect with code
    redirect_url = f"{redirect_uri}?code={code}&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)


@app.post("/oauth/token")
async def token_endpoint(request: Request):
    """OAuth2 token endpoint"""
    data = await request.form()
    
    # Simple token generation
    access_token = f"access_{uuid.uuid4()}"
    refresh_token = f"refresh_{uuid.uuid4()}"
    
    return JSONResponse({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": refresh_token,
        "scope": data.get("scope", "read")
    })


# Claude.ai specific endpoint
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(
    org_id: str, 
    auth_id: str,
    redirect_url: Optional[str] = Query(None),
    open_in_browser: Optional[int] = Query(None)
):
    """Claude.ai specific authentication endpoint"""
    logger.info(f"Claude.ai auth request: org={org_id}, auth={auth_id}")
    
    # Store Claude.ai client info
    client_id = f"claude_{auth_id[:16]}"
    _claude_clients[client_id] = {
        "org_id": org_id,
        "auth_id": auth_id,
        "redirect_url": redirect_url,
        "created_at": datetime.now().isoformat()
    }
    
    # Return success directly (no OAuth needed for now)
    return JSONResponse({
        "status": "success",
        "server_url": f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}",
        "auth_not_required": True,
        "message": "MCP server ready for use"
    })


# MCP Messages endpoint
@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle MCP protocol messages"""
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        
        logger.debug(f"MCP request: {method}")
        
        # Route to appropriate handler
        if method == "initialize":
            return await handle_initialize(body)
        elif method == "tools/list":
            return await handle_tools_list(body)
        elif method == "tools/call":
            return await handle_tool_call(body)
        elif method == "prompts/list":
            return await handle_prompts_list(body)
        elif method == "prompts/get":
            return await handle_prompt_get(body)
        else:
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


async def handle_initialize(body: Dict) -> JSONResponse:
    """Handle initialize method"""
    return JSONResponse({
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": False},
                "prompts": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "sampling": {}
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
                "vendor": "Longevity Coach"
            }
        },
        "id": body.get("id")
    })


async def handle_tools_list(body: Dict) -> JSONResponse:
    """Handle tools/list method"""
    tools = []
    
    if _enhanced_server:
        # Use full tool registry from enhanced server
        for name, tool_info in _enhanced_server.tool_registry.items():
            # Extract function from tool_info (handle FastMCP FunctionTool objects)
            if hasattr(tool_info, 'fn'):
                func = tool_info.fn  # FastMCP FunctionTool.fn is the actual function
            elif hasattr(tool_info, 'run'):
                # FastMCP FunctionTool.run method
                func = lambda **kwargs: tool_info.run(**kwargs)
            elif hasattr(tool_info, 'func'):
                func = tool_info.func  # Other FunctionTool variants
            elif hasattr(tool_info, 'function'):
                func = tool_info.function  # Other wrappers
            elif callable(tool_info):
                func = tool_info  # Direct function
            else:
                # Try to get the original function
                func = getattr(tool_info, '__call__', tool_info)
            
            tools.append({
                "name": name,
                "description": (func.__doc__ or "").strip() or f"Tool: {name}",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True
                }
            })
    else:
        # Fallback to basic tools
        tools = [
            {
                "name": "get_mcp_server_purpose",
                "description": "Get information about this MCP server",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
    
    return JSONResponse({
        "jsonrpc": "2.0",
        "result": {"tools": tools},
        "id": body.get("id")
    })


async def handle_tool_call(body: Dict) -> JSONResponse:
    """Handle tools/call method"""
    params = body.get("params", {})
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})
    
    try:
        result = None
        
        if _enhanced_server and tool_name in _enhanced_server.tool_registry:
            # Use enhanced server tools
            tool_info = _enhanced_server.tool_registry[tool_name]
            
            # Extract function (handle FastMCP FunctionTool objects)
            if hasattr(tool_info, 'fn'):
                func = tool_info.fn  # FastMCP FunctionTool.fn is the actual function
            elif hasattr(tool_info, 'run'):
                # FastMCP FunctionTool.run method
                func = lambda **kwargs: tool_info.run(**kwargs)
            elif hasattr(tool_info, 'func'):
                func = tool_info.func  # Other FunctionTool variants
            elif hasattr(tool_info, 'function'):
                func = tool_info.function  # Other wrappers
            elif callable(tool_info):
                func = tool_info  # Direct function
            else:
                # Try to get the original function
                func = getattr(tool_info, '__call__', tool_info)
            
            # Execute tool
            if asyncio.iscoroutinefunction(func):
                result = await func(**tool_args)
            else:
                result = func(**tool_args)
        else:
            # Fallback
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                },
                "id": body.get("id")
            })
        
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


async def handle_prompts_list(body: Dict) -> JSONResponse:
    """Handle prompts/list method"""
    prompts = []
    
    if _enhanced_server and hasattr(_enhanced_server, 'prompts'):
        # Get prompts from enhanced server
        prompts = []
        for name, prompt_func in _enhanced_server.prompts.items():
            prompts.append({
                "name": name,
                "description": (prompt_func.__doc__ or "").strip(),
                "arguments": []
            })
    else:
        # Basic prompts
        prompts = [
            {
                "name": "health_assessment",
                "description": "Comprehensive health assessment questionnaire",
                "arguments": []
            }
        ]
    
    return JSONResponse({
        "jsonrpc": "2.0",
        "result": {"prompts": prompts},
        "id": body.get("id")
    })


async def handle_prompt_get(body: Dict) -> JSONResponse:
    """Handle prompts/get method"""
    params = body.get("params", {})
    name = params.get("name")
    
    if _enhanced_server and hasattr(_enhanced_server, 'prompts'):
        # Get prompt from enhanced server
        try:
            if name in _enhanced_server.prompts:
                prompt_func = _enhanced_server.prompts[name]
                # Execute prompt function
                if asyncio.iscoroutinefunction(prompt_func):
                    prompt_text = await prompt_func(**params.get("arguments", {}))
                else:
                    prompt_text = prompt_func(**params.get("arguments", {}))
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "result": {
                        "messages": [
                            {
                                "role": "user",
                                "content": {"type": "text", "text": prompt_text}
                            }
                        ]
                    },
                    "id": body.get("id")
                })
        except Exception as e:
            logger.error(f"Prompt get error: {e}")
    
    # Fallback
    return JSONResponse({
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": f"Prompt not found: {name}"
        },
        "id": body.get("id")
    })


# SSE endpoint
@app.get("/sse")
@app.post("/sse")  # Handle Claude.ai POST requests
async def sse_endpoint(request: Request):
    """SSE endpoint for real-time communication"""
    # Log the request for debugging
    logger.info(f"SSE request: method={request.method}, headers={dict(request.headers)}")
    
    async def event_generator():
        # Send initial connection message
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
    
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    logger.info(f"Host: {host}:{port}")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"Public domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    
    # Run server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())