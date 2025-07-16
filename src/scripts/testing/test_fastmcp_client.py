#!/usr/bin/env python3
"""
Test Railway MCP endpoint using FastMCP client
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

async def test_railway_mcp():
    """Test the Railway MCP endpoint with FastMCP client"""
    try:
        from fastmcp import Client
        print("✅ FastMCP imported successfully")
    except ImportError:
        print("❌ FastMCP not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastmcp"])
        from fastmcp import Client
        print("✅ FastMCP installed and imported")
    
    # Railway MCP endpoint URL
    railway_sse_url = "https://strunz.up.railway.app/sse"
    
    print(f"\n🚀 Connecting to Railway MCP endpoint: {railway_sse_url}")
    
    try:
        # Connect to the Railway SSE endpoint
        async with Client(railway_sse_url) as client:
            print("✅ Connected to Railway MCP server!")
            
            # Test 1: List available tools
            print("\n📋 Testing list_tools()...")
            try:
                tools = await client.list_tools()
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                    print(f"   {i+1}. {tool.name}: {tool.description[:50]}...")
                if len(tools) > 5:
                    print(f"   ... and {len(tools) - 5} more tools")
            except Exception as e:
                print(f"❌ Error listing tools: {e}")
            
            # Test 2: Get server info
            print("\n📊 Testing server info...")
            try:
                # Try to get server capabilities
                if hasattr(client, 'server_info'):
                    info = client.server_info
                    print(f"✅ Server info: {info}")
                else:
                    print("ℹ️  Server info not available in client")
            except Exception as e:
                print(f"❌ Error getting server info: {e}")
            
            # Test 3: Call a simple tool
            print("\n🔧 Testing tool call: get_mcp_server_purpose...")
            try:
                result = await client.call_tool("get_mcp_server_purpose", {})
                print("✅ Tool call successful!")
                print(f"   Result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"   Keys: {list(result.keys())}")
                elif isinstance(result, str):
                    print(f"   Result: {result[:200]}...")
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
            
            # Test 4: Search for content
            print("\n🔍 Testing knowledge search...")
            try:
                search_result = await client.call_tool(
                    "knowledge_search", 
                    {"query": "Vitamin D", "max_results": 3}
                )
                print("✅ Search successful!")
                if isinstance(search_result, dict) and 'results' in search_result:
                    print(f"   Found {len(search_result['results'])} results")
                else:
                    print(f"   Result: {str(search_result)[:200]}...")
            except Exception as e:
                print(f"❌ Error searching: {e}")
            
            print("\n✨ MCP client tests completed!")
            
    except Exception as e:
        print(f"\n❌ Failed to connect to Railway MCP endpoint: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try alternative connection methods
        print("\n🔄 Trying alternative connection methods...")
        
        # Try HTTP endpoint
        try:
            messages_url = "https://strunz.up.railway.app/messages"
            print(f"   Trying HTTP messages endpoint: {messages_url}")
            
            # FastMCP might need OAuth token
            print("   ⚠️  Note: OAuth authentication may be required")
            
        except Exception as e2:
            print(f"   ❌ Alternative method failed: {e2}")

async def test_oauth_flow():
    """Test OAuth authentication flow"""
    print("\n🔐 Testing OAuth endpoints...")
    
    import aiohttp
    
    oauth_discovery = "https://strunz.up.railway.app/.well-known/oauth-authorization-server"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Get OAuth metadata
            async with session.get(oauth_discovery) as resp:
                if resp.status == 200:
                    metadata = await resp.json()
                    print("✅ OAuth discovery endpoint working!")
                    print(f"   Authorization: {metadata.get('authorization_endpoint')}")
                    print(f"   Token: {metadata.get('token_endpoint')}")
                    print(f"   Registration: {metadata.get('registration_endpoint')}")
                else:
                    print(f"❌ OAuth discovery failed: {resp.status}")
        except Exception as e:
            print(f"❌ OAuth test failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 FastMCP Client Test Suite for Railway Deployment")
    print("=" * 50)
    
    # Test MCP connection
    await test_railway_mcp()
    
    # Test OAuth endpoints
    await test_oauth_flow()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())