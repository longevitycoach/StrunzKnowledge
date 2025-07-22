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
    
    print(f"🚀 Starting Dr. Strunz Knowledge Base MCP Server v0.7.10...")
    print(f"📍 Environment: Railway")
    print(f"🌍 Public Domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN')}")
    print(f"🔧 Port: {os.environ.get('PORT')}")
    print(f"⏰ Startup Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("📡 Loading Railway deployment with clean MCP SDK server...")
    print("🔄 This may take 30-60 seconds while loading FAISS indices...")
    
    try:
        # Use unified MCP server with fixes for tool exposure
        from src.mcp.unified_mcp_server import main as run_server
        import asyncio
        print(f"✅ Unified MCP server loaded in {time.time() - start_time:.2f}s")
        print("🎯 Starting unified server with all 20 tools exposed...")
        print("🔧 Fixes: OAuth2 redirect & FastMCP tool extraction")
        asyncio.run(run_server())
        
    except Exception as e:
        print(f"❌ Unified MCP server failed: {e}")
        print("🆘 Critical deployment failure")
        sys.exit(1)

if __name__ == "__main__":
    main()