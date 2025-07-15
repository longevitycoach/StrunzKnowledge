#!/usr/bin/env python3
"""
Railway MCP+SSE Server - Production deployment with SSE endpoint for testing
Exposes health check and SSE endpoints for Railway, MCP protocol via stdio
"""
import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# For Railway health checks and SSE
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

# Create FastAPI app for health check and SSE ONLY
app = FastAPI(title="MCP Server with SSE")

@app.get("/")
async def health_check():
    """Health check for Railway."""
    public_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'strunz.up.railway.app')
    return JSONResponse({
        "status": "healthy",
        "server": "Dr. Strunz Knowledge MCP Server",
        "version": "0.2.0",
        "timestamp": datetime.now().isoformat(),
        "domain": public_domain,
        "endpoints": {
            "health": "/",
            "sse": "/sse",
            "mcp": "via stdio protocol only"
        }
    })

@app.get("/sse")
async def sse_endpoint():
    """Server-Sent Events endpoint for testing and monitoring."""
    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events."""
        # Send initial connection event
        yield {
            "event": "connected",
            "data": json.dumps({
                "message": "Connected to Dr. Strunz Knowledge MCP Server SSE",
                "timestamp": datetime.now().isoformat(),
                "server_version": "0.2.0"
            })
        }
        
        # Send periodic heartbeat events
        heartbeat_count = 0
        while True:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            heartbeat_count += 1
            
            # Get server status
            try:
                from src.mcp.pure_mcp_server import mcp, HAS_VECTOR_STORE
                status = {
                    "heartbeat": heartbeat_count,
                    "timestamp": datetime.now().isoformat(),
                    "mcp_tools": len([n for n in dir(mcp) if hasattr(getattr(mcp, n), '_tool_metadata')]) if 'mcp' in locals() else 0,
                    "vector_store": HAS_VECTOR_STORE,
                    "status": "operational"
                }
            except:
                status = {
                    "heartbeat": heartbeat_count,
                    "timestamp": datetime.now().isoformat(),
                    "status": "limited"
                }
            
            yield {
                "event": "heartbeat",
                "data": json.dumps(status)
            }
    
    return EventSourceResponse(event_generator())

# Import enhanced MCP server for tools
enhanced_mcp_server = None
try:
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    enhanced_mcp_server = StrunzKnowledgeMCP()
    logger.info("Enhanced MCP server initialized with tool registry")
except Exception as e:
    logger.error(f"Failed to initialize enhanced MCP server: {e}")

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """MCP JSON-RPC endpoint for testing with enhanced server."""
    if not enhanced_mcp_server:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32500,
                "message": "Enhanced MCP server not available"
            },
            "id": request.get("id", 1)
        })
    
    # Handle MCP protocol requests
    method = request.get("method", "")
    
    if method == "tools/list":
        # Return list of available tools
        tools = []
        tool_names = [
            "knowledge_search", "find_contradictions", "trace_topic_evolution",
            "create_health_protocol", "compare_approaches", "analyze_supplement_stack",
            "nutrition_calculator", "get_community_insights", "summarize_posts",
            "get_trending_insights", "analyze_strunz_newsletter_evolution",
            "get_guest_authors_analysis", "track_health_topic_trends",
            "get_health_assessment_questions", "assess_user_health_profile",
            "create_personalized_protocol", "get_dr_strunz_biography",
            "get_mcp_server_purpose", "get_vector_db_analysis"
        ]
        
        for name in tool_names:
            tools.append({
                "name": name,
                "description": f"Tool: {name}",
                "inputSchema": {"type": "object"}
            })
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": request.get("id", 1)
        })
    
    elif method == "tools/call":
        # Handle tool calls
        tool_name = request.get("params", {}).get("name", "")
        args = request.get("params", {}).get("arguments", {})
        
        # Route to appropriate tool
        if tool_name in enhanced_mcp_server.tool_registry:
            try:
                tool_func = enhanced_mcp_server.tool_registry[tool_name]
                result = await tool_func(**args)
            except Exception as e:
                result = {"error": f"Tool execution failed: {str(e)}"}
        else:
            result = {"error": f"Tool {tool_name} not found in registry"}
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": request.get("id", 1)
        })
    
    else:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found"
            },
            "id": request.get("id", 1)
        })

def run_fastapi_server():
    """Run FastAPI server in background thread."""
    import threading
    
    def start_uvicorn():
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8000")),
            log_level="warning"  # Reduce noise
        )
    
    thread = threading.Thread(target=start_uvicorn, daemon=True)
    thread.start()
    logger.info(f"HTTP server started on port {os.environ.get('PORT', '8000')}")
    logger.info("Endpoints available: / (health), /sse (events)")

async def main():
    """Run MCP server with SSE endpoint."""
    # Start HTTP server for health check and SSE
    run_fastapi_server()
    
    # Import and run the enhanced MCP server with FastMCP
    try:
        from src.mcp.enhanced_server import main as run_enhanced_server
        
        logger.info("Starting Enhanced Dr. Strunz Knowledge MCP Server v0.2.0")
        logger.info("Enhanced MCP server with 20 tools available")
        logger.info("Running FastMCP with SSE transport on Railway")
        logger.info("SSE endpoint available at /sse for monitoring")
        
        # Run the enhanced server directly with fixed SSE transport
        logger.info("Running in production mode with enhanced MCP capabilities")
        
        # Import and create the enhanced server
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        # Use SSE transport correctly for Railway
        logger.info("Starting FastMCP with SSE transport")
        server.app.run(transport="sse")
        
        # This line won't be reached but kept for completeness
        while True:
            await asyncio.sleep(60)
        
    except ImportError as e:
        logger.error(f"Failed to import MCP server: {e}")
        
        # Keep server running for health checks and SSE
        logger.info("Running in HTTP-only mode (health + SSE)")
        while True:
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)