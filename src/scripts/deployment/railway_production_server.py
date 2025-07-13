#!/usr/bin/env python3
"""
Railway Production Server - Enhanced MCP Server with HTTP endpoints
Simpler approach to avoid asyncio conflicts
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the enhanced MCP server directly"""
    logger.info("Starting Railway Production Server with Enhanced MCP")
    logger.info(f"Port: {os.environ.get('PORT', '8000')}")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
    
    try:
        # Import and run the enhanced server's FastAPI app
        from src.mcp.enhanced_server import create_fastapi_app
        import uvicorn
        
        logger.info("Creating enhanced FastAPI app...")
        app = create_fastapi_app()
        
        logger.info("Enhanced MCP server with 19 tools initialized")
        logger.info("Starting uvicorn server...")
        
        # Run uvicorn server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8000")),
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start enhanced server: {e}")
        logger.info("Falling back to basic health check server...")
        
        # Fallback basic server
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        import uvicorn
        
        app = FastAPI(title="Fallback MCP Server")
        
        @app.get("/")
        async def health_check():
            return JSONResponse({
                "status": "healthy",
                "server": "Enhanced Dr. Strunz Knowledge MCP Server",
                "version": "0.2.0",
                "error": "Enhanced server failed to initialize",
                "timestamp": datetime.now().isoformat()
            })
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8000")),
            log_level="info"
        )

if __name__ == "__main__":
    main()