#!/usr/bin/env python3
"""
Test existing enhanced server locally with different transports
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_http():
    """Test HTTP transport with existing server"""
    print("Testing HTTP transport with existing enhanced server...")
    
    # Set environment to avoid SSE mode
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    try:
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        print("✓ Enhanced server created")
        print(f"✓ Tool registry has {len(server.tool_registry)} tools")
        print("Starting HTTP server on http://localhost:8001/mcp")
        
        # Run with HTTP transport
        server.app.run(transport="http", host="127.0.0.1", port=8001, path="/mcp")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_sse():
    """Test SSE transport with existing server"""
    print("Testing SSE transport with existing enhanced server...")
    
    # Set environment to avoid SSE mode
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    try:
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        print("✓ Enhanced server created")
        print(f"✓ Tool registry has {len(server.tool_registry)} tools")
        print("Starting SSE server on http://localhost:8002")
        
        # Run with SSE transport
        server.app.run(transport="sse", host="127.0.0.1", port=8002)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_stdio():
    """Test stdio transport with existing server"""
    print("Testing stdio transport with existing enhanced server...")
    
    # Set environment to avoid SSE mode
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    try:
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        print("✓ Enhanced server created")
        print(f"✓ Tool registry has {len(server.tool_registry)} tools")
        print("Starting stdio server...")
        
        # Run with stdio transport (default)
        server.app.run()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    if transport == "stdio":
        test_stdio()
    elif transport == "http":
        test_http()
    elif transport == "sse":
        test_sse()
    else:
        print("Usage: python test_existing_server.py [stdio|http|sse]")
        print("Available transports:")
        print("  stdio - Standard input/output (default)")
        print("  http  - HTTP transport on port 8001")
        print("  sse   - Server-Sent Events on port 8002")