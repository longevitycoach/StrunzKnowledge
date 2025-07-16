#!/usr/bin/env python3
"""
TEMPORARY TEST SCRIPT - DELETE AFTER USE
Purpose: OAuth endpoint testing for v0.5.0
Location: src/tests/test_oauth_endpoints.py

Comprehensive OAuth Endpoint Tests for MCP Server
Tests all OAuth 2.1 endpoints and workflows
"""

import asyncio
import json
import aiohttp
import urllib.parse
from typing import Dict, Optional
import time
import base64
import hashlib
import secrets


class OAuthEndpointTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.client_id = None
        self.client_secret = None
        self.auth_code = None
        self.access_token = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def test_oauth_discovery(self) -> Dict:
        """Test OAuth discovery endpoints"""
        print("\n🔍 Testing OAuth Discovery Endpoints...")
        results = {}
        
        # Test OAuth authorization server metadata
        endpoint = f"{self.base_url}/.well-known/oauth-authorization-server"
        try:
            async with self.session.get(endpoint) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ OAuth server metadata found at {endpoint}")
                    print(f"   - Issuer: {data.get('issuer', 'N/A')}")
                    print(f"   - Authorization endpoint: {data.get('authorization_endpoint', 'N/A')}")
                    print(f"   - Token endpoint: {data.get('token_endpoint', 'N/A')}")
                    results["oauth_server"] = {"status": "pass", "data": data}
                else:
                    print(f"❌ OAuth server metadata failed: HTTP {resp.status}")
                    results["oauth_server"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ OAuth server metadata error: {e}")
            results["oauth_server"] = {"status": "error", "error": str(e)}
        
        # Test OAuth protected resource metadata
        endpoint = f"{self.base_url}/.well-known/oauth-protected-resource"
        try:
            async with self.session.get(endpoint) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ OAuth resource metadata found at {endpoint}")
                    results["oauth_resource"] = {"status": "pass", "data": data}
                else:
                    print(f"❌ OAuth resource metadata failed: HTTP {resp.status}")
                    results["oauth_resource"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ OAuth resource metadata error: {e}")
            results["oauth_resource"] = {"status": "error", "error": str(e)}
        
        return results
    
    async def test_client_registration(self) -> Dict:
        """Test OAuth dynamic client registration"""
        print("\n🔍 Testing OAuth Client Registration...")
        
        registration_data = {
            "client_name": "Test MCP Client",
            "redirect_uris": ["http://localhost:3000/callback", "claude://claude.ai/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read",
            "token_endpoint_auth_method": "none"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/oauth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.client_id = data.get("client_id")
                    self.client_secret = data.get("client_secret")
                    print("✅ Client registration successful")
                    print(f"   - Client ID: {self.client_id}")
                    print(f"   - Client Secret: {'None (public client)' if not self.client_secret else 'Generated'}")
                    print(f"   - Auth Method: {data.get('token_endpoint_auth_method', 'N/A')}")
                    return {"status": "pass", "data": data}
                else:
                    text = await resp.text()
                    print(f"❌ Client registration failed: HTTP {resp.status}")
                    print(f"   Response: {text}")
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ Client registration error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_authorization_flow(self) -> Dict:
        """Test OAuth authorization flow"""
        print("\n🔍 Testing OAuth Authorization Flow...")
        
        if not self.client_id:
            print("❌ No client_id available, skipping authorization test")
            return {"status": "skip", "error": "No client_id"}
        
        # Generate PKCE challenge
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        # Build authorization URL
        auth_params = {
            "client_id": self.client_id,
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "scope": "read",
            "state": secrets.token_urlsafe(16),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        try:
            # Test GET authorization endpoint
            async with self.session.get(
                f"{self.base_url}/oauth/authorize",
                params=auth_params,
                allow_redirects=False
            ) as resp:
                if resp.status in [302, 303]:  # Redirect
                    location = resp.headers.get("Location", "")
                    if "code=" in location:
                        # Extract auth code
                        parsed = urllib.parse.urlparse(location)
                        query_params = urllib.parse.parse_qs(parsed.query)
                        self.auth_code = query_params.get("code", [None])[0]
                        print("✅ Authorization successful (auto-approved)")
                        print(f"   - Auth code: {self.auth_code[:10]}...")
                        return {"status": "pass", "auth_code": self.auth_code}
                    else:
                        print("❌ Authorization redirect missing code")
                        return {"status": "fail", "error": "No code in redirect"}
                elif resp.status == 200:
                    # Consent screen
                    print("✅ Authorization consent screen returned")
                    return {"status": "pass", "consent_required": True}
                else:
                    print(f"❌ Authorization failed: HTTP {resp.status}")
                    return {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ Authorization error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_token_exchange(self) -> Dict:
        """Test OAuth token exchange"""
        print("\n🔍 Testing OAuth Token Exchange...")
        
        if not self.auth_code:
            print("❌ No auth code available, skipping token test")
            return {"status": "skip", "error": "No auth code"}
        
        token_data = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "client_id": self.client_id,
            "redirect_uri": "http://localhost:3000/callback"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/oauth/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.access_token = data.get("access_token")
                    print("✅ Token exchange successful")
                    print(f"   - Access token: {self.access_token[:20]}...")
                    print(f"   - Token type: {data.get('token_type', 'N/A')}")
                    print(f"   - Expires in: {data.get('expires_in', 'N/A')} seconds")
                    return {"status": "pass", "data": data}
                else:
                    text = await resp.text()
                    print(f"❌ Token exchange failed: HTTP {resp.status}")
                    print(f"   Response: {text}")
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ Token exchange error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_protected_endpoints(self) -> Dict:
        """Test accessing protected endpoints with token"""
        print("\n🔍 Testing Protected Endpoints...")
        
        if not self.access_token:
            print("❌ No access token available, skipping protected endpoint test")
            return {"status": "skip", "error": "No access token"}
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        results = {}
        
        # Test SSE endpoint with auth
        try:
            async with self.session.get(
                f"{self.base_url}/sse",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    print("✅ SSE endpoint accessible with token")
                    results["sse"] = {"status": "pass"}
                else:
                    print(f"❌ SSE endpoint failed: HTTP {resp.status}")
                    results["sse"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")
            results["sse"] = {"status": "error", "error": str(e)}
        
        # Test userinfo endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/oauth/userinfo",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Userinfo endpoint accessible")
                    print(f"   - User: {data.get('name', 'N/A')}")
                    results["userinfo"] = {"status": "pass", "data": data}
                else:
                    print(f"❌ Userinfo endpoint failed: HTTP {resp.status}")
                    results["userinfo"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ Userinfo endpoint error: {e}")
            results["userinfo"] = {"status": "error", "error": str(e)}
        
        return results
    
    async def test_mcp_with_auth(self) -> Dict:
        """Test MCP endpoints with OAuth authentication"""
        print("\n🔍 Testing MCP with OAuth...")
        
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        # Test initialize with auth
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "OAuth Test Client", "version": "1.0.0"}
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/messages",
                json=init_request,
                headers={**headers, "Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ MCP initialize successful with auth")
                    return {"status": "pass", "data": data}
                elif resp.status == 401:
                    print("❌ MCP requires authentication")
                    return {"status": "auth_required", "error": "HTTP 401"}
                else:
                    print(f"❌ MCP initialize failed: HTTP {resp.status}")
                    return {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ MCP initialize error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict:
        """Run all OAuth tests"""
        print("🚀 Starting OAuth Endpoint Tests")
        print("=" * 60)
        
        await self.setup()
        
        results = {}
        
        # Run tests in sequence
        results["discovery"] = await self.test_oauth_discovery()
        results["registration"] = await self.test_client_registration()
        results["authorization"] = await self.test_authorization_flow()
        results["token"] = await self.test_token_exchange()
        results["protected"] = await self.test_protected_endpoints()
        results["mcp_auth"] = await self.test_mcp_with_auth()
        
        await self.cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 OAuth Test Results Summary")
        print("=" * 60)
        
        passed = 0
        failed = 0
        skipped = 0
        
        def count_results(result):
            nonlocal passed, failed, skipped
            if isinstance(result, dict):
                status = result.get("status", "")
                if status == "pass":
                    passed += 1
                elif status == "fail" or status == "error":
                    failed += 1
                elif status == "skip":
                    skipped += 1
                else:
                    # Handle nested results
                    for sub_result in result.values():
                        if isinstance(sub_result, dict):
                            count_results(sub_result)
        
        for test_name, result in results.items():
            count_results(result)
            status = result.get("status", "unknown")
            if status == "pass":
                print(f"✅ {test_name}: PASSED")
            elif status == "fail" or status == "error":
                print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
            elif status == "skip":
                print(f"⏭️  {test_name}: SKIPPED - {result.get('error', 'Unknown reason')}")
            else:
                # Handle nested results
                for sub_test, sub_result in result.items():
                    if isinstance(sub_result, dict) and "status" in sub_result:
                        if sub_result["status"] == "pass":
                            print(f"✅ {test_name}.{sub_test}: PASSED")
                        else:
                            print(f"❌ {test_name}.{sub_test}: FAILED")
        
        total = passed + failed
        print(f"\n📈 Total Tests: {total} (Skipped: {skipped})")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "0%")
        
        return {
            "results": results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": (passed/total)*100 if total > 0 else 0
            }
        }


async def main():
    """Main test function"""
    import sys
    
    # Check if URL provided
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🧪 Testing OAuth Endpoints at: {base_url}")
    print(f"📋 Testing OAuth 2.1 + MCP Integration")
    
    tester = OAuthEndpointTester(base_url)
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results["summary"]["failed"] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    asyncio.run(main())