#!/usr/bin/env python3
"""
Test MCP tools through the messages endpoint
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_mcp_tools():
    """Test MCP tools via messages endpoint"""
    base_url = "https://strunz.up.railway.app"
    
    print("🧪 Testing MCP Tools via Messages Endpoint")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Initialize connection
        print("\n1️⃣ Initializing MCP connection...")
        
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "MCP Tools Test Client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        async with session.post(
            f"{base_url}/messages",
            json=init_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print("✅ Initialized successfully")
                server_info = result.get('result', {}).get('serverInfo', {})
                print(f"   Server: {server_info.get('name')} v{server_info.get('version')}")
                capabilities = result.get('result', {}).get('capabilities', {})
                print(f"   Capabilities: {list(capabilities.keys())}")
            else:
                print(f"❌ Initialization failed: {resp.status}")
                return
        
        # Step 2: List available tools
        print("\n2️⃣ Listing available tools...")
        
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        tools = []
        async with session.post(
            f"{base_url}/messages",
            json=list_tools_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                tools = result.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:10]):
                    print(f"   {i+1:2}. {tool.get('name'):30} - {tool.get('description', '')[:50]}...")
                if len(tools) > 10:
                    print(f"   ... and {len(tools) - 10} more tools")
            else:
                print(f"❌ List tools failed: {resp.status}")
                return
        
        # Step 3: Test specific tools
        print("\n3️⃣ Testing specific MCP tools...")
        
        # Test 1: get_mcp_server_purpose
        print("\n   📋 Testing get_mcp_server_purpose...")
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            },
            "id": 3
        }
        
        async with session.post(
            f"{base_url}/messages",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                tool_result = result.get('result', {})
                print("   ✅ Tool call successful")
                
                # Pretty print the result
                if isinstance(tool_result, dict):
                    for key, value in tool_result.items():
                        if isinstance(value, list) and len(value) > 3:
                            print(f"      {key}: {len(value)} items")
                        else:
                            print(f"      {key}: {value}")
                else:
                    print(f"      Result: {str(tool_result)[:200]}...")
            else:
                print(f"   ❌ Tool call failed: {resp.status}")
        
        # Test 2: knowledge_search
        print("\n   🔍 Testing knowledge_search...")
        search_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "knowledge_search",
                "arguments": {
                    "query": "Vitamin D Dosierung",
                    "max_results": 3
                }
            },
            "id": 4
        }
        
        async with session.post(
            f"{base_url}/messages",
            json=search_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                search_result = result.get('result', {})
                print("   ✅ Search successful")
                
                if isinstance(search_result, dict) and 'results' in search_result:
                    results = search_result['results']
                    print(f"      Found {len(results)} results:")
                    for i, res in enumerate(results[:3]):
                        print(f"      {i+1}. Score: {res.get('score', 0):.3f}")
                        print(f"         Content: {res.get('content', '')[:100]}...")
                        if 'metadata' in res:
                            source = res['metadata'].get('source', 'Unknown')
                            print(f"         Source: {source}")
            else:
                print(f"   ❌ Search failed: {resp.status}")
        
        # Test 3: get_dr_strunz_biography
        print("\n   👨‍⚕️ Testing get_dr_strunz_biography...")
        bio_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_dr_strunz_biography",
                "arguments": {}
            },
            "id": 5
        }
        
        async with session.post(
            f"{base_url}/messages",
            json=bio_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                bio_result = result.get('result', {})
                print("   ✅ Biography retrieved")
                
                # Show first part of biography
                if isinstance(bio_result, dict):
                    bio_text = bio_result.get('biography', '')
                    print(f"      {bio_text[:300]}...")
                elif isinstance(bio_result, str):
                    print(f"      {bio_result[:300]}...")
            else:
                print(f"   ❌ Biography failed: {resp.status}")
        
        print("\n✨ MCP tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())