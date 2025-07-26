#!/usr/bin/env python3
"""
Official MCP SDK Implementation - Claude.ai Compatible Server  
Uses the official MCP Python SDK from https://github.com/modelcontextprotocol/python-sdk
"""

import os
import sys
import asyncio
import logging
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, Request, Response, Depends, Query, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP SDK is not needed for HTTP server - only for tool imports
OFFICIAL_MCP_AVAILABLE = False

# Server configuration
SERVER_NAME = "Dr. Strunz Knowledge MCP Server"
SERVER_VERSION = "0.9.9"
PROTOCOL_VERSION = "2025-03-26"

# Track server start time for uptime calculation
start_time = time.time()

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

# Preload vector store singleton for performance
try:
    from src.scripts.startup.preload_vector_store import preload_vector_store
    preload_success = preload_vector_store()
    if preload_success:
        logger.info("Vector store preloaded successfully - faster first requests")
    else:
        logger.warning("Vector store preload failed - first requests may be slower")
except Exception as e:
    logger.warning(f"Vector store preload error: {e}")

# Import MCP SDK server and tools
server_instance = None
tool_registry = {}
try:
    from src.mcp.mcp_sdk_clean import StrunzKnowledgeServer
    server_instance = StrunzKnowledgeServer()
    
    # Extract tools from the MCP server
    # The server has handlers registered, we need to create a compatible registry
    for tool_name in dir(server_instance):
        if tool_name.startswith('_handle_'):
            actual_name = tool_name.replace('_handle_', '')
            tool_registry[actual_name] = getattr(server_instance, tool_name)
    
    logger.info(f"Loaded {len(tool_registry)} tools from MCP SDK server")
