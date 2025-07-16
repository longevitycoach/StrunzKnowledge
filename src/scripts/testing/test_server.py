#!/usr/bin/env python3
"""
Test server for running MCP with HTTP endpoints
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the create_fastapi_app function
from src.mcp.enhanced_server import create_fastapi_app

if __name__ == "__main__":
    import uvicorn
    
    # Create the FastAPI app with MCP
    app = create_fastapi_app()
    
    # Run with uvicorn
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting test MCP server on port {port}...")
    print("Available endpoints:")
    print("  - Health: http://localhost:8000/")
    print("  - SSE: http://localhost:8000/sse")
    print("  - MCP: http://localhost:8000/mcp")
    
    uvicorn.run(app, host="0.0.0.0", port=port)