#!/usr/bin/env python3
"""
Main Entry Point for StrunzKnowledge MCP Server
Supports both stdio (Claude Desktop) and SSE (Claude.ai/Web) transports
Using official MCP Python SDK
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_transport():
    """Determine which transport to use"""
    # Railway deployment always uses SSE
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return 'sse'
    
    # Check explicit transport setting
    transport = os.environ.get('MCP_TRANSPORT', 'stdio').lower()
    return transport

async def main():
    """Main entry point"""
    transport = get_transport()
    
    print("🚀 Starting StrunzKnowledge MCP Server v2.0.0")
    print("📚 Using official MCP Python SDK")
    print(f"📡 Transport: {transport}")
    print(f"📍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    
    if transport == 'sse':
        # Run SSE server for web deployment
        from src.mcp.sse_server import app
        import uvicorn
        
        port = int(os.environ.get("PORT", 8000))
        print(f"🌐 Starting SSE server on port {port}")
        
        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Run stdio server for Claude Desktop
        from src.mcp.mcp_server_clean import main as stdio_main
        print("🖥️  Starting stdio server for Claude Desktop")
        await stdio_main()

if __name__ == "__main__":
    asyncio.run(main())