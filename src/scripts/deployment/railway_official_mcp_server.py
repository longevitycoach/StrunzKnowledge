#!/usr/bin/env python3
"""
Railway MCP Server using Official SDK

This server provides full HTTP/SSE support with proper prompts capability
for Claude.ai and Claude Desktop integration.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI and MCP
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import MCP SDK
from mcp.server.sse import create_sse_transport
from mcp.server import MCPServer
from mcp.types import (
    ServerCapabilities,
    Tool,
    Prompt,
    PromptArgument,
    TextContent,
    UserMessage,
    AssistantMessage
)

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
    description="MCP server with full prompts support using official SDK"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server instance
mcp_server = MCPServer(
    name="Dr. Strunz Knowledge MCP Server",
    version="0.7.1"
)

# Global transport instance
sse_transport = None


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server (Official SDK)")
    
    # Preload vector store
    try:
        await preload_vector_store()
    except Exception as e:
        logger.warning(f"Failed to preload vector store: {e}")
    
    # Initialize SSE transport
    global sse_transport
    sse_transport = create_sse_transport("/sse")
    
    # Register capabilities
    await mcp_server.set_capabilities(
        ServerCapabilities(
            tools={"listChanged": False},
            prompts={"listChanged": False}
        )
    )
    
    # Register tools
    tools = []
    for name, func in tool_registry.items():
        tools.append(Tool(
            name=name,
            description=(func.__doc__ or "").strip() or f"Tool: {name}",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": True
            }
        ))
    await mcp_server.set_tools(tools)
    
    # Register prompts
    prompts = [
        Prompt(
            name="health_assessment",
            description="Comprehensive health assessment questionnaire",
            arguments=[
                PromptArgument(name="symptoms", description="Current symptoms", required=True),
                PromptArgument(name="history", description="Medical history", required=False)
            ]
        ),
        Prompt(
            name="supplement_protocol",
            description="Create personalized supplement protocol",
            arguments=[
                PromptArgument(name="goals", description="Health goals", required=True),
                PromptArgument(name="conditions", description="Existing conditions", required=False)
            ]
        ),
        Prompt(
            name="nutrition_optimization",
            description="Optimize nutrition based on Dr. Strunz principles",
            arguments=[
                PromptArgument(name="current_diet", description="Current dietary habits", required=True),
                PromptArgument(name="objectives", description="Nutrition objectives", required=True)
            ]
        )
    ]
    await mcp_server.set_prompts(prompts)
    
    logger.info(f"Server initialized with {len(tools)} tools and {len(prompts)} prompts")


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
    if not sse_transport:
        return JSONResponse(
            {"error": "SSE transport not initialized"},
            status_code=500
        )
    
    return await sse_transport.handle_sse(request, mcp_server)


# Messages endpoint (for testing)
@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle MCP messages via HTTP POST"""
    try:
        body = await request.json()
        
        # Process through MCP server
        response = await mcp_server.handle_request(body)
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": body.get("id") if "body" in locals() else None
            },
            status_code=500
        )


def main():
    """Main entry point"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Public domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    logger.info("Using official MCP SDK with full prompts support")
    
    # Run server
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()