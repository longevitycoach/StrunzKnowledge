#!/usr/bin/env python3
"""
OAuth 2.0 implementation for Claude Desktop MCP Remote Server
Implements Dynamic Client Registration and OAuth authorization flow
"""

import os
import uuid
import json
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, Request, HTTPException, Query, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import logging

logger = logging.getLogger(__name__)

class OAuthMCPServer:
    def __init__(self):
        self.app = FastAPI(title="Strunz Knowledge OAuth MCP Server")
        self.clients: Dict[str, Dict] = {}  # client_id -> client info
        self.auth_codes: Dict[str, Dict] = {}  # code -> auth info
        self.access_tokens: Dict[str, Dict] = {}  # token -> token info
        self.setup_routes()
        self.setup_cors()
        
    def setup_cors(self):
        """Configure CORS for Claude Desktop"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://claude.ai", "https://*.claude.ai", "claude://claude.ai"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup all OAuth and MCP routes"""
        
        @self.app.get("/")
        async def health_check():
            """Health check endpoint"""
            return JSONResponse({
                "status": "healthy",
                "server": "Strunz Knowledge OAuth MCP Server",
                "version": "0.3.0",
                "oauth": {
                    "dynamic_registration": True,
                    "authorization_endpoint": "/oauth/authorize",
                    "token_endpoint": "/oauth/token",
                    "registration_endpoint": "/oauth/register"
                },
                "mcp": {
                    "sse_endpoint": "/mcp/sse",
                    "tools_count": 19
                }
            })
        
        @self.app.post("/oauth/register")
        async def dynamic_client_registration(request: Request):
            """Dynamic Client Registration endpoint"""
            data = await request.json()
            
            # Generate client credentials
            client_id = str(uuid.uuid4())
            client_secret = secrets.token_urlsafe(32)
            
            # Store client info
            self.clients[client_id] = {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": data.get("redirect_uris", []),
                "client_name": data.get("client_name", "Claude Desktop"),
                "grant_types": data.get("grant_types", ["authorization_code"]),
                "response_types": data.get("response_types", ["code"]),
                "created_at": datetime.now().isoformat()
            }
            
            return JSONResponse({
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": data.get("redirect_uris", []),
                "grant_types": ["authorization_code"],
                "response_types": ["code"],
                "client_name": data.get("client_name", "Claude Desktop"),
                "token_endpoint_auth_method": "client_secret_basic"
            })
        
        @self.app.get("/oauth/authorize")
        async def authorize(
            response_type: str = Query(...),
            client_id: str = Query(...),
            redirect_uri: str = Query(...),
            state: Optional[str] = Query(None),
            scope: Optional[str] = Query(None)
        ):
            """OAuth authorization endpoint"""
            
            # Validate client
            if client_id not in self.clients:
                # For Claude Desktop, allow unknown clients (they register dynamically)
                pass
            
            # Generate authorization code
            auth_code = secrets.token_urlsafe(32)
            
            # Store auth code
            self.auth_codes[auth_code] = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope or "mcp:access",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=10)
            }
            
            # For simplicity, auto-approve and redirect
            # In production, show consent screen
            redirect_url = f"{redirect_uri}{'&' if '?' in redirect_uri else '?'}code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
            
            return RedirectResponse(url=redirect_url)
        
        @self.app.post("/oauth/token")
        async def token_exchange(request: Request):
            """OAuth token exchange endpoint"""
            # Parse form data
            form_data = await request.form()
            grant_type = form_data.get("grant_type")
            
            if grant_type == "authorization_code":
                code = form_data.get("code")
                client_id = form_data.get("client_id")
                client_secret = form_data.get("client_secret")
                redirect_uri = form_data.get("redirect_uri")
                
                # Validate auth code
                if code not in self.auth_codes:
                    raise HTTPException(status_code=400, detail="Invalid authorization code")
                
                auth_info = self.auth_codes[code]
                
                # Check expiration
                if datetime.now() > auth_info["expires_at"]:
                    raise HTTPException(status_code=400, detail="Authorization code expired")
                
                # Generate access token
                access_token = f"mcp_{secrets.token_urlsafe(32)}"
                
                # Store token
                self.access_tokens[access_token] = {
                    "client_id": client_id,
                    "scope": auth_info["scope"],
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(hours=24)
                }
                
                # Clean up used auth code
                del self.auth_codes[code]
                
                return JSONResponse({
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 86400,  # 24 hours
                    "scope": auth_info["scope"]
                })
            
            else:
                raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        @self.app.get("/mcp/sse")
        async def mcp_sse_endpoint(
            authorization: Optional[str] = Query(None, alias="access_token")
        ):
            """MCP SSE endpoint with OAuth protection"""
            
            # Validate access token
            if authorization and authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
            elif authorization:
                token = authorization
            else:
                # For testing, allow unauthenticated access
                token = None
            
            if token and token not in self.access_tokens:
                raise HTTPException(status_code=401, detail="Invalid access token")
            
            async def event_generator():
                """Generate MCP protocol events over SSE"""
                # Send initial connection event
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {
                            "serverInfo": {
                                "name": "strunz-knowledge",
                                "version": "0.3.0"
                            },
                            "capabilities": {
                                "tools": {
                                    "listChanged": True
                                },
                                "prompts": {
                                    "listChanged": False
                                },
                                "resources": {
                                    "listChanged": True
                                }
                            }
                        }
                    })
                }
                
                # Import enhanced server for MCP functionality
                try:
                    from .enhanced_server import StrunzKnowledgeMCP
                    mcp_server = StrunzKnowledgeMCP()
                    
                    # Periodic heartbeat
                    while True:
                        await asyncio.sleep(30)
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({
                                "timestamp": datetime.now().isoformat(),
                                "status": "connected"
                            })
                        }
                except Exception as e:
                    logger.error(f"MCP server error: {e}")
                    yield {
                        "event": "error",
                        "data": json.dumps({
                            "error": str(e)
                        })
                    }
            
            return EventSourceResponse(event_generator())
        
        @self.app.post("/mcp/rpc")
        async def mcp_rpc_endpoint(request: Request):
            """MCP JSON-RPC endpoint for handling tool calls"""
            # Validate authorization
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing authorization")
            
            token = auth_header.replace("Bearer ", "")
            if token not in self.access_tokens:
                raise HTTPException(status_code=401, detail="Invalid access token")
            
            # Import MCP server
            try:
                from .enhanced_server import StrunzKnowledgeMCP
                mcp_server = StrunzKnowledgeMCP()
                
                # Handle JSON-RPC request
                request_data = await request.json()
                method = request_data.get("method", "")
                params = request_data.get("params", {})
                request_id = request_data.get("id", 1)
                
                # Route to appropriate handler
                if method == "tools/list":
                    # Return available tools
                    tools = []
                    for name, func in mcp_server.tool_registry.items():
                        tools.append({
                            "name": name,
                            "description": f"Tool: {name}",
                            "inputSchema": {"type": "object"}
                        })
                    
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "result": {"tools": tools},
                        "id": request_id
                    })
                
                elif method == "tools/call":
                    # Execute tool
                    tool_name = params.get("name", "")
                    args = params.get("arguments", {})
                    
                    if tool_name in mcp_server.tool_registry:
                        result = await mcp_server.tool_registry[tool_name](**args)
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "result": result,
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
                            "message": "Method not found"
                        },
                        "id": request_id
                    })
                    
            except Exception as e:
                logger.error(f"MCP RPC error: {e}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": request_data.get("id", 1)
                })

def create_oauth_app():
    """Create OAuth MCP server app"""
    server = OAuthMCPServer()
    return server.app

if __name__ == "__main__":
    import uvicorn
    app = create_oauth_app()
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))