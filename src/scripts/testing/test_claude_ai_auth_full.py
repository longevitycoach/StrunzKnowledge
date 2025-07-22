#!/usr/bin/env python3
"""
Comprehensive Claude.ai Authentication Test
Tests SSE/HTTP transport with MCP spec authorization flow
According to: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
"""

import asyncio
import json
import httpx
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.parse

class ClaudeAIAuthTester:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": []
        }
    
    async def test_mcp_discovery(self) -> Dict[str, Any]:
        """Test MCP resource discovery endpoint"""
        print("\n🔍 Testing MCP Resource Discovery...")
        
        try:
            response = await self.client.get(f"{self.base_url}/.well-known/mcp/resource")
            result = {
                "test": "MCP Resource Discovery",
                "endpoint": "/.well-known/mcp/resource",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                result["data"] = data
                result["has_auth"] = "authentication" in data
                result["auth_type"] = data.get("authentication", {}).get("type")
                result["auth_required"] = data.get("authentication", {}).get("required", False)
                result["endpoints"] = data.get("endpoints", {})
                result["transport"] = data.get("transport", [])
            else:
                result["error"] = response.text
            
            return result
        except Exception as e:
            return {
                "test": "MCP Resource Discovery",
                "endpoint": "/.well-known/mcp/resource",
                "success": False,
                "error": str(e)
            }
    
    async def test_oauth_discovery(self) -> Dict[str, Any]:
        """Test OAuth authorization server metadata"""
        print("\n🔐 Testing OAuth Discovery...")
        
        try:
            response = await self.client.get(f"{self.base_url}/.well-known/oauth-authorization-server")
            result = {
                "test": "OAuth Discovery",
                "endpoint": "/.well-known/oauth-authorization-server",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                result["data"] = data
                result["authorization_endpoint"] = data.get("authorization_endpoint")
                result["token_endpoint"] = data.get("token_endpoint")
                result["registration_endpoint"] = data.get("registration_endpoint")
                result["grant_types"] = data.get("grant_types_supported", [])
                result["response_types"] = data.get("response_types_supported", [])
            else:
                result["error"] = response.text
            
            return result
        except Exception as e:
            return {
                "test": "OAuth Discovery",
                "endpoint": "/.well-known/oauth-authorization-server",
                "success": False,
                "error": str(e)
            }
    
    async def test_claude_ai_endpoint(self) -> Dict[str, Any]:
        """Test Claude.ai specific authentication endpoint"""
        print("\n🤖 Testing Claude.ai Authentication Endpoint...")
        
        org_id = "test-org-" + str(uuid.uuid4())[:8]
        auth_id = "test-auth-" + str(uuid.uuid4())[:8]
        
        try:
            url = f"{self.base_url}/api/organizations/{org_id}/mcp/start-auth/{auth_id}"
            response = await self.client.get(
                url,
                params={
                    "redirect_url": "https://claude.ai/api/callback",
                    "open_in_browser": 0
                },
                follow_redirects=False
            )
            
            result = {
                "test": "Claude.ai Authentication Endpoint",
                "endpoint": f"/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
                "status_code": response.status_code,
                "success": response.status_code in [200, 302, 307],
                "org_id": org_id,
                "auth_id": auth_id
            }
            
            if response.status_code in [302, 307]:
                result["redirect_location"] = response.headers.get("location")
                result["auth_flow"] = "OAuth redirect"
            elif response.status_code == 200:
                try:
                    data = response.json()
                    result["data"] = data
                    result["auth_flow"] = "Direct success" if data.get("status") == "success" else "Unknown"
                except:
                    result["response_text"] = response.text[:500]
            else:
                result["error"] = response.text[:500]
            
            return result
        except Exception as e:
            return {
                "test": "Claude.ai Authentication Endpoint",
                "endpoint": f"/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
                "success": False,
                "error": str(e)
            }
    
    async def test_oauth_flow(self) -> Dict[str, Any]:
        """Test full OAuth2 authorization flow"""
        print("\n🔄 Testing OAuth2 Flow...")
        
        # Step 1: Register client
        client_data = {
            "client_name": "Claude.ai Test Client",
            "redirect_uris": ["https://claude.ai/api/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read"
        }
        
        try:
            # Register client
            response = await self.client.post(
                f"{self.base_url}/oauth/register",
                json=client_data
            )
            
            if response.status_code != 201:
                return {
                    "test": "OAuth2 Flow",
                    "success": False,
                    "error": f"Client registration failed: {response.status_code}",
                    "details": response.text[:500]
                }
            
            client_info = response.json()
            client_id = client_info.get("client_id")
            
            # Step 2: Authorization request
            auth_params = {
                "client_id": client_id,
                "redirect_uri": "https://claude.ai/api/callback",
                "response_type": "code",
                "state": str(uuid.uuid4()),
                "scope": "read"
            }
            
            auth_url = f"{self.base_url}/oauth/authorize?" + urllib.parse.urlencode(auth_params)
            
            response = await self.client.get(auth_url, follow_redirects=False)
            
            result = {
                "test": "OAuth2 Flow",
                "success": True,
                "client_id": client_id,
                "registration_status": 201,
                "authorization_status": response.status_code,
                "authorization_headers": dict(response.headers)
            }
            
            if response.status_code in [302, 307]:
                result["redirect_location"] = response.headers.get("location")
                # Try to extract code from redirect
                if result["redirect_location"]:
                    parsed = urllib.parse.urlparse(result["redirect_location"])
                    query = urllib.parse.parse_qs(parsed.query)
                    result["authorization_code"] = query.get("code", [None])[0]
                    result["state_match"] = query.get("state", [None])[0] == auth_params["state"]
            
            return result
            
        except Exception as e:
            return {
                "test": "OAuth2 Flow",
                "success": False,
                "error": str(e)
            }
    
    async def test_sse_endpoint(self) -> Dict[str, Any]:
        """Test SSE (Server-Sent Events) endpoint"""
        print("\n📡 Testing SSE Endpoint...")
        
        try:
            # Quick test - just check if endpoint exists
            response = await self.client.get(
                f"{self.base_url}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=5.0
            )
            
            result = {
                "test": "SSE Endpoint",
                "endpoint": "/sse",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "content_type": response.headers.get("content-type")
            }
            
            if response.status_code == 200:
                # Read first few bytes to verify SSE format
                content = response.text[:200]
                result["starts_with_event"] = content.startswith("event:") or content.startswith("data:")
                result["sample"] = content
            else:
                result["error"] = response.text[:500]
            
            return result
        except Exception as e:
            return {
                "test": "SSE Endpoint",
                "endpoint": "/sse",
                "success": False,
                "error": str(e)
            }
    
    async def test_mcp_tools(self) -> Dict[str, Any]:
        """Test MCP tools listing via messages endpoint"""
        print("\n🛠️ Testing MCP Tools...")
        
        try:
            # Initialize session
            init_msg = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": False}
                    },
                    "clientInfo": {
                        "name": "Claude.ai Auth Test",
                        "version": "1.0.0"
                    }
                },
                "id": str(uuid.uuid4())
            }
            
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=init_msg
            )
            
            if response.status_code != 200:
                return {
                    "test": "MCP Tools",
                    "success": False,
                    "error": f"Initialize failed: {response.status_code}",
                    "details": response.text[:500]
                }
            
            # List tools
            list_msg = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": str(uuid.uuid4())
            }
            
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=list_msg
            )
            
            result = {
                "test": "MCP Tools",
                "endpoint": "/messages",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                result["tool_count"] = len(tools)
                result["tool_names"] = [t.get("name") for t in tools[:5]]  # First 5 tools
                result["has_auth_tools"] = any("auth" in t.get("name", "").lower() for t in tools)
            else:
                result["error"] = response.text[:500]
            
            return result
        except Exception as e:
            return {
                "test": "MCP Tools",
                "endpoint": "/messages",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """Run all authentication tests"""
        print(f"\n🚀 Claude.ai Authentication Test Suite")
        print(f"📍 Target: {self.base_url}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run tests
        tests = [
            self.test_mcp_discovery(),
            self.test_oauth_discovery(),
            self.test_claude_ai_endpoint(),
            self.test_oauth_flow(),
            self.test_sse_endpoint(),
            self.test_mcp_tools()
        ]
        
        results = await asyncio.gather(*tests)
        
        for result in results:
            self.results["tests"].append(result)
        
        # Summary
        total = len(results)
        passed = sum(1 for r in results if r.get("success"))
        
        print("\n" + "=" * 60)
        print(f"📊 Test Summary")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for test in self.results["tests"]:
            status = "✅" if test.get("success") else "❌"
            print(f"\n{status} {test.get('test', 'Unknown Test')}")
            if test.get("endpoint"):
                print(f"   Endpoint: {test.get('endpoint')}")
            if test.get("status_code"):
                print(f"   Status: {test.get('status_code')}")
            if not test.get("success") and test.get("error"):
                print(f"   Error: {test.get('error')}")
            if test.get("auth_flow"):
                print(f"   Auth Flow: {test.get('auth_flow')}")
        
        # Save results
        with open("claude_ai_auth_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to claude_ai_auth_test_results.json")
        
        await self.client.aclose()
        return self.results

async def main():
    # Test production by default
    url = "https://strunz.up.railway.app"
    
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    tester = ClaudeAIAuthTester(url)
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())