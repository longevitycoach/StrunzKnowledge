#!/usr/bin/env python3
"""
Unified Main Entry Point for StrunzKnowledge MCP Server
Supports both stdio (Claude Desktop) and HTTP/SSE (Railway) transports

Environment Variables:
- TRANSPORT: Force specific transport (stdio, http, sse) - auto-detected if not set
- RAILWAY_ENVIRONMENT: Railway deployment environment
- PORT: Server port for HTTP transport (default: 8000)
- MCP_STDIO_MODE: Force stdio mode for Claude Desktop
- LOG_LEVEL: Logging level (default: INFO)
"""

import os
import sys
import asyncio
import logging
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_transport_type():
    """Determine which transport to use based on environment"""
    # Check explicit transport setting
    transport = os.environ.get('TRANSPORT', '').lower()
    if transport in ['stdio', 'http', 'sse']:
        return transport
    
    # Auto-detect based on environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Railway deployment - use HTTP/SSE
        return 'http'
    elif os.environ.get('MCP_STDIO_MODE'):
        # Explicit stdio mode
        return 'stdio'
    elif os.environ.get('PORT'):
        # Port specified - assume HTTP
        return 'http'
    else:
        # Default to stdio for local Claude Desktop
        return 'stdio'

async def run_stdio_server():
    """Run MCP server in stdio mode for Claude Desktop"""
    logger.info("Starting MCP server in stdio mode for Claude Desktop")
    
    try:
        from src.mcp.mcp_sdk_clean import main
        await main()
    except ImportError as e:
        logger.error(f"Failed to import stdio server: {e}")
        logger.info("Installing MCP SDK...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp>=1.0.0"])
        from src.mcp.mcp_sdk_clean import main
        await main()

async def run_http_server():
    """Run MCP server in HTTP/SSE mode for Railway"""
    logger.info("Starting MCP server in HTTP/SSE mode for Railway")
    
    try:
        from src.mcp.claude_compatible_server import main
        await main()
    except ImportError as e:
        logger.error(f"Failed to import HTTP server: {e}")
        logger.info("Installing FastAPI dependencies...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "sse-starlette"])
        from src.mcp.claude_compatible_server import main
        await main()

async def main():
    """Main entry point - selects appropriate transport"""
    start_time = time.time()
    transport = get_transport_type()
    
    print(f"🚀 Starting StrunzKnowledge MCP Server v0.9.0")
    print(f"📡 Transport mode: {transport}")
    print(f"📍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"🌍 Public Domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    print(f"🔧 Port: {os.environ.get('PORT', '8000')}")
    print(f"⏰ Startup Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if transport == 'stdio':
        print("🖥️  Using stdio transport for Claude Desktop")
        await run_stdio_server()
    else:
        print("🌐 Using HTTP/SSE transport for web deployment")
        print("🔄 This may take 30-60 seconds while loading FAISS indices...")
        await run_http_server()
    
    print(f"✅ Server loaded in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)