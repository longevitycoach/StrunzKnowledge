#!/usr/bin/env python3
"""
Simple MCP client test for Railway endpoint
Tests MCP protocol without requiring fastmcp installation
"""
import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

class SimpleMCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def test_sse_connection(self):
        """Test SSE endpoint connection"""
        print(f"\n🔌 Testing SSE connection to {self.base_url}/sse")
        
        try:
            # Try to connect to SSE endpoint
            async with self.session.get(
                f"{self.base_url}/sse",
                headers={"Accept": "text/event-stream"}
            ) as resp:
                print(f"   Status: {resp.status}")
                print(f"   Content-Type: {resp.headers.get('Content-Type', 'Not specified')}")
                
                if resp.status == 200:
                    # Read first few events
                    print("   ✅ SSE endpoint accessible")
                    
                    # Try to read some data
                    data = await resp.content.read(1000)
                    if data:
                        print(f"   📨 Received data: {data[:100]}...")
                    return True
                elif resp.status == 401:
                    print("   ⚠️  401 Unauthorized - OAuth token required")
                    return False
                else:
                    print(f"   ❌ Unexpected status: {resp.status}")
                    body = await resp.text()
                    print(f"   Response: {body[:200]}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ SSE connection failed: {e}")
            return False
    
    async def test_messages_endpoint(self):
        """Test messages endpoint (JSON-RPC style)"""
        print(f"\n📬 Testing messages endpoint at {self.base_url}/messages")
        
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "SimpleMCPClient",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/messages",
                json=init_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                print(f"   Status: {resp.status}")
                
                if resp.status == 200:
                    result = await resp.json()
                    print("   ✅ Messages endpoint working")
                    print(f"   Server: {result.get('result', {}).get('serverInfo', {})}")
                    return True
                elif resp.status == 401:
                    print("   ⚠️  401 Unauthorized - OAuth token required")
                    return False
                else:
                    print(f"   ❌ Unexpected status: {resp.status}")
                    body = await resp.text()
                    print(f"   Response: {body[:200]}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Messages endpoint failed: {e}")
            return False
    
    async def test_mcp_endpoint(self):
        """Test /mcp endpoint (JSON-RPC)"""
        print(f"\n🔧 Testing MCP endpoint at {self.base_url}/mcp")
        
        # List tools request
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=tools_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                print(f"   Status: {resp.status}")
                
                if resp.status == 200:
                    result = await resp.json()
                    tools = result.get('result', {}).get('tools', [])
                    print(f"   ✅ MCP endpoint working - Found {len(tools)} tools")
                    
                    # Show first 5 tools
                    for i, tool in enumerate(tools[:5]):
                        print(f"      {i+1}. {tool.get('name')}")
                    if len(tools) > 5:
                        print(f"      ... and {len(tools) - 5} more")
                    return True
                else:
                    print(f"   ❌ Unexpected status: {resp.status}")
                    body = await resp.text()
                    print(f"   Response: {body[:200]}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ MCP endpoint failed: {e}")
            return False
    
    async def test_oauth_endpoints(self):
        """Test OAuth endpoints"""
        print(f"\n🔐 Testing OAuth endpoints")
        
        # Test discovery endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/.well-known/oauth-authorization-server"
            ) as resp:
                if resp.status == 200:
                    metadata = await resp.json()
                    print("   ✅ OAuth discovery working")
                    print(f"      Authorization: {metadata.get('authorization_endpoint')}")
                    print(f"      Token: {metadata.get('token_endpoint')}")
                    print(f"      Registration: {metadata.get('registration_endpoint')}")
                    
                    # Test dynamic client registration
                    await self.test_client_registration(metadata.get('registration_endpoint'))
                    return True
                else:
                    print(f"   ❌ OAuth discovery failed: {resp.status}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ OAuth test failed: {e}")
            return False
    
    async def test_client_registration(self, registration_endpoint):
        """Test OAuth dynamic client registration"""
        print(f"\n   📝 Testing dynamic client registration...")
        
        if not registration_endpoint:
            print("      ❌ No registration endpoint found")
            return
        
        # Registration request
        reg_request = {
            "client_name": "MCP Test Client",
            "client_uri": "https://example.com",
            "redirect_uris": ["http://localhost:8080/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read write",
            "token_endpoint_auth_method": "client_secret_basic"
        }
        
        try:
            async with self.session.post(
                registration_endpoint,
                json=reg_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                print(f"      Status: {resp.status}")
                
                if resp.status == 201 or resp.status == 200:
                    result = await resp.json()
                    print("      ✅ Client registration successful!")
                    print(f"      Client ID: {result.get('client_id', 'Not provided')}")
                    print(f"      Client Secret: {'*' * 16 if result.get('client_secret') else 'Not provided'}")
                else:
                    print(f"      ❌ Registration failed: {resp.status}")
                    body = await resp.text()
                    print(f"      Response: {body[:200]}")
                    
        except Exception as e:
            print(f"      ❌ Registration error: {e}")

async def main():
    """Run all tests"""
    print("🧪 Simple MCP Client Test for Railway Deployment")
    print("=" * 50)
    print(f"📅 Test Date: {datetime.now().isoformat()}")
    print(f"🌐 Target: https://strunz.up.railway.app")
    
    # Test Railway deployment
    base_url = "https://strunz.up.railway.app"
    
    async with SimpleMCPClient(base_url) as client:
        # Run all tests
        results = {
            "SSE": await client.test_sse_connection(),
            "Messages": await client.test_messages_endpoint(),
            "MCP": await client.test_mcp_endpoint(),
            "OAuth": await client.test_oauth_endpoints()
        }
        
        # Summary
        print("\n📊 Test Summary:")
        print("-" * 30)
        for endpoint, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {endpoint:10} {status}")
        
        success_rate = sum(results.values()) / len(results) * 100
        print(f"\n   Success Rate: {success_rate:.0f}%")
        
        if success_rate < 100:
            print("\n⚠️  Note: Some endpoints may require OAuth authentication")
            print("   Consider using an OAuth token for authenticated requests")

if __name__ == "__main__":
    asyncio.run(main())