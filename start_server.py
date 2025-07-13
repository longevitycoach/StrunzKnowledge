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

# Import and run the enhanced server
try:
    from src.mcp.enhanced_server import create_fastapi_app
    
    print("Starting Enhanced Dr. Strunz Knowledge MCP Server...")
    print(f"Port: {os.environ.get('PORT')}")
    print(f"Host: {os.environ.get('MCP_SERVER_HOST')}")
    
    # Get the FastAPI app instance
    app = create_fastapi_app()
    
    # Run with uvicorn
    import uvicorn
    uvicorn.run(
        app, 
        host=os.environ.get('MCP_SERVER_HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', '8000'))
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying original server as fallback...")
    
    # Try original server as fallback
    try:
        from src.mcp.server import run_server
        run_server()
    except Exception as fallback_error:
        print(f"Fallback also failed: {fallback_error}")
        sys.exit(1)