#!/usr/bin/env python3
"""
Test production server prompts capability
"""

import asyncio
import aiohttp
import json


async def test_production_server():
    """Test the production server's prompts capability"""
    base_url = "https://strunz.up.railway.app"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Production Server Prompts Capability")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1. Health Check:")
        async with session.get(f"{base_url}/") as resp:
            data = await resp.json()
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            
        # Test 2: Initialize with prompts check
        print("\n2. MCP Initialize:")
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "clientInfo": {
                    "name": "Prompts Test Client",
                    "version": "1.0"
                }
            },
            "id": 1
        }
        
        async with session.post(f"{base_url}/messages", json=payload) as resp:
            data = await resp.json()
            result = data.get("result", {})
            capabilities = result.get("capabilities", {})
            
            print(f"   Protocol: {result.get('protocolVersion')}")
            print(f"   Server: {result.get('serverInfo', {}).get('name')}")
            print(f"   Version: {result.get('serverInfo', {}).get('version')}")
            print(f"   Capabilities: {list(capabilities.keys())}")
            
            if "prompts" in capabilities:
                print("   ✅ Prompts capability is present")
            else:
                print("   ❌ Prompts capability is MISSING")
                
        # Test 3: List prompts
        print("\n3. List Prompts:")
        payload = {
            "jsonrpc": "2.0",
            "method": "prompts/list",
            "params": {},
            "id": 2
        }
        
        async with session.post(f"{base_url}/messages", json=payload) as resp:
            data = await resp.json()
            
            if "error" in data:
                print(f"   ❌ Error: {data['error']['message']}")
            elif "result" in data:
                prompts = data["result"].get("prompts", [])
                print(f"   ✅ Found {len(prompts)} prompts")
                
                # List prompts if any
                for prompt in prompts[:3]:  # First 3
                    print(f"      - {prompt.get('name', 'Unknown')}")
                    
        # Test 4: Get a specific prompt (if any exist)
        if prompts:
            print("\n4. Get Specific Prompt:")
            first_prompt = prompts[0]
            payload = {
                "jsonrpc": "2.0",
                "method": "prompts/get",
                "params": {
                    "name": first_prompt.get("name")
                },
                "id": 3
            }
            
            async with session.post(f"{base_url}/messages", json=payload) as resp:
                data = await resp.json()
                
                if "error" in data:
                    print(f"   ❌ Error: {data['error']['message']}")
                elif "result" in data:
                    print(f"   ✅ Got prompt: {first_prompt.get('name')}")
                    
        # Test 5: Check SSE endpoint
        print("\n5. SSE Endpoint Test:")
        async with session.get(f"{base_url}/sse") as resp:
            # Read first few lines
            lines = []
            async for line in resp.content:
                lines.append(line.decode('utf-8').strip())
                if len(lines) >= 3:
                    break
                    
            for line in lines:
                if line.startswith("data:"):
                    print(f"   ✅ SSE working: {line[:60]}...")
                    
        print("\n" + "=" * 50)
        print("Test Complete")
        
        # Summary
        print("\nSummary:")
        print(f"- Server Version: {data.get('version')}")
        print(f"- Prompts Capability: {'Present' if 'prompts' in capabilities else 'MISSING'}")
        print(f"- Prompts Method: {'Working' if not 'error' in data else 'Not Working'}")
        

async def test_local_fastmcp():
    """Test if FastMCP is the issue"""
    print("\nChecking FastMCP Implementation...")
    print("=" * 50)
    
    try:
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        
        server = StrunzKnowledgeMCP()
        app = server.app
        
        print(f"Server Type: {type(app)}")
        print(f"App Name: {getattr(app, 'name', 'Unknown')}")
        
        # Check for prompts
        if hasattr(app, '_prompts'):
            prompts = getattr(app, '_prompts', {})
            print(f"✅ Found {len(prompts)} prompts registered")
            for name in list(prompts.keys())[:3]:
                print(f"   - {name}")
        else:
            print("❌ No prompts registry found")
            
        # Check capabilities
        if hasattr(app, 'capabilities'):
            print(f"Capabilities: {app.capabilities}")
            
    except Exception as e:
        print(f"Error: {e}")
        

if __name__ == "__main__":
    # Test production
    asyncio.run(test_production_server())
    
    # Test local
    asyncio.run(test_local_fastmcp())