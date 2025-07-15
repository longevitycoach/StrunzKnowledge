#!/usr/bin/env python3
"""Test SSE endpoint for MCP protocol compliance"""

import asyncio
import json
import aiohttp
import sys

async def test_sse_endpoint(url: str):
    """Test SSE endpoint and MCP protocol messages"""
    print(f"Testing SSE endpoint: {url}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status != 200:
                    print(f"Error: {await response.text()}")
                    return
                
                # Read SSE stream
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            parsed = json.loads(data)
                            print(f"\nReceived: {json.dumps(parsed, indent=2)}")
                            
                            # Check for MCP protocol messages
                            if "jsonrpc" in parsed:
                                print("✓ Valid JSON-RPC message")
                            elif "type" in parsed:
                                print(f"✓ Event type: {parsed['type']}")
                                
                        except json.JSONDecodeError:
                            print(f"Raw data: {data}")
                    elif line.startswith('event: '):
                        print(f"\nEvent: {line[7:]}")
                        
        except Exception as e:
            print(f"Error: {e}")

async def test_mcp_tools_list(base_url: str):
    """Test MCP tools/list method"""
    url = base_url.replace('/sse', '/mcp')
    print(f"\nTesting MCP tools/list at: {url}")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=request) as response:
                print(f"Status: {response.status}")
                result = await response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                if "result" in result and "tools" in result["result"]:
                    print(f"\n✓ Found {len(result['result']['tools'])} tools")
                    
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Test both local and remote endpoints"""
    
    # Test remote Railway endpoint
    print("=== Testing Railway SSE Endpoint ===")
    await test_sse_endpoint("https://strunz.up.railway.app/sse")
    await test_mcp_tools_list("https://strunz.up.railway.app")
    
    print("\n" + "="*50 + "\n")
    
    # Test local endpoint
    print("=== Testing Local SSE Endpoint ===")
    await test_sse_endpoint("http://localhost:8000/sse")
    await test_mcp_tools_list("http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())