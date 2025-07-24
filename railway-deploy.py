#!/usr/bin/env python3
"""
Minimal Railway deployment script for Dr. Strunz Knowledge MCP Server

This script bypasses Railway's GitHub integration issues by directly
uploading a working version of the server.
"""

import os
import sys
import time

# Set Railway environment
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ.setdefault('RAILWAY_PUBLIC_DOMAIN', 'strunz.up.railway.app')
os.environ.setdefault('PORT', '8080')

# Add project root to path
sys.path.insert(0, '.')

def main():
    """Deploy to Railway with fallback strategy"""
    start_time = time.time()
    
    print(f"🚀 Starting Dr. Strunz Knowledge Base MCP Server v0.8.2...")
    print(f"📍 Environment: Railway")
    print(f"🌍 Public Domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN')}")
    print(f"🔧 Port: {os.environ.get('PORT')}")
    print(f"⏰ Startup Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("📡 Loading Railway deployment with clean MCP SDK server...")
    print("🔄 This may take 30-60 seconds while loading FAISS indices...")
    
    try:
        # Use claude_compatible_server which provides HTTP endpoints
        from src.mcp.claude_compatible_server import main as run_server
        import asyncio
        print(f"✅ Claude-compatible server loaded in {time.time() - start_time:.2f}s")
        print("🎯 Starting server with HTTP/SSE endpoints...")
        print("🔧 Using MCP SDK tools with HTTP wrapper")
        print("🌐 Health check endpoint: /railway-health")
        asyncio.run(run_server())
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("🆘 Critical deployment failure")
        sys.exit(1)

if __name__ == "__main__":
    main()