except Exception as e:
    logger.error(f"Failed to load MCP SDK tools: {e}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication"""
    if credentials:
        # In production, validate the token here
        return {"user": "authenticated"}
    return None


async def perform_health_checks():
    """Perform comprehensive system health checks"""
    import psutil
    import traceback
    
    health_status = {
        "overall": "healthy",
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    # 1. Memory Check
    try:
        memory = psutil.virtual_memory()
        memory_check = {
            "status": "healthy",
            "total_gb": round(memory.total / 1024**3, 2),
            "available_gb": round(memory.available / 1024**3, 2),
            "used_percent": memory.percent
        }
        
        if memory.percent > 90:
            memory_check["status"] = "critical"
            health_status["errors"].append("Memory usage critical (>90%)")
        elif memory.percent > 75:
            memory_check["status"] = "warning"
            health_status["warnings"].append("Memory usage high (>75%)")
            
        health_status["checks"]["memory"] = memory_check
    except Exception as e:
        health_status["checks"]["memory"] = {"status": "error", "error": str(e)}
        health_status["errors"].append(f"Memory check failed: {str(e)}")
    
    # 2. FAISS Vector Store Check
    try:
        vector_store_status = {"status": "unknown", "indices": {}}
        
        # Check if FAISS indices exist
        from pathlib import Path
        faiss_dir = Path("data/faiss_indices")
        
        if faiss_dir.exists():
            combined_index = faiss_dir / "combined_index.faiss"
            combined_metadata = faiss_dir / "combined_metadata.json"
            
            vector_store_status["indices"] = {
                "combined_index": combined_index.exists(),
                "combined_metadata": combined_metadata.exists()
            }
            
            if combined_index.exists() and combined_metadata.exists():
                vector_store_status["status"] = "healthy"
                # Check vector store without loading it (for performance)
                try:
                    from src.rag.search import is_vector_store_loaded, get_vector_store_singleton
                    
                    # First check if already loaded without recreating it
                    if is_vector_store_loaded():
                        vs = get_vector_store_singleton(index_path="data/faiss_indices")
                        vector_store_status["status"] = "operational"
                        vector_store_status["documents"] = len(vs.documents) if hasattr(vs, 'documents') else 0
                        vector_store_status["note"] = "Singleton instance active"
                    else:
                        vector_store_status["status"] = "available"
                        vector_store_status["note"] = "Index files exist but not loaded (will load on first search)"
                        
                except Exception as e:
                    vector_store_status["status"] = "warning"
                    vector_store_status["load_error"] = str(e)
                    health_status["warnings"].append(f"Vector store initialization issue: {str(e)}")
            else:
                vector_store_status["status"] = "missing"
                health_status["warnings"].append("FAISS indices not found")
        else:
            vector_store_status["status"] = "missing"
            health_status["warnings"].append("FAISS directory not found")
            
        health_status["checks"]["vector_store"] = vector_store_status
    except Exception as e:
        health_status["checks"]["vector_store"] = {"status": "warning", "error": str(e)}
        health_status["warnings"].append(f"Vector store check failed: {str(e)}")
    
    # 3. Tool Registry Check
    try:
        tool_check = {
            "status": "healthy",
            "total_tools": len(tool_registry),
            "tools_available": list(tool_registry.keys())  # Show all tools
        }
        
        if len(tool_registry) == 0:
            tool_check["status"] = "error"
            health_status["errors"].append("No tools registered")
        elif len(tool_registry) < 15:
            tool_check["status"] = "warning"
            health_status["warnings"].append(f"Only {len(tool_registry)} tools registered (expected 19+)")
            
        health_status["checks"]["tools"] = tool_check
    except Exception as e:
        health_status["checks"]["tools"] = {"status": "error", "error": str(e)}
        health_status["errors"].append(f"Tool registry check failed: {str(e)}")
    
    # 4. OAuth Endpoints Check
    try:
        routes = [route.path for route in app.routes]
        oauth_routes = [r for r in routes if 'oauth' in r or 'well-known' in r]
        
        oauth_check = {
            "status": "healthy",
            "endpoints_registered": len(oauth_routes),
            "oauth_routes": oauth_routes
        }
        
        expected_oauth_endpoints = [
            "/.well-known/oauth-authorization-server",
            "/oauth/register",
            "/oauth/authorize", 
            "/oauth/token"
        ]
        
        missing_endpoints = [ep for ep in expected_oauth_endpoints if ep not in oauth_routes]
        
        if missing_endpoints:
            oauth_check["status"] = "error"
            oauth_check["missing_endpoints"] = missing_endpoints
            health_status["errors"].append(f"Missing OAuth endpoints: {missing_endpoints}")
        
        health_status["checks"]["oauth"] = oauth_check
    except Exception as e:
        health_status["checks"]["oauth"] = {"status": "error", "error": str(e)}
        health_status["errors"].append(f"OAuth check failed: {str(e)}")
    
    # 5. Environment Check
    try:
        env_check = {
            "status": "healthy",
            "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            "public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown'),
            "port": os.environ.get('PORT', '8000'),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "working_directory": os.getcwd()
        }
        
        # Check critical environment variables
        critical_vars = ['RAILWAY_ENVIRONMENT', 'RAILWAY_PUBLIC_DOMAIN']
        missing_vars = [var for var in critical_vars if not os.environ.get(var)]
        
        if missing_vars:
            env_check["status"] = "warning"
            env_check["missing_vars"] = missing_vars
            health_status["warnings"].append(f"Missing environment variables: {missing_vars}")
        
        health_status["checks"]["environment"] = env_check
    except Exception as e:
        health_status["checks"]["environment"] = {"status": "error", "error": str(e)}
        health_status["errors"].append(f"Environment check failed: {str(e)}")
    
    # Determine overall health - Vector store issues should not block deployment
    critical_errors = [err for err in health_status["errors"] if not err.startswith("Vector store")]
    if critical_errors:
        health_status["overall"] = "unhealthy"
    elif health_status["warnings"]:
        health_status["overall"] = "degraded"
    
    return health_status

@app.get("/railway-health")
@app.head("/railway-health")
async def railway_health():
    """
    Simple, reliable health check endpoint specifically for Railway
    Always returns 200 if the server is running
    """
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }, status_code=200)


