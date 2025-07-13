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

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """MCP JSON-RPC endpoint for testing."""
    # This endpoint is for testing only - real MCP communication is via stdio
    return JSONResponse({
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "MCP protocol is available via stdio only, not HTTP"
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
    
    # Import and run the pure MCP server
    try:
        from src.mcp.pure_mcp_server import mcp, HAS_VECTOR_STORE
        
        logger.info("Starting Dr. Strunz Knowledge MCP Server v0.2.0")
        logger.info(f"Vector store available: {HAS_VECTOR_STORE}")
        # Count tools manually
        tool_count = len([name for name in dir(mcp) if hasattr(getattr(mcp, name), '_tool_metadata')])
        logger.info(f"MCP tools available: {tool_count}")
        logger.info("MCP protocol ready on stdio")
        logger.info("SSE endpoint available at /sse")
        
        # Run MCP server on stdio
        await mcp.run()
        
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