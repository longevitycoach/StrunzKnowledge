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
    
    print(f"🚀 Starting Dr. Strunz Knowledge Base MCP Server v0.6.3...")
    print(f"📍 Environment: Railway")
    print(f"🌍 Public Domain: {os.environ.get('RAILWAY_PUBLIC_DOMAIN')}")
    print(f"🔧 Port: {os.environ.get('PORT')}")
    print(f"⏰ Startup Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("📡 Loading Railway deployment with clean MCP SDK server...")
    print("🔄 This may take 30-60 seconds while loading FAISS indices...")
    
    try:
        # Try clean MCP SDK first
        from src.mcp.mcp_sdk_clean import main as run_server
        print(f"✅ Clean MCP SDK loaded in {time.time() - start_time:.2f}s")
        print("🎯 Starting MCP server with official SDK...")
        run_server()
        
    except Exception as e:
        print(f"⚠️ Clean MCP SDK failed: {e}")
        print("🔄 Falling back to compatible server...")
        
        try:
            from src.mcp.claude_compatible_server import main as run_server
            import asyncio
            print(f"✅ Fallback server loaded in {time.time() - start_time:.2f}s")
            print("🎯 Starting FastAPI server...")
            asyncio.run(run_server())
            
        except Exception as e2:
            print(f"❌ All servers failed: {e2}")
            print("🆘 Critical deployment failure")
            sys.exit(1)

if __name__ == "__main__":
    main()