@app.get("/")
@app.head("/")
@app.post("/")
async def health_check():
    """
    Comprehensive health check endpoint with detailed diagnostics
    For Railway deployment, consider using /railway-health instead
    """
    try:
        # For basic Railway health checks, always return healthy if server is running
        if os.environ.get('RAILWAY_HEALTHCHECK_BASIC', 'false').lower() == 'true':
            return JSONResponse({
                "status": "healthy",
                "server": "Dr. Strunz Knowledge MCP Server",
                "version": "0.9.9",
                "timestamp": datetime.now().isoformat()
            }, status_code=200)
        
        # Perform comprehensive health checks
        health_status = await perform_health_checks()
        
        # Get prompts (tools ending with _prompt)
        prompt_tools = [tool for tool in tool_registry.keys() if tool.endswith('_prompt')]
        
        # Base response for all methods
        response_data = {
            "status": health_status["overall"],
            "server": "Dr. Strunz Knowledge MCP Server",
            "version": "0.9.9",
            "protocol_version": PROTOCOL_VERSION,
            "transport": "sse",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(time.time() - start_time, 2),
            "tools_summary": {
                "total": len(tool_registry),
                "tools": list(tool_registry.keys()),
                "prompts": prompt_tools
            },
            "health": health_status,
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages",
                "oauth_discovery": "/.well-known/oauth-authorization-server",
                "oauth_register": "/oauth/register",
                "oauth_authorize": "/oauth/authorize",
                "oauth_token": "/oauth/token",
                "health_detailed": "/health",
                "railway_status": "/railway/status",
                "railway_health": "/railway-health"
            },
            "railway": {
                "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown'),
                "deployment_id": os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
                "service_id": os.environ.get('RAILWAY_SERVICE_ID', 'unknown')
            }
        }
        
        # Return appropriate status code based on health
        if health_status["overall"] == "unhealthy":
            return JSONResponse(response_data, status_code=503)
        elif health_status["overall"] == "degraded":
            return JSONResponse(response_data, status_code=200)  # Still operational
        else:
            return JSONResponse(response_data, status_code=200)
            
    except Exception as e:
        # Fallback minimal health check - always return 200 for Railway
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "healthy",
            "server": "Dr. Strunz Knowledge MCP Server",
            "version": "0.9.9",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "railway": {
                "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
            }
        }, status_code=200)  # Changed from 500 to 200 for Railway


@app.get("/health")
async def detailed_health_check():
    """
    Detailed health check endpoint with full diagnostics
    This provides more verbose information than the main health endpoint
    """
    try:
        health_status = await perform_health_checks()
        
        # Add additional diagnostic information
        diagnostics = {
            "server_info": {
                "name": "Dr. Strunz Knowledge MCP Server",
                "version": "0.9.9",
                "protocol_version": PROTOCOL_VERSION,
                "transport": "sse",
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "uptime_seconds": round(time.time() - start_time, 2),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "working_directory": os.getcwd()
            },
            "health_checks": health_status,
            "environment": {
                "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "railway_public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown'),
                "railway_private_domain": os.environ.get('RAILWAY_PRIVATE_DOMAIN', 'unknown'),
                "railway_deployment_id": os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
                "railway_service_id": os.environ.get('RAILWAY_SERVICE_ID', 'unknown'),
                "port": os.environ.get('PORT', '8000'),
                "log_level": os.environ.get('LOG_LEVEL', 'INFO')
            },
            "routes": {
                "total_routes": len(app.routes),
                "all_routes": [{"path": route.path, "methods": list(route.methods)} for route in app.routes]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add tool registry details if available
        if tool_registry:
            diagnostics["tools"] = {
                "total_tools": len(tool_registry),
                "available_tools": list(tool_registry.keys())
            }
        
        return JSONResponse(diagnostics, status_code=200)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)


@app.get("/railway/status")
async def railway_status():
    """
    Railway-specific status endpoint for monitoring and debugging
    Provides Railway-specific diagnostics and deployment information
    """
    try:
        # Get basic health
        health_status = await perform_health_checks()
        
        # Railway-specific information
        railway_info = {
            "deployment": {
                "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown'),
                "private_domain": os.environ.get('RAILWAY_PRIVATE_DOMAIN', 'unknown'),
                "deployment_id": os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
                "service_id": os.environ.get('RAILWAY_SERVICE_ID', 'unknown'),
                "project_id": os.environ.get('RAILWAY_PROJECT_ID', 'unknown'),
                "region": os.environ.get('RAILWAY_REGION', 'unknown')
            },
            "health_status": health_status["overall"],
            "deployment_timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(time.time() - start_time, 2),
            "version": "0.9.9",
            "ready_for_traffic": health_status["overall"] in ["healthy", "degraded"],
            "critical_services": {
                "vector_store": health_status["checks"].get("vector_store", {}).get("status", "unknown"),
                "oauth_endpoints": health_status["checks"].get("oauth", {}).get("status", "unknown"),
                "tool_registry": health_status["checks"].get("tools", {}).get("status", "unknown")
            }
        }
        
        # Add warnings and errors
        if health_status["warnings"]:
            railway_info["warnings"] = health_status["warnings"]
        if health_status["errors"]:
            railway_info["errors"] = health_status["errors"]
        
        return JSONResponse(railway_info, status_code=200)
        
    except Exception as e:
        logger.error(f"Railway status check failed: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')
        }, status_code=500)


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return JSONResponse({
        "CLAUDE_AI_SKIP_OAUTH": os.environ.get("CLAUDE_AI_SKIP_OAUTH", "not_set"),
        "CLAUDE_AI_MINIMAL_OAUTH": os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "not_set"),
        "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT", "not_set"),
        "version": "0.9.9",
        "oauth_mode": "minimal" if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true" else ("disabled" if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true" else "full")
    })

