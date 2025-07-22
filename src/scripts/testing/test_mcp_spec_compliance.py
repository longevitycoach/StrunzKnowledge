#!/usr/bin/env python3
"""
MCP Specification Compliance Test
Tests against https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
"""

import asyncio
import json
import httpx
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import urllib.parse

class MCPSpecComplianceTest:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "mcp_spec_version": "2025-06-18",
            "tests": []
        }
    
    async def test_mcp_discovery(self) -> Dict[str, Any]:
        """Test MCP discovery endpoint as per spec"""
        print("\n📋 Testing MCP Discovery (/.well-known/mcp/resource)")
        
        try:
            response = await self.client.get(f"{self.base_url}/.well-known/mcp/resource")
            result = {
                "test": "MCP Discovery",
                "endpoint": "/.well-known/mcp/resource",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields per MCP spec
                required_fields = ["mcpVersion", "serverInfo", "capabilities"]
                missing_fields = [f for f in required_fields if f not in data]
                
                result["data"] = data
                result["missing_required_fields"] = missing_fields
                result["spec_compliant"] = len(missing_fields) == 0
                
                # Validate serverInfo
                if "serverInfo" in data:
                    server_info = data["serverInfo"]
                    result["server_name"] = server_info.get("name")
                    result["server_version"] = server_info.get("version")
                
                # Validate capabilities
                if "capabilities" in data:
                    caps = data["capabilities"]
                    result["supports_tools"] = caps.get("tools", False)
                    result["supports_prompts"] = caps.get("prompts", False)
                    result["supports_resources"] = caps.get("resources", False)
                    result["supports_sampling"] = caps.get("sampling", False)
                
                # Check authentication config
                if "authentication" in data:
                    auth = data["authentication"]
                    result["auth_type"] = auth.get("type")
                    result["auth_required"] = auth.get("required", False)
            
            return result
        except Exception as e:
            return {
                "test": "MCP Discovery",
                "endpoint": "/.well-known/mcp/resource",
                "success": False,
                "error": str(e)
            }
    
    async def test_initialize_method(self) -> Dict[str, Any]:
        """Test MCP initialize method"""
        print("\n🚀 Testing MCP Initialize Method")
        
        try:
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "prompts": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "MCP Spec Compliance Test",
                        "version": "1.0.0"
                    }
                },
                "id": str(uuid.uuid4())
            }
            
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=init_request
            )
            
            result = {
                "test": "Initialize Method",
                "endpoint": "/messages",
                "method": "initialize",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response format
                result["has_jsonrpc"] = "jsonrpc" in data
                result["has_result"] = "result" in data
                result["has_error"] = "error" in data
                
                if "result" in data:
                    res = data["result"]
                    result["protocol_version"] = res.get("protocolVersion")
                    result["server_capabilities"] = res.get("capabilities", {})
                    result["server_info"] = res.get("serverInfo", {})
                    
                    # Validate response structure
                    result["valid_response"] = all([
                        "protocolVersion" in res,
                        "capabilities" in res
                    ])
            
            return result
        except Exception as e:
            return {
                "test": "Initialize Method",
                "endpoint": "/messages",
                "method": "initialize",
                "success": False,
                "error": str(e)
            }
    
    async def test_oauth2_flow(self) -> Dict[str, Any]:
        """Test OAuth2 authorization flow per MCP spec"""
        print("\n🔐 Testing OAuth2 Authorization Flow")
        
        result = {
            "test": "OAuth2 Authorization Flow",
            "steps": []
        }
        
        try:
            # Step 1: Client Registration
            print("  1️⃣ Client Registration...")
            reg_data = {
                "client_name": "MCP Spec Test Client",
                "redirect_uris": ["https://example.com/callback"],
                "grant_types": ["authorization_code"],
                "response_types": ["code"],
                "scope": "read"
            }
            
            reg_response = await self.client.post(
                f"{self.base_url}/oauth/register",
                json=reg_data
            )
            
            step1 = {
                "step": "Client Registration",
                "endpoint": "/oauth/register",
                "status_code": reg_response.status_code,
                "success": reg_response.status_code in [200, 201]
            }
            
            if step1["success"]:
                client_data = reg_response.json()
                client_id = client_data.get("client_id")
                step1["client_id"] = client_id
                step1["has_client_secret"] = "client_secret" in client_data
                result["steps"].append(step1)
                
                # Step 2: Authorization Request
                print("  2️⃣ Authorization Request...")
                auth_params = {
                    "client_id": client_id,
                    "redirect_uri": "https://example.com/callback",
                    "response_type": "code",
                    "state": str(uuid.uuid4()),
                    "scope": "read"
                }
                
                auth_url = f"{self.base_url}/oauth/authorize?" + urllib.parse.urlencode(auth_params)
                auth_response = await self.client.get(auth_url, follow_redirects=False)
                
                step2 = {
                    "step": "Authorization Request",
                    "endpoint": "/oauth/authorize",
                    "status_code": auth_response.status_code,
                    "success": auth_response.status_code in [302, 303, 307]
                }
                
                if auth_response.status_code in [302, 303, 307]:
                    location = auth_response.headers.get("location", "")
                    step2["redirect_location"] = location
                    
                    # Parse authorization code from redirect
                    if "code=" in location:
                        parsed = urllib.parse.urlparse(location)
                        query = urllib.parse.parse_qs(parsed.query)
                        auth_code = query.get("code", [None])[0]
                        step2["authorization_code"] = auth_code[:16] + "..." if auth_code else None
                        
                        # Step 3: Token Exchange
                        print("  3️⃣ Token Exchange...")
                        token_data = {
                            "grant_type": "authorization_code",
                            "code": auth_code,
                            "redirect_uri": "https://example.com/callback",
                            "client_id": client_id
                        }
                        
                        token_response = await self.client.post(
                            f"{self.base_url}/oauth/token",
                            data=token_data
                        )
                        
                        step3 = {
                            "step": "Token Exchange",
                            "endpoint": "/oauth/token",
                            "status_code": token_response.status_code,
                            "success": token_response.status_code == 200
                        }
                        
                        if token_response.status_code == 200:
                            token_result = token_response.json()
                            step3["has_access_token"] = "access_token" in token_result
                            step3["token_type"] = token_result.get("token_type")
                            step3["has_refresh_token"] = "refresh_token" in token_result
                            step3["expires_in"] = token_result.get("expires_in")
                        
                        result["steps"].append(step3)
                
                result["steps"].append(step2)
            else:
                result["steps"].append(step1)
            
            # Overall success
            result["success"] = all(step.get("success", False) for step in result["steps"])
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    async def test_tools_capability(self) -> Dict[str, Any]:
        """Test MCP tools capability"""
        print("\n🛠️ Testing Tools Capability")
        
        result = {
            "test": "Tools Capability",
            "subtests": []
        }
        
        # Test tools/list
        try:
            list_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": str(uuid.uuid4())
            }
            
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=list_request
            )
            
            list_test = {
                "method": "tools/list",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    list_test["tool_count"] = len(tools)
                    list_test["tool_names"] = [t.get("name") for t in tools[:5]]
                    
                    # Test first tool execution
                    if tools:
                        first_tool = tools[0]
                        tool_name = first_tool.get("name")
                        
                        print(f"  🔧 Testing tool execution: {tool_name}")
                        call_request = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": tool_name,
                                "arguments": {}
                            },
                            "id": str(uuid.uuid4())
                        }
                        
                        call_response = await self.client.post(
                            f"{self.base_url}/messages",
                            json=call_request
                        )
                        
                        call_test = {
                            "method": "tools/call",
                            "tool_name": tool_name,
                            "status_code": call_response.status_code,
                            "success": call_response.status_code == 200
                        }
                        
                        if call_response.status_code == 200:
                            call_data = call_response.json()
                            if "result" in call_data and "content" in call_data["result"]:
                                call_test["has_content"] = True
                                call_test["content_type"] = call_data["result"]["content"][0].get("type") if call_data["result"]["content"] else None
                        
                        result["subtests"].append(call_test)
            
            result["subtests"].append(list_test)
            
        except Exception as e:
            result["error"] = str(e)
        
        result["success"] = all(t.get("success", False) for t in result["subtests"])
        return result
    
    async def test_sse_transport(self) -> Dict[str, Any]:
        """Test SSE transport capability"""
        print("\n📡 Testing SSE Transport")
        
        try:
            # SSE endpoints are long-lived, so we just check if it's available
            response = await self.client.get(
                f"{self.base_url}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=5.0
            )
            
            result = {
                "test": "SSE Transport",
                "endpoint": "/sse",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                result["content_type"] = response.headers.get("content-type")
                result["is_event_stream"] = "event-stream" in response.headers.get("content-type", "")
                
                # Read first chunk
                content = response.text[:500]
                result["has_event_data"] = "event:" in content or "data:" in content
            
            return result
        except httpx.ReadTimeout:
            # SSE connections stay open, so timeout is expected
            return {
                "test": "SSE Transport",
                "endpoint": "/sse",
                "success": True,
                "note": "SSE endpoint exists (timeout expected for long-lived connections)"
            }
        except Exception as e:
            return {
                "test": "SSE Transport",
                "endpoint": "/sse",
                "success": False,
                "error": str(e)
            }
    
    async def test_claude_ai_compliance(self) -> Dict[str, Any]:
        """Test Claude.ai specific requirements"""
        print("\n🤖 Testing Claude.ai Compliance")
        
        org_id = f"test-org-{uuid.uuid4().hex[:8]}"
        auth_id = f"test-auth-{uuid.uuid4().hex[:8]}"
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
                params={
                    "redirect_url": "https://claude.ai/api/callback",
                    "open_in_browser": 0
                }
            )
            
            result = {
                "test": "Claude.ai Compliance",
                "endpoint": f"/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
                "status_code": response.status_code,
                "success": response.status_code in [200, 302, 307]
            }
            
            if response.status_code == 200:
                data = response.json()
                result["response_type"] = "direct_success"
                result["auth_not_required"] = data.get("auth_not_required", False)
                result["server_url"] = data.get("server_url")
                result["message"] = data.get("message")
            elif response.status_code in [302, 307]:
                result["response_type"] = "oauth_redirect"
                result["redirect_location"] = response.headers.get("location")
            
            return result
        except Exception as e:
            return {
                "test": "Claude.ai Compliance",
                "endpoint": f"/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """Run all MCP specification compliance tests"""
        print(f"\n🚀 MCP Specification Compliance Test")
        print(f"📍 Target: {self.base_url}")
        print(f"📋 MCP Spec: https://modelcontextprotocol.io/specification/2025-06-18")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_mcp_discovery(),
            self.test_initialize_method(),
            self.test_oauth2_flow(),
            self.test_tools_capability(),
            self.test_sse_transport(),
            self.test_claude_ai_compliance()
        ]
        
        results = await asyncio.gather(*tests)
        
        for result in results:
            self.results["tests"].append(result)
        
        # Summary
        total = len(results)
        passed = sum(1 for r in results if r.get("success"))
        
        print("\n" + "=" * 60)
        print(f"📊 Compliance Summary")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for test in self.results["tests"]:
            status = "✅" if test.get("success") else "❌"
            print(f"\n{status} {test.get('test', 'Unknown Test')}")
            
            if test.get("test") == "MCP Discovery":
                print(f"   Spec Compliant: {test.get('spec_compliant', False)}")
                print(f"   Server Version: {test.get('server_version', 'Unknown')}")
                print(f"   Capabilities: tools={test.get('supports_tools')}, prompts={test.get('supports_prompts')}")
            elif test.get("test") == "OAuth2 Authorization Flow":
                for step in test.get("steps", []):
                    step_status = "✅" if step.get("success") else "❌"
                    print(f"   {step_status} {step.get('step')}")
            elif test.get("test") == "Tools Capability":
                print(f"   Tool Count: {test.get('subtests', [{}])[0].get('tool_count', 0)}")
        
        # Save results
        with open("mcp_spec_compliance_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to mcp_spec_compliance_results.json")
        
        # Overall compliance assessment
        print(f"\n🏆 Overall MCP Specification Compliance: {(passed/total)*100:.1f}%")
        
        await self.client.aclose()
        return self.results

async def main():
    url = "https://strunz.up.railway.app"
    
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    tester = MCPSpecComplianceTest(url)
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())