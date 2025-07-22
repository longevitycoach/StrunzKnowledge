#!/usr/bin/env python3
"""
Test Claude.ai Integration Flow
Debug why Claude.ai shows "disabled" after successful OAuth
"""

import asyncio
import aiohttp
import json
from urllib.parse import urlencode

async def test_claude_ai_flow():
    base_url = "https://strunz.up.railway.app"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Claude.ai Integration Flow\n")
        
        # 1. Test MCP resource discovery
        print("1️⃣ Testing MCP Resource Discovery")
        async with session.get(f"{base_url}/.well-known/mcp/resource") as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
        # 2. Test Claude.ai specific endpoint
        print("\n2️⃣ Testing Claude.ai Start Auth Endpoint")
        async with session.get(
            f"{base_url}/api/organizations/test-org/mcp/start-auth/test-auth",
            params={"redirect_url": "https://claude.ai/callback"}
        ) as resp:
            if resp.headers.get("content-type", "").startswith("application/json"):
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"   Status: {resp.status}")
                print(f"   Redirect: {resp.headers.get('Location', 'No redirect')}")
                
        # 3. Test OAuth flow
        print("\n3️⃣ Testing OAuth Authorization")
        auth_params = {
            "response_type": "code",
            "client_id": "client_claude_test",
            "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
            "code_challenge": "test_challenge",
            "code_challenge_method": "S256",
            "state": "test_state",
            "scope": "read write"
        }
        
        async with session.get(
            f"{base_url}/oauth/authorize",
            params=auth_params,
            allow_redirects=False
        ) as resp:
            print(f"   Status: {resp.status}")
            print(f"   Location: {resp.headers.get('Location', 'No redirect')}")
            
        # 4. Test SSE endpoint
        print("\n4️⃣ Testing SSE Endpoint")
        async with session.get(f"{base_url}/sse") as resp:
            print(f"   Status: {resp.status}")
            print(f"   Content-Type: {resp.headers.get('content-type')}")
            # Read first event
            async for line in resp.content:
                decoded = line.decode('utf-8').strip()
                if decoded.startswith("event:"):
                    print(f"   First event: {decoded[:100]}...")
                    break
                    
        # 5. Test messages endpoint
        print("\n5️⃣ Testing Messages Endpoint (Initialize)")
        async with session.post(
            f"{base_url}/messages",
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "2025-03-26"},
                "id": 1
            }
        ) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
        # 6. Test tools list
        print("\n6️⃣ Testing Tools List")
        async with session.post(
            f"{base_url}/messages",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
        ) as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Tools count: {len(data.get('result', {}).get('tools', []))}")
            
        # 7. Test POST to root (Claude.ai callback)
        print("\n7️⃣ Testing POST to / (Claude.ai callback)")
        async with session.post(f"{base_url}/") as resp:
            data = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_claude_ai_flow())