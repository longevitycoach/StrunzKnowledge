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

# Check if we're in a minimal deployment (no FAISS indices)
if not Path("data/faiss_indices/combined_index.faiss").exists():
    print("WARNING: FAISS indices not found. Running in demo mode.")
    print("The full knowledge base will not be available.")

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
    print(f"Error details: {type(e).__name__}")
    
    # For Railway deployment, run the simple server as fallback
    print("Running simple server for Railway deployment...")
    try:
        from simple_server import app
        import uvicorn
        uvicorn.run(
            app,
            host=os.environ.get('MCP_SERVER_HOST', '0.0.0.0'),
            port=int(os.environ.get('PORT', '8000'))
        )
    except Exception as simple_error:
        print(f"Simple server also failed: {simple_error}")
        sys.exit(1)