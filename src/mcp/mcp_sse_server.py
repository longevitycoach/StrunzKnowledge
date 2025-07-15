#!/usr/bin/env python3
"""
MCP Server with SSE transport and OAuth support for Claude Desktop
Implements proper MCP protocol over Server-Sent Events
"""

import os
import sys
import json
import asyncio
import secrets
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, parse_qs

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Request, HTTPException, Query, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse

# Import enhanced server for tools
from src.mcp.enhanced_server import StrunzKnowledgeMCP

logger = logging.getLogger(__name__)

class MCPSSEServer:
    def __init__(self):
        self.app = FastAPI(title="Strunz Knowledge MCP SSE Server")
        self.security = HTTPBearer(auto_error=False)
        
        # OAuth state
        self.clients: Dict[str, Dict] = {}
        self.auth_codes: Dict[str, Dict] = {}
        self.access_tokens: Dict[str, Dict] = {}
        
        # MCP state
        self.mcp_server = StrunzKnowledgeMCP()
        self.sessions: Dict[str, Dict] = {}  # session_id -> session state
        
        self.setup_routes()
        self.setup_cors()
    
    def setup_cors(self):
        """Configure CORS for Claude Desktop"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://claude.ai",
                "https://*.claude.ai", 
                "claude://claude.ai",
                "http://localhost:*",
                "http://127.0.0.1:*"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"]
        )
    
    def verify_token(self, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
        """Verify Bearer token"""
        if not credentials:
            return None
            
        token = credentials.credentials
        if token in self.access_tokens:
            token_info = self.access_tokens[token]
            if datetime.now() < token_info["expires_at"]:
                return token
        return None
    
    def setup_routes(self):
        """Setup all routes"""
        
        @self.app.get("/")
        async def health_check():
            """Health check with MCP info"""
            return JSONResponse({
                "status": "healthy",
                "server": "Strunz Knowledge MCP SSE Server",
                "version": "0.4.0",
                "transports": ["sse", "http"],
                "authentication": {
                    "type": "oauth2",
                    "authorization_endpoint": "/oauth/authorize",
                    "token_endpoint": "/oauth/token",
                    "registration_endpoint": "/oauth/register"
                },
                "mcp": {
                    "sse_endpoint": "/mcp/sse",
                    "tools_count": len(self.mcp_server.tool_registry)
                }
            })
        
        @self.app.post("/oauth/register")
        async def oauth_register(request: Request):
            """Dynamic Client Registration"""
            data = await request.json()
            
            client_id = str(secrets.token_urlsafe(16))
            client_secret = secrets.token_urlsafe(32)
            
            self.clients[client_id] = {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": data.get("redirect_uris", []),
                "client_name": data.get("client_name", "MCP Client"),
                "created_at": datetime.now().isoformat()
            }
            
            return JSONResponse({
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": data.get("redirect_uris", []),
                "token_endpoint_auth_method": "client_secret_basic"
            })
        
        @self.app.get("/oauth/authorize")
        async def oauth_authorize(
            response_type: str = Query(...),
            client_id: str = Query(...),
            redirect_uri: str = Query(...),
            state: Optional[str] = Query(None),
            scope: Optional[str] = Query(None)
        ):
            """OAuth authorization endpoint"""
            # Generate auth code
            auth_code = secrets.token_urlsafe(32)
            
            self.auth_codes[auth_code] = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope or "mcp",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=10)
            }
            
            # Auto-approve for now
            redirect_url = f"{redirect_uri}{'&' if '?' in redirect_uri else '?'}code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
                
            return RedirectResponse(url=redirect_url)
        
        @self.app.post("/oauth/token")
        async def oauth_token(request: Request):
            """OAuth token exchange"""
            form_data = await request.form()
            grant_type = form_data.get("grant_type")
            
            if grant_type == "authorization_code":
                code = form_data.get("code")
                
                if code not in self.auth_codes:
                    raise HTTPException(status_code=400, detail="Invalid authorization code")
                
                auth_info = self.auth_codes[code]
                
                if datetime.now() > auth_info["expires_at"]:
                    raise HTTPException(status_code=400, detail="Authorization code expired")
                
                # Generate access token
                access_token = f"mcp_{secrets.token_urlsafe(32)}"
                
                self.access_tokens[access_token] = {
                    "client_id": auth_info["client_id"],
                    "scope": auth_info["scope"],
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(hours=24)
                }
                
                del self.auth_codes[code]
                
                return JSONResponse({
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 86400,
                    "scope": auth_info["scope"]
                })
            
            raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        @self.app.get("/mcp/sse")
        async def mcp_sse_endpoint(
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security)
        ):
            """MCP Server-Sent Events endpoint"""
            
            # Verify token if provided
            token = None
            if credentials:
                token = self.verify_token(credentials)
                if not token and credentials.credentials != "demo":
                    raise HTTPException(status_code=401, detail="Invalid token")
            
            # Create session
            session_id = secrets.token_urlsafe(16)
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "token": token,
                "request_counter": 0
            }
            
            async def mcp_event_stream():
                """Generate MCP protocol events"""
                try:
                    # Send initialization event
                    init_msg = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "prompts": {},
                                "resources": {}
                            },
                            "serverInfo": {
                                "name": "strunz-knowledge",
                                "version": "0.4.0"
                            }
                        }
                    }
                    
                    yield {
                        "event": "message",
                        "data": json.dumps(init_msg)
                    }
                    
                    # Keep connection alive
                    while session_id in self.sessions:
                        await asyncio.sleep(30)
                        
                        # Send ping
                        ping_msg = {
                            "jsonrpc": "2.0",
                            "method": "notifications/ping",
                            "params": {
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                        
                        yield {
                            "event": "ping",
                            "data": json.dumps(ping_msg)
                        }
                        
                except asyncio.CancelledError:
                    pass
                finally:
                    # Clean up session
                    if session_id in self.sessions:
                        del self.sessions[session_id]
            
            return EventSourceResponse(mcp_event_stream())
        
        @self.app.post("/mcp/sse")
        async def mcp_sse_request(
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security)
        ):
            """Handle MCP requests over HTTP POST"""
            
            # Verify token
            token = None
            if credentials:
                token = self.verify_token(credentials)
                if not token and credentials.credentials != "demo":
                    raise HTTPException(status_code=401, detail="Invalid token")
            
            # Parse request
            request_data = await request.json()
            method = request_data.get("method", "")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            try:
                # Handle different methods
                if method == "initialize":
                    result = {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "prompts": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "strunz-knowledge",
                            "version": "0.4.0"
                        }
                    }
                
                elif method == "tools/list":
                    tools = []
                    for name, func in self.mcp_server.tool_registry.items():
                        # Get function signature for parameters
                        import inspect
                        sig = inspect.signature(func)
                        
                        properties = {}
                        required = []
                        
                        for param_name, param in sig.parameters.items():
                            if param_name == 'self':
                                continue
                                
                            param_type = "string"  # Default type
                            if param.annotation != param.empty:
                                if param.annotation == int:
                                    param_type = "integer"
                                elif param.annotation == bool:
                                    param_type = "boolean"
                                elif param.annotation == list or param.annotation == List:
                                    param_type = "array"
                                elif param.annotation == dict or param.annotation == Dict:
                                    param_type = "object"
                            
                            properties[param_name] = {
                                "type": param_type,
                                "description": f"Parameter {param_name}"
                            }
                            
                            if param.default == param.empty:
                                required.append(param_name)
                        
                        tools.append({
                            "name": name,
                            "description": func.__doc__ or f"Tool {name}",
                            "inputSchema": {
                                "type": "object",
                                "properties": properties,
                                "required": required
                            }
                        })
                    
                    result = {"tools": tools}
                
                elif method == "tools/call":
                    tool_name = params.get("name", "")
                    arguments = params.get("arguments", {})
                    
                    if tool_name in self.mcp_server.tool_registry:
                        # Call tool
                        tool_func = self.mcp_server.tool_registry[tool_name]
                        tool_result = await tool_func(**arguments)
                        
                        # Format result
                        result = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(tool_result, indent=2)
                                }
                            ]
                        }
                    else:
                        raise ValueError(f"Tool not found: {tool_name}")
                
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                # Return success response
                response = {
                    "jsonrpc": "2.0",
                    "result": result
                }
                
                if request_id is not None:
                    response["id"] = request_id
                    
                return JSONResponse(response)
                
            except Exception as e:
                # Return error response
                response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                
                if request_id is not None:
                    response["id"] = request_id
                    
                return JSONResponse(response, status_code=500)

def create_app():
    """Create MCP SSE server app"""
    server = MCPSSEServer()
    return server.app

if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting MCP SSE Server on port {port}")
    logger.info("SSE endpoint: /mcp/sse")
    logger.info("OAuth endpoints: /oauth/authorize, /oauth/token")
    
    uvicorn.run(app, host="0.0.0.0", port=port)