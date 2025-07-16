#!/usr/bin/env python3
"""
Test MCP SDK transports locally
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_fastmcp_available():
    """Test if FastMCP is available"""
    try:
        from fastmcp import FastMCP
        print("✓ FastMCP is available")
        
        # Test creating a simple server
        mcp = FastMCP("Test Server")
        print(f"✓ FastMCP server created: {mcp.name}")
        
        # Check available methods
        methods = [method for method in dir(mcp) if not method.startswith('_')]
        print(f"✓ Available methods: {methods}")
        
        # Test if run method exists
        if hasattr(mcp, 'run'):
            print("✓ run() method available")
        else:
            print("✗ run() method not available")
        
        return True
        
    except ImportError as e:
        print(f"✗ FastMCP not available: {e}")
        return False

def test_mcp_sdk():
    """Test official MCP SDK"""
    try:
        from mcp import Server
        print("✓ Official MCP SDK is available")
        
        # Test creating a server
        server = Server("test-server")
        print(f"✓ MCP Server created: {server.name}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Official MCP SDK not available: {e}")
        return False

def test_enhanced_server():
    """Test our enhanced server"""
    try:
        from src.mcp.enhanced_server import StrunzKnowledgeMCP, FASTMCP_AVAILABLE
        print(f"✓ Enhanced server available, FastMCP: {FASTMCP_AVAILABLE}")
        
        if FASTMCP_AVAILABLE:
            server = StrunzKnowledgeMCP()
            print(f"✓ Enhanced server created with {len(server.tool_registry)} tools")
        else:
            print("✗ Enhanced server created but FastMCP not available")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced server error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_http_server():
    """Create a simple HTTP server for testing"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class MCPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy",
                    "server": "Test MCP Server",
                    "transport": "http"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            if self.path == '/mcp':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                    method = request_data.get('method', '')
                    
                    if method == 'tools/list':
                        response = {
                            "jsonrpc": "2.0",
                            "result": {
                                "tools": [
                                    {
                                        "name": "test_tool",
                                        "description": "A test tool",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "query": {"type": "string"}
                                            }
                                        }
                                    }
                                ]
                            },
                            "id": request_data.get('id', 1)
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32601,
                                "message": "Method not found"
                            },
                            "id": request_data.get('id', 1)
                        }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    return HTTPServer(('localhost', 8001), MCPHandler)

def test_http_server():
    """Test HTTP server"""
    print("Testing HTTP server...")
    server = create_simple_http_server()
    print("✓ HTTP server created on http://localhost:8001")
    print("✓ Health check: http://localhost:8001/")
    print("✓ MCP endpoint: http://localhost:8001/mcp")
    print("Starting server... (Press Ctrl+C to stop)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("✓ Server stopped")
        server.shutdown()

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "test"
    
    if command == "test":
        print("=== Testing MCP SDK Availability ===")
        print()
        test_fastmcp_available()
        print()
        test_mcp_sdk()
        print()
        test_enhanced_server()
        print()
        print("=== Summary ===")
        print("Use 'python test_mcp_sdk.py http' to start a simple HTTP server")
        
    elif command == "http":
        test_http_server()
    else:
        print("Usage: python test_mcp_sdk.py [test|http]")
        print("  test - Test SDK availability")
        print("  http - Start HTTP server")