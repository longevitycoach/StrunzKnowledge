#!/usr/bin/env python3
"""
MCP Streamable HTTP Server Implementation
Follows MCP Specification 2025-06-18
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, List, AsyncGenerator
from dataclasses import dataclass

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# MCP Protocol Version
PROTOCOL_VERSION = "2025-06-18"

# Session storage
sessions: Dict[str, 'MCPSession'] = {}


@dataclass
class MCPSession:
    """MCP Session state"""
    session_id: str
    client_info: Dict
    protocol_version: str
    capabilities: Dict
    initialized: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class MCPStreamableHTTPServer:
    """MCP Server with Streamable HTTP Transport"""
    
    def __init__(self, name: str = "Dr. Strunz Knowledge MCP Server"):
        self.name = name
        self.app = FastAPI(title=name)
        self._setup_routes()
        
        # Import tools from enhanced server
        self.tool_registry = {}
        try:
            from src.mcp.enhanced_server import StrunzKnowledgeMCP
            self.enhanced_server = StrunzKnowledgeMCP()
            self.tool_registry = self.enhanced_server.tool_registry
            logger.info(f"Loaded {len(self.tool_registry)} tools from enhanced server")
        except Exception as e:
            logger.error(f"Failed to load enhanced server: {e}")
            self.enhanced_server = None
    
    def _setup_routes(self):
        """Setup HTTP routes for MCP protocol"""
        
        @self.app.post("/mcp/v1/message")
        async def handle_mcp_message(
            request: Request,
            accept: Optional[str] = Header(None),
            origin: Optional[str] = Header(None),
            x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
        ):
            """
            Main MCP endpoint for Streamable HTTP transport.
            Handles JSON-RPC messages and returns either JSON or SSE stream.
            """
            # Validate Origin header for security
            if origin and not self._validate_origin(origin):
                raise HTTPException(status_code=403, detail="Invalid origin")
            
            # Parse request body
            try:
                body = await request.json()
            except:
                raise HTTPException(status_code=400, detail="Invalid JSON")
            
            # Get or create session
            session = None
            if x_session_id:
                session = sessions.get(x_session_id)
            
            # Determine response type
            wants_stream = accept and "text/event-stream" in accept
            
            # Handle the message
            method = body.get("method", "")
            params = body.get("params", {})
            request_id = body.get("id")
            
            # For notifications (no id), return 202 Accepted
            if request_id is None:
                await self._handle_notification(method, params, session)
                return JSONResponse(status_code=202, content={})
            
            # For requests, return response
            if wants_stream:
                # Return SSE stream
                return EventSourceResponse(
                    self._handle_request_stream(method, params, request_id, session)
                )
            else:
                # Return JSON response
                result = await self._handle_request(method, params, request_id, session)
                return JSONResponse(content=result)
        
        @self.app.get("/.well-known/mcp/resource")
        async def mcp_resource_metadata():
            """OAuth 2.0 Protected Resource Metadata"""
            base_url = os.environ.get('OAUTH_ISSUER_URL', 'https://strunz.up.railway.app')
            return {
                "resource": base_url,
                "authorization_servers": [base_url],
                "bearer_methods_supported": ["header"],
                "resource_documentation": f"{base_url}/docs",
                "resource_signing_alg_values_supported": ["RS256", "HS256"],
                "authz_server": f"{base_url}/.well-known/oauth-authorization-server"
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "server": self.name,
                "protocol_version": PROTOCOL_VERSION,
                "transport": "streamable-http",
                "sessions": len(sessions),
                "tools": len(self.tool_registry)
            }
    
    def _validate_origin(self, origin: str) -> bool:
        """Validate Origin header to prevent DNS rebinding attacks"""
        allowed_origins = [
            "https://claude.ai",
            "https://*.claude.ai",
            "http://localhost",
            "http://localhost:*",
            "http://127.0.0.1",
            "http://127.0.0.1:*"
        ]
        
        # Check exact matches and patterns
        for allowed in allowed_origins:
            if allowed.endswith("*"):
                if origin.startswith(allowed[:-1]):
                    return True
            elif origin == allowed:
                return True
        
        return False
    
    async def _handle_notification(self, method: str, params: Dict, session: Optional[MCPSession]):
        """Handle MCP notifications (no response expected)"""
        logger.info(f"Notification: {method}")
        
        if method == "notifications/initialized":
            if session:
                session.initialized = True
                logger.info(f"Session {session.session_id} initialized")
    
    async def _handle_request(self, method: str, params: Dict, request_id: int, session: Optional[MCPSession]) -> Dict:
        """Handle MCP request and return JSON response"""
        try:
            if method == "initialize":
                return await self._handle_initialize(params, request_id)
            
            elif method == "tools/list":
                return await self._handle_tools_list(request_id, session)
            
            elif method == "tools/call":
                return await self._handle_tool_call(params, request_id, session)
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }
        
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id
            }
    
    async def _handle_request_stream(self, method: str, params: Dict, request_id: int, 
                                   session: Optional[MCPSession]) -> AsyncGenerator[Dict, None]:
        """Handle MCP request and return SSE stream"""
        try:
            # Send initial acknowledgment
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "method": "request/received",
                    "params": {
                        "id": request_id,
                        "method": method
                    }
                })
            }
            
            # Handle the request
            result = await self._handle_request(method, params, request_id, session)
            
            # Send the response
            yield {
                "event": "message",
                "data": json.dumps(result)
            }
            
            # Send stream complete
            yield {
                "event": "done",
                "data": json.dumps({"id": request_id})
            }
            
        except Exception as e:
            logger.error(f"Stream handling error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": request_id
                })
            }
    
    async def _handle_initialize(self, params: Dict, request_id: int) -> Dict:
        """Handle initialize request"""
        client_info = params.get("clientInfo", {})
        client_version = params.get("protocolVersion", "2025-06-18")
        client_capabilities = params.get("capabilities", {})
        
        # Create session
        session_id = str(uuid.uuid4())
        session = MCPSession(
            session_id=session_id,
            client_info=client_info,
            protocol_version=client_version,
            capabilities=client_capabilities
        )
        sessions[session_id] = session
        
        # Determine protocol version
        if client_version == PROTOCOL_VERSION:
            server_version = PROTOCOL_VERSION
        else:
            # Fallback to older version if needed
            server_version = "2025-03-26"
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": server_version,
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "prompts": None,
                    "resources": None,
                    "logging": None
                },
                "serverInfo": {
                    "name": self.name,
                    "version": "0.3.0"
                },
                "sessionId": session_id
            },
            "id": request_id
        }
    
    async def _handle_tools_list(self, request_id: int, session: Optional[MCPSession]) -> Dict:
        """Handle tools/list request"""
        tools = []
        
        for name, func in self.tool_registry.items():
            # Extract function signature for input schema
            import inspect
            sig = inspect.signature(func)
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                
                # Determine type
                param_type = "string"  # Default
                if param.annotation != param.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif hasattr(param.annotation, "__origin__"):
                        if param.annotation.__origin__ == list:
                            param_type = "array"
                        elif param.annotation.__origin__ == dict:
                            param_type = "object"
                
                properties[param_name] = {"type": param_type}
                
                # Check if required
                if param.default == param.empty:
                    required.append(param_name)
            
            tools.append({
                "name": name,
                "description": func.__doc__ or f"Tool: {name}",
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            })
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools
            },
            "id": request_id
        }
    
    async def _handle_tool_call(self, params: Dict, request_id: int, session: Optional[MCPSession]) -> Dict:
        """Handle tools/call request"""
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        
        if tool_name not in self.tool_registry:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                },
                "id": request_id
            }
        
        try:
            tool_func = self.tool_registry[tool_name]
            result = await tool_func(**tool_args)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ],
                    "isError": False
                },
                "id": request_id
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {str(e)}"
                        }
                    ],
                    "isError": True
                },
                "id": request_id
            }


# Create server instance
mcp_server = MCPStreamableHTTPServer()
app = mcp_server.app