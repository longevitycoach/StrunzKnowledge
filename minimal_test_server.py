#!/usr/bin/env python3
"""
Minimal test server using only standard library
"""
import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import enhanced server
from src.mcp.enhanced_server import StrunzKnowledgeMCP

# Global MCP server instance
mcp_server = None

class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "server": "Enhanced Dr. Strunz Knowledge MCP Server",
                "version": "1.0.0",
                "mcp_tools": len(mcp_server.tool_registry) if mcp_server else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/mcp":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                
                if data.get("method") == "tools/call":
                    tool_name = data["params"]["name"]
                    args = data["params"].get("arguments", {})
                    
                    # Call the tool using the registry
                    if tool_name in mcp_server.tool_registry:
                        tool_func = mcp_server.tool_registry[tool_name]
                        
                        # Run async function
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(tool_func(**args))
                        loop.close()
                        
                        response = {
                            "jsonrpc": "2.0",
                            "result": result,
                            "id": data.get("id")
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32601,
                                "message": f"Tool '{tool_name}' not found"
                            },
                            "id": data.get("id")
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Method '{data.get('method')}' not supported"
                        },
                        "id": data.get("id")
                    }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": None
                }
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logs for cleaner output"""
        pass

def main():
    global mcp_server
    
    # Initialize MCP server
    print("Initializing MCP server...")
    mcp_server = StrunzKnowledgeMCP()
    print(f"Loaded {len(mcp_server.tool_registry)} tools")
    
    # Start HTTP server
    port = 8000
    server = HTTPServer(('localhost', port), MCPHandler)
    
    print(f"Starting Enhanced MCP server on port {port}...")
    print("Available endpoints:")
    print(f"  - Health: http://localhost:{port}/")
    print(f"  - MCP: http://localhost:{port}/mcp")
    print(f"  - Tools: {list(mcp_server.tool_registry.keys())[:5]}...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()