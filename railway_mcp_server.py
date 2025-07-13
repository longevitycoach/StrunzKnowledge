#!/usr/bin/env python3
"""
Railway MCP Server - Production deployment without public HTTP API
Only exposes health check endpoint for Railway, all MCP communication via stdio
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# For Railway health checks only
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create minimal FastAPI app for health checks ONLY
health_app = FastAPI(title="MCP Server Health Check")

@health_app.get("/")
async def health_check():
    """Minimal health check for Railway."""
    return JSONResponse({
        "status": "healthy",
        "server": "Dr. Strunz Knowledge MCP Server",
        "timestamp": datetime.now().isoformat(),
        "note": "MCP protocol only - no public API"
    })

def run_health_server():
    """Run health check server in background thread."""
    import threading
    
    def start_uvicorn():
        uvicorn.run(
            health_app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8000")),
            log_level="warning"  # Reduce noise
        )
    
    thread = threading.Thread(target=start_uvicorn, daemon=True)
    thread.start()
    logger.info(f"Health check server started on port {os.environ.get('PORT', '8000')}")

async def main():
    """Run MCP server with minimal health endpoint."""
    # Start health check server for Railway
    run_health_server()
    
    # Import and run the pure MCP server
    try:
        from src.mcp.pure_mcp_server import mcp, HAS_VECTOR_STORE
        
        logger.info("Starting Dr. Strunz Knowledge MCP Server")
        logger.info(f"Vector store available: {HAS_VECTOR_STORE}")
        logger.info(f"MCP tools available: {len(mcp.tools)}")
        logger.info("MCP protocol ready on stdio (no HTTP API)")
        
        # Run MCP server on stdio
        await mcp.run()
        
    except ImportError as e:
        logger.error(f"Failed to import MCP server: {e}")
        
        # Fallback to simple health-only server
        logger.info("Running in health-check only mode")
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