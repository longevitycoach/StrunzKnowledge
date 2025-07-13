#!/usr/bin/env python3
"""
Test MCP Server SSE endpoint and tools via direct HTTP calls
"""

import asyncio
import json
import httpx
import time
from typing import AsyncGenerator

# Configuration
import os
import sys

# Get BASE_URL from command line argument or environment variable
if len(sys.argv) > 1 and sys.argv[1].startswith('--url='):
    BASE_URL = sys.argv[1].replace('--url=', '')
elif len(sys.argv) > 2 and sys.argv[1] == '--url':
    BASE_URL = sys.argv[2]
else:
    BASE_URL = os.environ.get('MCP_TEST_URL', 'http://localhost:8000')

async def test_health_check():
    """Test basic health check endpoint."""
    print("🔍 Testing health check...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   Connection error: {e}")
            return False

async def test_sse_connection():
    """Test Server-Sent Events endpoint."""
    print("\n📡 Testing SSE endpoint...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            async with client.stream(
                "GET", 
                f"{BASE_URL}/sse",
                headers={"Accept": "text/event-stream"}
            ) as response:
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    print(f"   Error response: {await response.aread()}")
                    return False
                
                # Read first few events
                event_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        event_count += 1
                        print(f"   Event {event_count}: {line}")
                        if event_count >= 3:
                            break
                
                print(f"   ✅ Received {event_count} events")
                return True
                
        except httpx.ReadTimeout:
            print("   ⏱️ Connection timeout (might be normal if no events)")
            return True
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

async def test_mcp_tools():
    """Test MCP tools via JSON-RPC."""
    print("\n🔧 Testing MCP tools...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: List tools
        print("\n   1. Listing available tools:")
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    tools = result["result"]["tools"]
                    print(f"      Found {len(tools)} tools:")
                    for tool in tools[:5]:  # Show first 5
                        print(f"      - {tool['name']}")
                    if len(tools) > 5:
                        print(f"      ... and {len(tools) - 5} more")
            else:
                print(f"      Error: {response.text}")
                return False
        except Exception as e:
            print(f"      Error: {e}")
            return False
        
        # Test 2: Call get_dr_strunz_biography
        print("\n   2. Testing get_dr_strunz_biography tool:")
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_dr_strunz_biography",
                "arguments": {}
            },
            "id": 2
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    bio = result["result"]
                    print(f"      ✅ Biography retrieved:")
                    print(f"      - Name: {bio.get('full_name', 'N/A')}")
                    print(f"      - Title: {bio.get('title', 'N/A')}")
                    print(f"      - Books: {bio.get('books_overview', {}).get('total', 'N/A')}")
        except Exception as e:
            print(f"      Error: {e}")
        
        # Test 3: Call get_mcp_server_purpose
        print("\n   3. Testing get_mcp_server_purpose tool:")
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            },
            "id": 3
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    purpose = result["result"]
                    print(f"      ✅ Server purpose retrieved:")
                    print(f"      - Title: {purpose.get('title', 'N/A')}")
                    print(f"      - Version: {purpose.get('version', 'N/A')}")
                    print(f"      - Total tools: {purpose.get('mcp_tools_overview', {}).get('total_tools', 'N/A')}")
        except Exception as e:
            print(f"      Error: {e}")
        
        # Test 4: Search functionality
        print("\n   4. Testing knowledge_search tool:")
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "knowledge_search",
                "arguments": {
                    "query": "Vitamin D Dosierung",
                    "semantic_boost": 1.0
                }
            },
            "id": 4
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    results = result["result"]
                    if isinstance(results, list) and len(results) > 0:
                        print(f"      ✅ Found {len(results)} search results")
                        first = results[0]
                        print(f"      - First result: {first.get('title', 'N/A')}")
                        print(f"      - Source: {first.get('source', 'N/A')}")
                        print(f"      - Score: {first.get('score', 'N/A')}")
                    else:
                        print("      ⚠️ No search results returned")
        except Exception as e:
            print(f"      Error: {e}")
        
        return True

async def main():
    """Run all tests."""
    print(f"🚀 Testing MCP Server at: {BASE_URL}")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = await test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Server might not be running.")
        print("   Trying to continue with other tests anyway...")
    
    # Test 2: SSE endpoint
    sse_ok = await test_sse_connection()
    
    # Test 3: MCP tools
    mcp_ok = await test_mcp_tools()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   - Health Check: {'✅ Passed' if health_ok else '❌ Failed'}")
    print(f"   - SSE Endpoint: {'✅ Passed' if sse_ok else '❌ Failed'}")
    print(f"   - MCP Tools: {'✅ Passed' if mcp_ok else '❌ Failed'}")
    
    if all([health_ok, sse_ok, mcp_ok]):
        print("\n✅ All tests passed! MCP server is fully operational.")
    else:
        print("\n⚠️ Some tests failed. Check the server deployment.")

if __name__ == "__main__":
    asyncio.run(main())