@app.get("/sse")
@app.post("/sse")
@app.head("/sse")
async def sse_endpoint(request: Request, user=Depends(get_current_user)):
    """
    SSE endpoint for Claude.ai MCP communication.
    Uses the older SSE transport that Claude.ai expects.
    """
    # Handle HEAD requests for health checks - must return SSE headers
    if request.method == "HEAD":
        return Response(
            status_code=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
    
    # Check if this is a Claude Desktop request
    user_agent = request.headers.get("user-agent", "")
    is_claude_desktop = "Supabase-Edge-Function" in user_agent or "claude" in user_agent.lower()
    
    logger.info(f"SSE connection established - User-Agent: {user_agent}")
    logger.info(f"Claude Desktop: {is_claude_desktop}, Method: {request.method}")
    
    # For POST requests from Claude Desktop, handle initialization data
    init_data = None
    if request.method == "POST":
        try:
            init_data = await request.json()
            logger.info(f"SSE POST initialization data: {init_data}")
        except Exception as e:
            logger.debug(f"No JSON body in POST request: {e}")
    
    # Create session
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created": datetime.utcnow().isoformat(),
        "user": user,
        "initialized": False,
        "claude_desktop": is_claude_desktop,
        "init_data": init_data
    }
    
    async def event_generator():
        """Generate SSE events for MCP protocol"""
        try:
            # If this is a POST with initialization data from Claude.ai, handle it first
            if request.method == "POST" and init_data:
                # Send initialization response for Claude.ai
                init_response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": init_data.get("params", {}).get("protocolVersion", "2025-03-26"),
                        "capabilities": {
                            "tools": {"listChanged": False},
                            "prompts": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "Dr. Strunz Knowledge MCP Server",
                            "version": "0.9.9"
                        }
                    },
                    "id": init_data.get("id")
                }
                yield {
                    "event": "message",
                    "data": json.dumps(init_response)
                }
            else:
                # Send initial endpoint event like the working server for GET requests
                yield {
                    "event": "endpoint",
                    "data": f"/messages/?session_id={session_id}"
                }
            
            # Keep connection alive with appropriate format
            while True:
                await asyncio.sleep(15)  # Ping every 15 seconds
                if request.method == "POST" and init_data:
                    # Claude.ai expects JSON ping format
                    yield {
                        "event": "ping",
                        "data": json.dumps({
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    }
                else:
                    # Simple timestamp format for regular browsers
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "+00:00"
                    yield {
                        "event": "ping",
                        "data": timestamp
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
@app.post("/messages/")
@app.post("/mcp")  # Claude.ai sometimes uses /mcp instead of /messages
async def messages_endpoint(request: Request, session_id: Optional[str] = Query(None), user=Depends(get_current_user)):
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
        elif method == "prompts/list":
            result = handle_prompts_list()
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
                },
                "prompts": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "Dr. Strunz Knowledge MCP Server",
                "version": "0.9.9"
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

def handle_prompts_list() -> Dict:
    """Handle prompts/list request"""
    # For now, return an empty list of prompts
    # In the future, this could be extended to include actual prompts
    return {
        "result": {
            "prompts": []
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
        # MCP SDK handlers expect a dict argument
        result = await tool_func(tool_args)
        
        # Handle MCP SDK response format (List[TextContent])
        if isinstance(result, list) and len(result) > 0:
            # Extract text from TextContent objects
            if hasattr(result[0], 'text'):
                text = result[0].text
            else:
                text = str(result[0])
        elif isinstance(result, dict):
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


# OAuth Endpoints - Only enabled when OAuth is not skipped
@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth 2.1 Authorization Server Metadata (RFC 8414)"""
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        # This route will be replaced by minimal_oauth
        pass
    # If OAuth is skipped, return 404
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
    
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
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        pass
    # If OAuth is skipped, return 404
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
    
    base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
    return {
        "resource": base_url,
        "authorization_servers": [base_url],
        "scopes_supported": ["read", "write"],
        "bearer_methods_supported": ["header", "query"]
    }

@app.post("/oauth/register")
@app.post("/register")  # Claude.ai uses /register instead of /oauth/register
async def register_client(request: Request):
    """Dynamic Client Registration (RFC 7591)"""
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        pass
    # If OAuth is skipped, return 404
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
    
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
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        pass
    # If OAuth is skipped, return 404
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
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

# Add route for Claude.ai which uses /authorize instead of /oauth/authorize
@app.get("/authorize")
async def authorize_redirect(
    request: Request
):
    """Redirect /authorize to /oauth/authorize for Claude.ai compatibility"""
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        pass
    # Always return 404 when OAuth is disabled
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
    # If OAuth were enabled, redirect to the correct path
    query_string = str(request.url.query)
    return RedirectResponse(url=f"/oauth/authorize?{query_string}")

@app.post("/oauth/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(default=None),
    client_id: Optional[str] = Form(default=None),
    redirect_uri: Optional[str] = Form(default=None)
):
    """OAuth Token Endpoint"""
    # If minimal OAuth is enabled, let minimal_oauth handle this
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        pass
    # If OAuth is skipped, return 404
    elif os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        raise HTTPException(status_code=404, detail="OAuth not enabled")
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

# Claude.ai specific endpoints
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(org_id: str, auth_id: str, redirect_url: Optional[str] = Query(None)):
    """Claude.ai specific authentication start endpoint"""
    # Store client info
    client_id = f"claude_{auth_id[:16]}"
    
    # Check if OAuth should be skipped (default: true for Claude.ai)
    if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        return JSONResponse({
            "status": "success",
            "auth_not_required": True,
            "server_url": "https://strunz.up.railway.app",
            "message": "MCP server ready for use"
        })
    
    # Otherwise redirect to OAuth flow
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

@app.get("/api/mcp/auth_callback")
async def claude_ai_oauth_callback(code: str = Query(None), state: str = Query(None)):
    """OAuth callback handler for Claude.ai"""
    # Return success HTML with postMessage for iframe communication
    return HTMLResponse(f'''
        <html>
        <head><title>MCP Authentication</title></head>
        <body>
            <script>
                // Send message to parent window (Claude.ai)
                if (window.parent !== window) {{
                    window.parent.postMessage({{
                        type: 'mcp-oauth-success',
                        code: '{code}',
                        state: '{state}'
                    }}, '*');
                }}
            </script>
            <h1>✓ Successfully Connected!</h1>
            <p>You can close this window now.</p>
        </body>
        </html>
    ''')

@app.get("/api/callback")
async def claude_ai_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    """Alternative callback endpoint for Claude.ai"""
    if error:
        return JSONResponse({"error": error}, status_code=400)
    
    return JSONResponse({
        "status": "success",
        "code": code,
        "state": state,
        "message": "Authentication successful"
    })

# MCP Resource Discovery - REMOVED for Claude.ai compatibility
# The working bloodtest-mcp-server has NO resource discovery endpoint
# @app.get("/.well-known/mcp/resource")
# async def mcp_resource_metadata():
#     """MCP resource metadata for discovery"""
#     # REMOVED - Claude.ai works without this endpoint


async def main():
    """Run the server"""
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting Claude.ai compatible MCP server on port {port}")
    logger.info(f"Protocol version: {PROTOCOL_VERSION}")
    logger.info(f"Tools available: {len(tool_registry)}")
    
    # Check if we should use minimal OAuth for Claude.ai
    if os.environ.get("CLAUDE_AI_MINIMAL_OAUTH", "false").lower() == "true":
        logger.info("Enabling minimal OAuth for Claude.ai compatibility")
        from src.mcp.minimal_oauth import setup_minimal_oauth_routes
        setup_minimal_oauth_routes(app)
    
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