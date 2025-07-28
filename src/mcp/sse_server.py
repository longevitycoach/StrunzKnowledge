#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - SSE Transport
Using official MCP SDK with Starlette for web deployment
Version: 2.0.0
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

# Import our server implementation
from src.mcp.mcp_server_clean import app as mcp_app, initialize_vector_store
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
        "version": "2.0.0",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/"
        },
        "mcp_implementation": "Official MCP Python SDK",
        "protocol_version": "2025-11-05"
    })

# Create Starlette routes
routes = [
    Route("/", endpoint=health_check, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v2.0.0 (SSE Transport)")
    logger.info("Using official MCP Python SDK")
    await initialize_vector_store()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting SSE server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)