#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base - Main Entry Point

This is the main entry point for the Dr. Strunz Knowledge Base MCP Server.
For production deployment, use the scripts in src/scripts/deployment/

Environment Variables:
- RAILWAY_PUBLIC_DOMAIN: Public domain for Railway deployment (default: strunz.up.railway.app)
- RAILWAY_PRIVATE_DOMAIN: Private domain for Railway internal (default: strunz.railway.internal)
- PORT: Server port (default: 8000)
- LOG_LEVEL: Logging level (default: INFO)
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set default Railway domains
os.environ.setdefault('RAILWAY_PUBLIC_DOMAIN', 'strunz.up.railway.app')
os.environ.setdefault('RAILWAY_PRIVATE_DOMAIN', 'strunz.railway.internal')
os.environ.setdefault('PORT', '8000')
os.environ.setdefault('LOG_LEVEL', 'INFO')

def main():
    """Main entry point - determines which server to run."""
    import time
    start_time = time.time()
    
    # Check environment
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
    
    print(f"🚀 Starting Dr. Strunz Knowledge Base MCP Server...")
    print(f"📍 Environment: {'Railway' if is_railway else 'Local'}")
    print(f"🌍 Public Domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}")
    print(f"🔧 Port: {os.environ.get('PORT', '8000')}")
    print(f"⏰ Startup Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if is_railway:
        # Railway deployment - use official MCP SDK server for proper prompts support
        print("📡 Loading Railway deployment with official MCP SDK server...")
        print("🔄 This may take 30-60 seconds while loading FAISS indices...")
        
        # Use official SDK server for better Claude.ai compatibility
        from src.mcp.mcp_sdk_server import main as run_server
        
        print(f"✅ Server initialized in {time.time() - start_time:.2f}s")
        print("🎯 Starting MCP server with SSE transport...")
        run_server()
    else:
        # Local development - use official SDK in stdio mode
        print("🏠 Starting local development server with official MCP SDK...")
        from src.mcp.mcp_sdk_server import main as run_server
        run_server()

if __name__ == "__main__":
    main()