#!/usr/bin/env python3
"""
Test MCP authentication flow with official client patterns
Tests both local and production servers
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Optional
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPAuthFlowTester:
    """Test MCP authentication flow"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.client = None
        self.test_results = []
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_health_check(self) -> bool:
        """Test basic health check"""
        try:
            response = await self.client.get(f"{self.server_url}/")
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                self.log_result("Health Check", True, f"Server v{version} is healthy")
                return True
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    async def test_mcp_discovery(self) -> Optional[Dict]:
        """Test MCP resource discovery"""
        try:
            response = await self.client.get(f"{self.server_url}/.well-known/mcp/resource")
            if response.status_code == 200:
                data = response.json()
                self.log_result("MCP Discovery", True, 
                    f"Version: {data.get('mcpVersion')}, Transport: {data.get('transport')}")
                return data
            else:
                self.log_result("MCP Discovery", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("MCP Discovery", False, str(e))
            return None
    
    async def test_oauth_discovery(self) -> Optional[Dict]:
        """Test OAuth discovery"""
        try:
            response = await self.client.get(f"{self.server_url}/.well-known/oauth-authorization-server")
            if response.status_code == 200:
                data = response.json()
                self.log_result("OAuth Discovery", True, 
                    f"Issuer: {data.get('issuer')}")
                return data
            else:
                self.log_result("OAuth Discovery", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("OAuth Discovery", False, str(e))
            return None
    
    async def test_client_registration(self) -> Optional[Dict]:
        """Test OAuth client registration"""
        try:
            register_data = {
                "client_name": "MCP Test Client",
                "redirect_uris": ["http://localhost:3000/callback", "https://claude.ai/api/callback"],
                "grant_types": ["authorization_code"],
                "response_types": ["code"]
            }
            
            response = await self.client.post(
                f"{self.server_url}/oauth/register",
                json=register_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Client Registration", True, 
                    f"Client ID: {data.get('client_id')}")
                return data
            else:
                self.log_result("Client Registration", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("Client Registration", False, str(e))
            return None
    
    async def test_claude_ai_endpoint(self) -> bool:
        """Test Claude.ai specific endpoint"""
        try:
            # Test the Claude.ai specific auth endpoint
            org_id = "test-org-id"
            auth_id = "test-auth-id"
            url = f"{self.server_url}/api/organizations/{org_id}/mcp/start-auth/{auth_id}?redirect_url=https://claude.ai/callback"
            
            response = await self.client.get(url, follow_redirects=False)
            
            if response.status_code in [200, 302, 307]:
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Claude.ai Endpoint", True, 
                        f"Response: {data.get('status', 'unknown')}")
                else:
                    location = response.headers.get('location', 'none')
                    self.log_result("Claude.ai Endpoint", True, 
                        f"Redirect to: {location[:50]}...")
                return True
            else:
                self.log_result("Claude.ai Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Claude.ai Endpoint", False, str(e))
            return False
    
    async def test_mcp_protocol(self) -> bool:
        """Test MCP protocol methods"""
        # Test initialize
        try:
            request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "MCP Test Client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            response = await self.client.post(
                f"{self.server_url}/messages",
                json=request
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    server_info = data["result"].get("serverInfo", {})
                    self.log_result("MCP Initialize", True, 
                        f"Server: {server_info.get('name')}, v{server_info.get('version')}")
                    
                    # Test tools/list
                    await self._test_tools_list()
                    
                    # Test tool execution
                    await self._test_tool_execution()
                    
                    return True
                else:
                    self.log_result("MCP Initialize", False, "No result in response")
                    return False
            else:
                self.log_result("MCP Initialize", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("MCP Initialize", False, str(e))
            return False
    
    async def _test_tools_list(self):
        """Test tools/list method"""
        try:
            request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            response = await self.client.post(
                f"{self.server_url}/messages",
                json=request
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    tools = data["result"].get("tools", [])
                    self.log_result("Tools List", True, f"Found {len(tools)} tools")
                else:
                    self.log_result("Tools List", False, "No result")
            else:
                self.log_result("Tools List", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Tools List", False, str(e))
    
    async def _test_tool_execution(self):
        """Test tool execution"""
        try:
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_mcp_server_purpose",
                    "arguments": {}
                },
                "id": 3
            }
            
            response = await self.client.post(
                f"{self.server_url}/messages",
                json=request
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    self.log_result("Tool Execution", True, "Tool executed successfully")
                else:
                    self.log_result("Tool Execution", False, "No result")
            else:
                self.log_result("Tool Execution", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Tool Execution", False, str(e))
    
    async def run_all_tests(self):
        """Run all authentication flow tests"""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"MCP Authentication Flow Test")
        logger.info(f"Server: {self.server_url}")
        logger.info(f"{'=' * 60}\n")
        
        # Run tests
        await self.test_health_check()
        await self.test_mcp_discovery()
        await self.test_oauth_discovery()
        await self.test_client_registration()
        await self.test_claude_ai_endpoint()
        await self.test_mcp_protocol()
        
        # Summary
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Test Summary: {passed}/{total} passed ({passed/total*100:.1f}%)")
        logger.info(f"{'=' * 60}")
        
        return passed == total


async def main():
    """Main test runner"""
    # Test production first (since local Docker is slow to start)
    logger.info("Testing Production Server...")
    async with MCPAuthFlowTester("https://strunz.up.railway.app") as tester:
        prod_success = await tester.run_all_tests()
    
    # Test local if available
    logger.info("\n\nTesting Local Server...")
    try:
        async with MCPAuthFlowTester("http://localhost:8000") as tester:
            # Quick check if local server is running
            try:
                await tester.client.get("http://localhost:8000/", timeout=2.0)
                local_success = await tester.run_all_tests()
            except:
                logger.info("Local server not available")
                local_success = False
    except:
        local_success = False
    
    # Overall result
    if prod_success:
        logger.info("\n✅ Production server authentication flow is working!")
        sys.exit(0)
    else:
        logger.error("\n❌ Authentication flow tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())