#!/usr/bin/env python3
"""
Simple server starter for local development
Usage: python start_server.py
"""

import os
import sys
import asyncio

# Set local environment
os.environ.setdefault('PORT', '8000')
os.environ.setdefault('LOG_LEVEL', 'INFO')

# Import and run unified server
from src.mcp.unified_mcp_server import main

if __name__ == "__main__":
    print("🚀 Starting Unified MCP Server for local development...")
    print("📍 URL: http://localhost:8000")
    print("🛠️  All 19 tools available")
    print("✨ Claude.ai compatible")
    print("🔐 OAuth2 + SSE support")
    print("\nPress Ctrl+C to stop\n")
    
    asyncio.run(main())