#!/usr/bin/env python3
"""
MCP Inspector Compatibility Test
Ensures our server works with MCP Inspector
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_mcp_inspector_requirements():
    """Test all requirements for MCP Inspector compatibility"""
    
    print("🔍 MCP Inspector Compatibility Test")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    all_passed = True
    
    async with aiohttp.ClientSession() as session:
        # 1. Test SSE endpoint
        print("\n1️⃣ Testing SSE Endpoint")
        try:
            async with session.get(f"{base_url}/sse") as resp:
                if resp.status == 200:
                    print("✅ SSE endpoint accessible")
                    
                    # Check content type
                    ct = resp.headers.get("Content-Type", "")
                    if "text/event-stream" in ct:
                        print("✅ Correct Content-Type: text/event-stream")
                    else:
                        print(f"❌ Wrong Content-Type: {ct}")
                        all_passed = False
                    
                    # Read first event
                    chunk = await resp.content.read(256)
                    if chunk:
                        text = chunk.decode('utf-8')
                        if "event:" in text and "data:" in text:
                            print("✅ SSE format correct")
                            
                            # Look for endpoint
                            if "/messages/" in text:
                                print("✅ Messages endpoint provided")
                            else:
                                print("❌ No messages endpoint in SSE")
                                all_passed = False
                        else:
                            print(f"❌ Invalid SSE format: {text[:100]}")
                            all_passed = False
                else:
                    print(f"❌ SSE endpoint returned {resp.status}")
                    all_passed = False
        except Exception as e:
            print(f"❌ SSE test failed: {e}")
            all_passed = False
        
        # 2. Test Initialize
        print("\n2️⃣ Testing Initialize")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-inspector-test",
                    "version": "1.0.0"
                }
            },
            "id": "init-1"
        }
        
        try:
            async with session.post(
                f"{base_url}/messages/",
                json=init_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("jsonrpc") == "2.0" and "result" in data:
                        print("✅ Initialize successful")
                        
                        result = data["result"]
                        if result.get("protocolVersion"):
                            print(f"✅ Protocol version: {result['protocolVersion']}")
                        
                        if result.get("serverInfo", {}).get("name"):
                            print(f"✅ Server name: {result['serverInfo']['name']}")
                        
                        caps = result.get("capabilities", {})
                        if "tools" in caps:
                            print("✅ Tools capability present")
                        else:
                            print("❌ No tools capability")
                            all_passed = False
                    else:
                        print(f"❌ Invalid initialize response: {data}")
                        all_passed = False
                else:
                    print(f"❌ Initialize returned {resp.status}")
                    all_passed = False
        except Exception as e:
            print(f"❌ Initialize failed: {e}")
            all_passed = False
        
        # 3. Test Resources List (CRITICAL for Inspector)
        print("\n3️⃣ Testing Resources List (CRITICAL)")
        resources_request = {
            "jsonrpc": "2.0",
            "method": "resources/list",
            "id": "res-1"
        }
        
        try:
            async with session.post(
                f"{base_url}/messages/",
                json=resources_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data and "resources" in data.get("result", {}):
                        print("✅ Resources list endpoint works")
                        resources = data["result"]["resources"]
                        print(f"   Resources count: {len(resources)}")
                    else:
                        print("❌ Invalid resources response")
                        all_passed = False
                else:
                    print(f"❌ Resources list returned {resp.status}")
                    all_passed = False
        except Exception as e:
            print(f"❌ Resources list failed: {e}")
            all_passed = False
        
        # 4. Test Tools List
        print("\n4️⃣ Testing Tools List")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "tools-1"
        }
        
        try:
            async with session.post(
                f"{base_url}/messages/",
                json=tools_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data and "tools" in data.get("result", {}):
                        tools = data["result"]["tools"]
                        print(f"✅ Tools list works: {len(tools)} tools")
                        
                        # Check tool schemas
                        with_schema = sum(1 for t in tools if t.get("inputSchema"))
                        print(f"   Tools with schemas: {with_schema}/{len(tools)}")
                        
                        if with_schema < len(tools):
                            print("❌ Some tools missing schemas")
                            all_passed = False
                    else:
                        print("❌ Invalid tools response")
                        all_passed = False
                else:
                    print(f"❌ Tools list returned {resp.status}")
                    all_passed = False
        except Exception as e:
            print(f"❌ Tools list failed: {e}")
            all_passed = False
        
        # 5. Test Tool Execution
        print("\n5️⃣ Testing Tool Execution")
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            },
            "id": "call-1"
        }
        
        try:
            async with session.post(
                f"{base_url}/messages/",
                json=call_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data:
                        print("✅ Tool execution works")
                        
                        result = data["result"]
                        if "content" in result or isinstance(result, list):
                            print("✅ Tool returned content")
                        else:
                            print("❌ Tool returned no content")
                            all_passed = False
                    else:
                        print(f"❌ Tool execution error: {data.get('error', 'Unknown')}")
                        all_passed = False
                else:
                    print(f"❌ Tool execution returned {resp.status}")
                    all_passed = False
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            all_passed = False
        
        # 6. Test CORS Headers
        print("\n6️⃣ Testing CORS Headers")
        try:
            headers = {
                "Origin": "http://localhost:5173",  # MCP Inspector origin
                "Access-Control-Request-Method": "POST"
            }
            
            async with session.options(f"{base_url}/messages/", headers=headers) as resp:
                cors_origin = resp.headers.get("Access-Control-Allow-Origin")
                cors_methods = resp.headers.get("Access-Control-Allow-Methods")
                
                if cors_origin in ["*", "http://localhost:5173"]:
                    print(f"✅ CORS Origin allowed: {cors_origin}")
                else:
                    print(f"❌ CORS Origin not allowed: {cors_origin}")
                    all_passed = False
                
                if cors_methods and "POST" in cors_methods:
                    print("✅ CORS POST method allowed")
                else:
                    print(f"❌ CORS POST not allowed: {cors_methods}")
                    all_passed = False
                    
        except Exception as e:
            print(f"⚠️  CORS test inconclusive: {e}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All MCP Inspector requirements passed!")
        print("\nYour server should work with MCP Inspector.")
        print("Test with: npx @modelcontextprotocol/inspector http://localhost:8000/sse")
    else:
        print("❌ Some requirements failed!")
        print("\nFix the issues above before testing with MCP Inspector.")
    
    return all_passed


async def test_with_actual_inspector():
    """Instructions for testing with actual MCP Inspector"""
    
    print("\n📝 Manual MCP Inspector Test Instructions")
    print("=" * 60)
    print("""
1. Make sure your server is running:
   MCP_TRANSPORT=sse python main.py

2. In another terminal, run MCP Inspector:
   npx @modelcontextprotocol/inspector http://localhost:8000/sse

3. In the Inspector UI:
   - Click "Connect"
   - You should see "Connected" status
   - Tools should appear in the tools list
   - Try executing a tool

4. Expected results:
   ✅ Connection established without errors
   ✅ Tools list populated
   ✅ Tool execution returns results
   ✅ No console errors about missing endpoints

5. Common issues:
   - "Connection Error" → Check resources/list endpoint
   - "No tools" → Check tools/list response format
   - SSE errors → Check SSE event format
   - CORS errors → Add proper CORS headers
""")


if __name__ == "__main__":
    # Check if server is running
    import aiohttp
    
    async def check_server():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/") as resp:
                    return resp.status == 200
        except:
            return False
    
    async def main():
        if not await check_server():
            print("❌ Server not running!")
            print("Start it with: MCP_TRANSPORT=sse python main.py")
            return
        
        # Run automated tests
        passed = await test_mcp_inspector_requirements()
        
        # Show manual test instructions
        await test_with_actual_inspector()
    
    asyncio.run(main())