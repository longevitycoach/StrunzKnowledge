#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set default environment variables
os.environ.setdefault('PORT', '8000')
os.environ.setdefault('MCP_SERVER_HOST', '0.0.0.0')
os.environ.setdefault('LOG_LEVEL', 'INFO')

# Import and run the server
try:
    from src.mcp.server import run_server
    
    print("Starting Dr. Strunz Knowledge MCP Server...")
    print(f"Port: {os.environ.get('PORT')}")
    print(f"Host: {os.environ.get('MCP_SERVER_HOST')}")
    
    # Run the server
    run_server()
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    
    # Try running as module
    import subprocess
    subprocess.run([sys.executable, "-m", "src.mcp.server"])