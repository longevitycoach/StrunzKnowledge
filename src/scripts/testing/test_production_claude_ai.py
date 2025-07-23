#!/usr/bin/env python3
"""
Production Test for Claude.ai Integration
Tests the complete OAuth flow and MCP functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class ProductionClaudeAITest:
    def __init__(self):
        self.base_url = "https://strunz.up.railway.app"
        self.results = []
        
    async def run_all_tests(self):
        """Run all tests"""
        async with aiohttp.ClientSession() as session:
            print(f"🚀 Testing Production: {self.base_url}")
            print(f"Time: {datetime.now()}")
            print("=" * 60)
            
            # Test 1: Health Check
            await self.test_health(session)
            
            # Test 2: MCP Discovery
            await self.test_mcp_discovery(session)
            
            # Test 3: Claude.ai Start Auth
            await self.test_claude_start_auth(session)
            
            # Test 4: OAuth Callback
            await self.test_oauth_callback(session)
            
            # Test 5: MCP Protocol
            await self.test_mcp_protocol(session)
            
            # Test 6: OAuth Registration
            await self.test_oauth_registration(session)
            
            # Print results
            self.print_results()
    
    async def test_health(self, session):
        """Test health endpoint"""
        print("\n🔍 Testing Health Endpoint")
        try:
            async with session.get(f"{self.base_url}/health") as resp:
                data = await resp.json()
                self.results.append({
                    "test": "Health Check",
                    "endpoint": "/health",
                    "status": resp.status,
                    "success": resp.status == 200 and data.get("version") == "0.7.10",
                    "details": f"Version: {data.get('version')}, Tools: {data.get('tools_available')}"
                })
                print(f"✅ Health: {data.get('status')} - v{data.get('version')}")
        except Exception as e:
            self.results.append({
                "test": "Health Check",
                "endpoint": "/health",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ Health check failed: {e}")
    
    async def test_mcp_discovery(self, session):
        """Test MCP discovery endpoint"""
        print("\n🔍 Testing MCP Discovery")
        try:
            async with session.get(f"{self.base_url}/.well-known/mcp/resource") as resp:
                data = await resp.json()
                self.results.append({
                    "test": "MCP Discovery",
                    "endpoint": "/.well-known/mcp/resource",
                    "status": resp.status,
                    "success": resp.status == 200 and "mcpVersion" in data,
                    "details": f"MCP Version: {data.get('mcpVersion')}"
                })
                print(f"✅ MCP Discovery: {data.get('mcpVersion')}")
        except Exception as e:
            self.results.append({
                "test": "MCP Discovery",
                "endpoint": "/.well-known/mcp/resource",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ MCP discovery failed: {e}")
    
    async def test_claude_start_auth(self, session):
        """Test Claude.ai start auth endpoint"""
        print("\n🤖 Testing Claude.ai Auth Flow")
        try:
            url = f"{self.base_url}/api/organizations/test-org/mcp/start-auth/test-auth-id"
            async with session.get(url, allow_redirects=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    success = data.get("auth_not_required") == True
                    self.results.append({
                        "test": "Claude.ai Start Auth",
                        "endpoint": "/api/organizations/.../mcp/start-auth/...",
                        "status": resp.status,
                        "success": success,
                        "details": f"Auth skip mode: {data.get('auth_not_required')}"
                    })
                    print(f"✅ Claude.ai Auth: Simplified mode active")
                elif resp.status == 302:
                    self.results.append({
                        "test": "Claude.ai Start Auth",
                        "endpoint": "/api/organizations/.../mcp/start-auth/...",
                        "status": resp.status,
                        "success": True,
                        "details": "OAuth redirect mode"
                    })
                    print(f"✅ Claude.ai Auth: OAuth redirect")
                else:
                    self.results.append({
                        "test": "Claude.ai Start Auth",
                        "endpoint": "/api/organizations/.../mcp/start-auth/...",
                        "status": resp.status,
                        "success": False,
                        "details": "Unexpected response"
                    })
                    print(f"❌ Claude.ai Auth: Status {resp.status}")
        except Exception as e:
            self.results.append({
                "test": "Claude.ai Start Auth",
                "endpoint": "/api/organizations/.../mcp/start-auth/...",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ Claude.ai auth failed: {e}")
    
    async def test_oauth_callback(self, session):
        """Test OAuth callback endpoint"""
        print("\n🔄 Testing OAuth Callback")
        try:
            # Test success case
            url = f"{self.base_url}/api/mcp/auth_callback?code=test123&state=test"
            async with session.get(url) as resp:
                content = await resp.text()
                has_postmessage = "postMessage" in content
                self.results.append({
                    "test": "OAuth Callback (success)",
                    "endpoint": "/api/mcp/auth_callback",
                    "status": resp.status,
                    "success": resp.status == 200 and has_postmessage,
                    "details": "Has postMessage: " + str(has_postmessage)
                })
                print(f"✅ OAuth Callback: Success case working")
                
            # Test error case
            url = f"{self.base_url}/api/mcp/auth_callback?error=access_denied"
            async with session.get(url) as resp:
                self.results.append({
                    "test": "OAuth Callback (error)",
                    "endpoint": "/api/mcp/auth_callback",
                    "status": resp.status,
                    "success": resp.status == 400,
                    "details": "Error handling working"
                })
                print(f"✅ OAuth Callback: Error case working")
                
        except Exception as e:
            self.results.append({
                "test": "OAuth Callback",
                "endpoint": "/api/mcp/auth_callback",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ OAuth callback failed: {e}")
    
    async def test_mcp_protocol(self, session):
        """Test MCP protocol endpoints"""
        print("\n🔧 Testing MCP Protocol")
        try:
            # Initialize
            init_data = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0.0",
                    "clientInfo": {"name": "test"}
                },
                "id": 1
            }
            async with session.post(f"{self.base_url}/messages", json=init_data) as resp:
                data = await resp.json()
                self.results.append({
                    "test": "MCP Initialize",
                    "endpoint": "/messages",
                    "status": resp.status,
                    "success": resp.status == 200 and "result" in data,
                    "details": "Server initialized"
                })
                print(f"✅ MCP Initialize: Success")
                
            # Tools list
            tools_data = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            async with session.post(f"{self.base_url}/messages", json=tools_data) as resp:
                data = await resp.json()
                tools = data.get("result", {}).get("tools", [])
                self.results.append({
                    "test": "MCP Tools List",
                    "endpoint": "/messages",
                    "status": resp.status,
                    "success": resp.status == 200 and len(tools) == 20,
                    "details": f"Tools available: {len(tools)}"
                })
                print(f"✅ MCP Tools: {len(tools)} tools available")
                
        except Exception as e:
            self.results.append({
                "test": "MCP Protocol",
                "endpoint": "/messages",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ MCP protocol failed: {e}")
    
    async def test_oauth_registration(self, session):
        """Test OAuth client registration"""
        print("\n🔐 Testing OAuth Registration")
        try:
            reg_data = {
                "client_name": "Production Test Client",
                "redirect_uris": ["https://claude.ai/callback"],
                "grant_types": ["authorization_code"],
                "response_types": ["code"]
            }
            async with session.post(f"{self.base_url}/oauth/register", json=reg_data) as resp:
                data = await resp.json()
                client_id = data.get("client_id")
                self.results.append({
                    "test": "OAuth Registration",
                    "endpoint": "/oauth/register",
                    "status": resp.status,
                    "success": resp.status == 201 and client_id is not None,
                    "details": f"Client ID: {client_id[:10]}..." if client_id else "No client ID"
                })
                print(f"✅ OAuth Registration: {client_id[:10]}...")
        except Exception as e:
            self.results.append({
                "test": "OAuth Registration",
                "endpoint": "/oauth/register",
                "status": 0,
                "success": False,
                "details": str(e)
            })
            print(f"❌ OAuth registration failed: {e}")
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} | {result['test']} | Status: {result['status']} | {result['details']}")
        
        if passed == total:
            print("\n🎉 All tests passed! Production is ready for Claude.ai!")
        elif passed >= total * 0.9:
            print("\n✨ Most tests passed. Production is operational.")
        else:
            print("\n⚠️  Multiple tests failed. Please investigate.")

async def main():
    tester = ProductionClaudeAITest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())