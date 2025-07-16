#!/usr/bin/env python3
"""
Simple SSE server for testing MCP inspector
"""

import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class SSEHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Health check
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "server": "Test SSE MCP Server",
                "transport": "sse"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/sse' or self.path == '/':
            # SSE endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send initial MCP initialization event
            init_event = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "test-sse-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            self.wfile.write(f"event: message\n".encode())
            self.wfile.write(f"data: {json.dumps(init_event)}\n\n".encode())
            self.wfile.flush()
            
            # Send periodic heartbeat
            try:
                for i in range(10):  # Send 10 heartbeats then close
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "notifications/ping",
                        "params": {
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    self.wfile.write(f"event: heartbeat\n".encode())
                    self.wfile.write(f"data: {json.dumps(heartbeat)}\n\n".encode())
                    self.wfile.flush()
                    
                    # Sleep for 1 second
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                print(f"SSE connection closed: {e}")
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
                
                if method == 'initialize':
                    response = {
                        "jsonrpc": "2.0",
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "test-sse-server",
                                "version": "1.0.0"
                            }
                        },
                        "id": request_data.get('id', 1)
                    }
                elif method == 'tools/list':
                    response = {
                        "jsonrpc": "2.0",
                        "result": {
                            "tools": [
                                {
                                    "name": "test_sse_tool",
                                    "description": "A test tool for SSE",
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

def start_sse_server():
    """Start the SSE server"""
    server = HTTPServer(('localhost', 8002), SSEHandler)
    print("✓ SSE server created on http://localhost:8002")
    print("✓ Health check: http://localhost:8002/")
    print("✓ SSE endpoint: http://localhost:8002/sse")
    print("Starting server... (Press Ctrl+C to stop)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("✓ Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_sse_server()