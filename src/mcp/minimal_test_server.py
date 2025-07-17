#!/usr/bin/env python3
"""
Minimal MCP Test Server

A minimal MCP server implementation to test prompts capability.
This helps isolate issues with Claude.ai/Desktop integration.
"""

import json
import sys
from typing import Dict, Any


class MinimalMCPServer:
    def __init__(self):
        self.tools = {
            "test_tool": self.test_tool
        }
        self.prompts = [
            {
                "name": "test_prompt",
                "description": "A test prompt",
                "arguments": []
            }
        ]
        
    def test_tool(self, **kwargs) -> str:
        return "Test tool response"
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        try:
            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False}  # Critical!
                    },
                    "serverInfo": {
                        "name": "Minimal Test Server",
                        "version": "1.0.0"
                    }
                }
                
            elif method == "initialized":
                response["result"] = {}
                
            elif method == "tools/list":
                response["result"] = {
                    "tools": [
                        {
                            "name": name,
                            "description": f"Test tool: {name}",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "additionalProperties": True
                            }
                        }
                        for name in self.tools.keys()
                    ]
                }
                
            elif method == "prompts/list":
                response["result"] = {
                    "prompts": self.prompts
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                if tool_name in self.tools:
                    result = self.tools[tool_name](**params.get("arguments", {}))
                    response["result"] = {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                else:
                    response["error"] = {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                    
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
                
        except Exception as e:
            response["error"] = {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
            
        return response
        
    def run_stdio(self):
        """Run server in stdio mode"""
        print("Minimal MCP Test Server started", file=sys.stderr)
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                request = json.loads(line.strip())
                response = self.handle_request(request)
                
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    },
                    "id": None
                }
                print(json.dumps(error_response), flush=True)
                
            except KeyboardInterrupt:
                break
                
            except Exception as e:
                print(f"Server error: {e}", file=sys.stderr)
                

def main():
    server = MinimalMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()