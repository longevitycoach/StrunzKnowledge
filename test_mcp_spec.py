#!/usr/bin/env python3
"""
Test MCP Server against MCP Specification
Tests the claude_compatible_server.py implementation
"""

import asyncio
import json
import aiohttp
import time
from typing import Dict, List, Optional

class MCPSpecificationTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.session = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> Dict:
        """Test basic health check endpoint"""
        print("🔍 Testing Health Check...")
        try:
            async with self.session.get(f"{self.base_url}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check passed: {data.get('server', 'Unknown')}")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ Health check failed: {resp.status}")
                    return {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_oauth_discovery(self) -> Dict:
        """Test OAuth discovery endpoints"""
        print("🔍 Testing OAuth Discovery...")
        results = {}
        
        # Test OAuth authorization server metadata
        try:
            async with self.session.get(f"{self.base_url}/.well-known/oauth-authorization-server") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ OAuth authorization server metadata found")
                    results["oauth_server"] = {"status": "pass", "data": data}
                else:
                    print(f"❌ OAuth server metadata failed: {resp.status}")
                    results["oauth_server"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ OAuth server metadata error: {e}")
            results["oauth_server"] = {"status": "error", "error": str(e)}
        
        # Test OAuth protected resource metadata
        try:
            async with self.session.get(f"{self.base_url}/.well-known/oauth-protected-resource") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ OAuth protected resource metadata found")
                    results["oauth_resource"] = {"status": "pass", "data": data}
                else:
                    print(f"❌ OAuth resource metadata failed: {resp.status}")
                    results["oauth_resource"] = {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ OAuth resource metadata error: {e}")
            results["oauth_resource"] = {"status": "error", "error": str(e)}
        
        return results
    
    async def test_mcp_discovery(self) -> Dict:
        """Test MCP resource discovery"""
        print("🔍 Testing MCP Discovery...")
        try:
            async with self.session.get(f"{self.base_url}/.well-known/mcp/resource") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ MCP resource metadata found")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ MCP resource metadata failed: {resp.status}")
                    return {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ MCP resource metadata error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_oauth_client_registration(self) -> Dict:
        """Test OAuth dynamic client registration"""
        print("🔍 Testing OAuth Client Registration...")
        
        registration_data = {
            "client_name": "Test MCP Client",
            "redirect_uris": ["http://localhost:3000/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/oauth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ OAuth client registration successful")
                    return {"status": "pass", "data": data}
                else:
                    print(f"❌ OAuth client registration failed: {resp.status}")
                    text = await resp.text()
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ OAuth client registration error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_sse_endpoint(self) -> Dict:
        """Test SSE endpoint connectivity"""
        print("🔍 Testing SSE Endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/sse") as resp:
                if resp.status == 200:
                    print("✅ SSE endpoint accessible")
                    return {"status": "pass", "message": "SSE endpoint responds"}
                else:
                    print(f"❌ SSE endpoint failed: {resp.status}")
                    return {"status": "fail", "error": f"HTTP {resp.status}"}
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_mcp_initialize(self) -> Dict:
        """Test MCP initialization protocol"""
        print("🔍 Testing MCP Initialize...")
        
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "Test MCP Client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/messages",
                json=initialize_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data:
                        print("✅ MCP initialize successful")
                        return {"status": "pass", "data": data}
                    else:
                        print(f"❌ MCP initialize failed: {data}")
                        return {"status": "fail", "error": data}
                else:
                    print(f"❌ MCP initialize failed: {resp.status}")
                    text = await resp.text()
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ MCP initialize error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_tools_list(self) -> Dict:
        """Test tools/list request"""
        print("🔍 Testing Tools List...")
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/messages",
                json=tools_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data and "tools" in data["result"]:
                        tools_count = len(data["result"]["tools"])
                        print(f"✅ Tools list successful: {tools_count} tools found")
                        return {"status": "pass", "data": data, "tools_count": tools_count}
                    else:
                        print(f"❌ Tools list failed: {data}")
                        return {"status": "fail", "error": data}
                else:
                    print(f"❌ Tools list failed: {resp.status}")
                    text = await resp.text()
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ Tools list error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_tool_call(self) -> Dict:
        """Test a simple tool call"""
        print("🔍 Testing Tool Call...")
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/messages",
                json=tool_request,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "result" in data:
                        print("✅ Tool call successful")
                        return {"status": "pass", "data": data}
                    else:
                        print(f"❌ Tool call failed: {data}")
                        return {"status": "fail", "error": data}
                else:
                    print(f"❌ Tool call failed: {resp.status}")
                    text = await resp.text()
                    return {"status": "fail", "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict:
        """Run all MCP specification tests"""
        print("🚀 Starting MCP Specification Tests")
        print("=" * 50)
        
        await self.setup()
        
        results = {}
        
        # Run tests in order
        results["health_check"] = await self.test_health_check()
        results["oauth_discovery"] = await self.test_oauth_discovery()
        results["mcp_discovery"] = await self.test_mcp_discovery()
        results["oauth_registration"] = await self.test_oauth_client_registration()
        results["sse_endpoint"] = await self.test_sse_endpoint()
        results["mcp_initialize"] = await self.test_mcp_initialize()
        results["tools_list"] = await self.test_tools_list()
        results["tool_call"] = await self.test_tool_call()
        
        await self.cleanup()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, result in results.items():
            if isinstance(result, dict) and "status" in result:
                status = result["status"]
                if status == "pass":
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                elif status == "fail":
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                    failed += 1
                else:
                    print(f"🔴 {test_name}: ERROR - {result.get('error', 'Unknown error')}")
                    errors += 1
            else:
                # Handle nested results (like oauth_discovery)
                for sub_test, sub_result in result.items():
                    if isinstance(sub_result, dict) and "status" in sub_result:
                        status = sub_result["status"]
                        if status == "pass":
                            print(f"✅ {test_name}.{sub_test}: PASSED")
                            passed += 1
                        elif status == "fail":
                            print(f"❌ {test_name}.{sub_test}: FAILED - {sub_result.get('error', 'Unknown error')}")
                            failed += 1
                        else:
                            print(f"🔴 {test_name}.{sub_test}: ERROR - {sub_result.get('error', 'Unknown error')}")
                            errors += 1
        
        total = passed + failed + errors
        print(f"\n📈 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔴 Errors: {errors}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "0%")
        
        return {
            "results": results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
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
    
    print(f"🧪 Testing MCP Server at: {base_url}")
    print(f"📋 Testing against MCP Specification 2025-03-26")
    
    tester = MCPSpecificationTest(base_url)
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results["summary"]["failed"] == 0 and results["summary"]["errors"] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    asyncio.run(main())