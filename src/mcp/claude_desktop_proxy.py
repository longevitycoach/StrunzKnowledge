#!/usr/bin/env python3
"""
Claude Desktop STDIO to HTTP-SSE Proxy
Converts STDIO transport to HTTP-SSE for Railway deployment
"""

import asyncio
import json
import sys
import aiohttp
from typing import Dict, Any

class StdioToHttpSseProxy:
    """Proxy that converts STDIO to HTTP-SSE MCP communication"""
    
    def __init__(self, remote_url: str):
        self.remote_url = remote_url
        self.session = None
        self.request_id = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    async def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send MCP request to remote HTTP server"""
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.next_id()
        }
        
        try:
            async with self.session.post(
                f"{self.remote_url}/mcp",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"HTTP {response.status}"
                        },
                        "id": request_data["id"]
                    }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_data["id"]
            }
    
    async def process_stdio_requests(self):
        """Process STDIO requests from Claude Desktop"""
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    method = request.get("method", "")
                    params = request.get("params", {})
                    
                    # Forward to remote server
                    response = await self.send_mcp_request(method, params)
                    
                    # Send response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError:
                    # Invalid JSON, send error response
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            sys.stderr.write(f"Proxy error: {e}\n")

async def main():
    """Main proxy function"""
    # Use Railway deployment URL
    remote_url = "https://strunz.up.railway.app"
    
    async with StdioToHttpSseProxy(remote_url) as proxy:
        await proxy.process_stdio_requests()

if __name__ == "__main__":
    asyncio.run(main())