#!/usr/bin/env python3
"""
Simple MCP client to test your server locally
Works with both SSE and regular HTTP endpoints
"""

import asyncio
import aiohttp
import json
import sys

async def test_mcp_server():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MCP Server")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Server running: {data['service']} v{data['version']}")
                print(f"   Tools available: {data['tools_count']}")
            else:
                print(f"❌ Server not responding: {resp.status}")
                return
    
    # Test 2: SSE Connection
    print("\n2️⃣ Testing SSE connection...")
    session_id = None
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/sse", headers={"Accept": "text/event-stream"}) as resp:
            print(f"✅ SSE connected: {resp.status}")
            
            # Read first few events
            count = 0
            async for line in resp.content:
                decoded = line.decode('utf-8').strip()
                if decoded:
                    print(f"   Received: {decoded[:80]}...")
                    if "event: endpoint" in decoded:
                        # Extract session ID from next line
                        data_line = await resp.content.readline()
                        data = data_line.decode('utf-8').strip()
                        if "session_id=" in data:
                            session_id = data.split("session_id=")[1].strip()
                            print(f"   Session ID: {session_id}")
                    count += 1
                    if count > 5:
                        break
    
    # Test 3: Initialize
    print("\n3️⃣ Testing initialize...")
    async with aiohttp.ClientSession() as session:
        init_msg = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "Test Client", "version": "1.0.0"}
            }
        }
        
        url = f"{base_url}/messages/"
        if session_id:
            url += f"?session_id={session_id}"
            
        async with session.post(url, json=init_msg) as resp:
            result = await resp.json()
            if "result" in result:
                print(f"✅ Initialized: {result['result']['serverInfo']['name']}")
                print(f"   Capabilities: {list(result['result']['capabilities'].keys())}")
            else:
                print(f"❌ Initialize failed: {result}")
    
    # Test 4: List tools
    print("\n4️⃣ Testing tools/list...")
    async with aiohttp.ClientSession() as session:
        tools_msg = {
            "jsonrpc": "2.0",
            "id": "tools-1",
            "method": "tools/list"
        }
        
        async with session.post(f"{base_url}/messages/", json=tools_msg) as resp:
            result = await resp.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"✅ Found {len(tools)} tools")
                
                # Show first 3 tools with schemas
                for i, tool in enumerate(tools[:3]):
                    schema = tool.get("inputSchema", {})
                    props = schema.get("properties", {})
                    print(f"\n   Tool: {tool['name']}")
                    print(f"   Description: {tool['description'][:60]}...")
                    print(f"   Parameters: {list(props.keys())}")
                    
                # Count tools with proper schemas
                empty_count = sum(1 for t in tools if not t.get("inputSchema", {}).get("properties"))
                print(f"\n   📊 Schema Summary:")
                print(f"   - Tools with parameters: {len(tools) - empty_count}")
                print(f"   - Tools without parameters: {empty_count}")
            else:
                print(f"❌ Tools list failed: {result}")
    
    # Test 5: Call a tool
    print("\n5️⃣ Testing tool call (get_mcp_server_purpose)...")
    async with aiohttp.ClientSession() as session:
        call_msg = {
            "jsonrpc": "2.0",
            "id": "call-1",
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            }
        }
        
        async with session.post(f"{base_url}/messages/", json=call_msg) as resp:
            result = await resp.json()
            if "result" in result:
                print(f"✅ Tool executed successfully")
                content = result.get("result", {}).get("content", [])
                if content and isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")[:200]
                    print(f"   Response: {text}...")
            else:
                print(f"❌ Tool call failed: {result}")
    
    print("\n" + "=" * 60)
    print("✨ Test complete!")

if __name__ == "__main__":
    # Start your server first:
    # python src/mcp/claude_compatible_server.py
    
    print("Make sure your server is running on http://localhost:8000")
    print("Starting test in 2 seconds...\n")
    
    asyncio.run(test_mcp_server())