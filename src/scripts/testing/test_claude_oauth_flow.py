#!/usr/bin/env python3
"""
Test Claude.ai OAuth flow to debug "not_available" error
"""
import httpx
import json
import asyncio
from urllib.parse import urlparse, parse_qs

async def test_claude_oauth_flow():
    """Test the OAuth flow that Claude.ai uses"""
    base_url = "https://strunz.up.railway.app"
    
    print("🔍 Testing Claude.ai OAuth Flow")
    print("=" * 50)
    
    # Step 1: Check MCP resource discovery
    print("\n1️⃣ Checking MCP resource discovery...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/.well-known/mcp/resource")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ MCP Version: {data.get('mcpVersion')}")
                print(f"✅ Transport: {data.get('transport')}")
                print(f"✅ Auth Type: {data.get('authentication', {}).get('type')}")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 2: Check OAuth discovery
    print("\n2️⃣ Checking OAuth discovery...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/.well-known/oauth-authorization-server")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Issuer: {data.get('issuer')}")
                print(f"✅ Authorization Endpoint: {data.get('authorization_endpoint')}")
                print(f"✅ Token Endpoint: {data.get('token_endpoint')}")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 3: Test OAuth registration (what Claude does)
    print("\n3️⃣ Testing OAuth client registration...")
    async with httpx.AsyncClient() as client:
        try:
            register_data = {
                "client_name": "Claude Desktop",
                "redirect_uris": ["https://claude.ai/api/callback"],
                "grant_types": ["authorization_code"],
                "response_types": ["code"]
            }
            response = await client.post(
                f"{base_url}/oauth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Client ID: {data.get('client_id')}")
                print(f"✅ Client Name: {data.get('client_name')}")
                return data.get('client_id')
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 4: Test authorization endpoint
    print("\n4️⃣ Testing authorization endpoint...")
    client_id = "test_client_id"
    auth_url = f"{base_url}/oauth/authorize?client_id={client_id}&redirect_uri=https://claude.ai/callback&response_type=code&state=test123"
    print(f"Authorization URL: {auth_url}")
    
    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            response = await client.get(auth_url)
            print(f"Status: {response.status_code}")
            if response.status_code == 302:
                location = response.headers.get('location')
                print(f"✅ Redirect to: {location}")
                # Parse the authorization code
                parsed = urlparse(location)
                params = parse_qs(parsed.query)
                if 'code' in params:
                    print(f"✅ Authorization code: {params['code'][0]}")
            elif response.status_code == 200:
                print("✅ Authorization page returned (would show consent form)")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 5: Check SSE endpoint
    print("\n5️⃣ Testing SSE endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{base_url}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=5.0
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                # Read first few lines
                content = response.text[:200]
                if "event:" in content or "data:" in content:
                    print("✅ SSE stream is working")
                    print(f"Preview: {content[:100]}...")
                else:
                    print("❌ SSE stream format incorrect")
        except httpx.TimeoutException:
            print("⏱️ SSE timeout (expected for streaming)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 OAuth flow test complete")

if __name__ == "__main__":
    asyncio.run(test_claude_oauth_flow())