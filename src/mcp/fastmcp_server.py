#!/usr/bin/env python3
"""
FastMCP Server wrapper for Railway deployment
This handles the SSE transport configuration properly
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for FastMCP server."""
    # Import the enhanced server
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    
    logger.info("Starting FastMCP Strunz Knowledge Server")
    server = StrunzKnowledgeMCP()
    
    # Check if running on Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Running on Railway with SSE transport on port {port}")
        
        # Use SSE transport for Railway without host parameter
        # FastMCP will bind to 0.0.0.0 by default for SSE
        server.app.run(transport="sse", port=port)
    else:
        # Local development uses stdio
        logger.info("Running locally with stdio transport")
        server.app.run()

if __name__ == "__main__":
    main()