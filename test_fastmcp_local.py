#!/usr/bin/env python3
"""
Test FastMCP locally with different transports
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP

def create_test_server():
    """Create a simple test MCP server"""
    mcp = FastMCP("Test Strunz Knowledge Server")
    
    @mcp.tool()
    def test_tool(query: str) -> str:
        """A simple test tool"""
        return f"Test response for: {query}"
    
    @mcp.tool()
    def get_server_info() -> dict:
        """Get server information"""
        return {
            "name": "Test Strunz Knowledge Server",
            "version": "1.0.0",
            "tools": ["test_tool", "get_server_info"]
        }
    
    return mcp

def test_stdio():
    """Test stdio transport"""
    print("Testing STDIO transport...")
    mcp = create_test_server()
    print("✓ STDIO server created")
    print("To test: run 'python test_fastmcp_local.py stdio' and use MCP inspector")
    return mcp

def test_http():
    """Test HTTP transport"""
    print("Testing HTTP transport...")
    mcp = create_test_server()
    print("✓ HTTP server created")
    print("Starting HTTP server on http://localhost:8001/mcp")
    mcp.run(transport="http", host="127.0.0.1", port=8001, path="/mcp")

def test_sse():
    """Test SSE transport"""
    print("Testing SSE transport...")
    mcp = create_test_server()
    print("✓ SSE server created")
    print("Starting SSE server on http://localhost:8002")
    mcp.run(transport="sse", host="127.0.0.1", port=8002)

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    if transport == "stdio":
        mcp = test_stdio()
        mcp.run()  # Default stdio
    elif transport == "http":
        test_http()
    elif transport == "sse":
        test_sse()
    else:
        print("Usage: python test_fastmcp_local.py [stdio|http|sse]")
        print("Available transports:")
        print("  stdio - Standard input/output (default)")
        print("  http  - HTTP transport on port 8001")
        print("  sse   - Server-Sent Events on port 8002")