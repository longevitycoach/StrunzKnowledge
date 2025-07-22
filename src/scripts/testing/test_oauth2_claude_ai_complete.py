#!/usr/bin/env python3
"""
Complete OAuth2 and Claude.ai Integration Test Suite
Tests all OAuth endpoints, Claude.ai specific flows, and MCP integration
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp
from urllib.parse import urlparse, parse_qs
import sys

# Add project root to path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.scripts.startup.preload_vector_store import preload_vector_store

class CompleteOAuth2Tester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.session = None
        self.start_time = time.time()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def preload_data(self):
        """Check if server is already running instead of preloading"""
        print("📚 Checking server status...")
        try:
            async with self.session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    print("✅ Server is already running and ready")
                else:
                    print("⚠️ Server not ready, may need preload")
        except Exception as e:
            print(f"⚠️ Server check failed: {e}")
            
    async def test_discovery_endpoints(self):
        """Test all discovery endpoints"""
        print("\n🔍 Testing Discovery Endpoints")
        
        endpoints = [
            ("/.well-known/mcp/resource", "MCP Resource Discovery"),
            ("/.well-known/oauth-authorization-server", "OAuth Server Metadata"),
            ("/", "Health Check"),
            ("/health", "Detailed Health")
        ]
        
        for endpoint, name in endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as resp:
                    data = await resp.json() if resp.headers.get("content-type", "").startswith("application/json") else await resp.text()
                    self.results.append({
                        "category": "Discovery",
                        "test": name,
                        "endpoint": endpoint,
                        "method": "GET",
                        "status_code": resp.status,
                        "success": resp.status == 200,
                        "response": data if isinstance(data, dict) else {"text": str(data)[:200]},
                        "validations": self._validate_discovery(endpoint, data) if isinstance(data, dict) else {}
                    })
            except Exception as e:
                self.results.append({
                    "category": "Discovery",
                    "test": name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                })
                
    def _validate_discovery(self, endpoint: str, data: dict) -> dict:
        """Validate discovery endpoint responses"""
        validations = {}
        
        if endpoint == "/.well-known/mcp/resource":
            validations["has_mcp_version"] = "mcpVersion" in data
            validations["has_server_info"] = "serverInfo" in data
            validations["has_endpoints"] = "endpoints" in data
            validations["has_authentication"] = "authentication" in data
            validations["oauth_configured"] = data.get("authentication", {}).get("type") == "oauth2"
            
        elif endpoint == "/.well-known/oauth-authorization-server":
            validations["has_issuer"] = "issuer" in data
            validations["has_authorization_endpoint"] = "authorization_endpoint" in data
            validations["has_token_endpoint"] = "token_endpoint" in data
            validations["has_registration_endpoint"] = "registration_endpoint" in data
            validations["supports_dynamic_registration"] = bool(data.get("registration_endpoint"))
            
        return validations
        
    async def test_claude_ai_flow(self):
        """Test Claude.ai specific authentication flow"""
        print("\n🤖 Testing Claude.ai Specific Flow")
        
        # Test different scenarios
        scenarios = [
            {
                "name": "Basic Claude.ai Auth",
                "org_id": "test-org-123",
                "auth_id": "test-auth-456",
                "params": {}
            },
            {
                "name": "Claude.ai with Redirect URL",
                "org_id": "claude-org",
                "auth_id": "auth-789",
                "params": {"redirect_url": "https://claude.ai/callback", "open_in_browser": "1"}
            }
        ]
        
        for scenario in scenarios:
            endpoint = f"/api/organizations/{scenario['org_id']}/mcp/start-auth/{scenario['auth_id']}"
            
            try:
                async with self.session.get(
                    f"{self.base_url}{endpoint}",
                    params=scenario["params"],
                    allow_redirects=False
                ) as resp:
                    data = None
                    if resp.headers.get("content-type", "").startswith("application/json"):
                        data = await resp.json()
                        
                    self.results.append({
                        "category": "Claude.ai",
                        "test": scenario["name"],
                        "endpoint": endpoint,
                        "method": "GET",
                        "input": scenario["params"],
                        "status_code": resp.status,
                        "success": resp.status in [200, 302],
                        "response": data,
                        "headers": dict(resp.headers),
                        "validations": {
                            "is_success": resp.status == 200 and data and data.get("status") == "success",
                            "is_redirect": resp.status == 302,
                            "auth_not_required": data.get("auth_not_required") == True if data else False,
                            "has_server_url": "server_url" in data if data else False
                        }
                    })
            except Exception as e:
                self.results.append({
                    "category": "Claude.ai",
                    "test": scenario["name"],
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                })
                
    async def test_oauth_flow_complete(self):
        """Test complete OAuth flow from registration to token"""
        print("\n🔐 Testing Complete OAuth Flow")
        
        # 1. Register client
        client_data = {
            "client_name": "Test OAuth Client",
            "redirect_uris": ["http://localhost:3000/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read write"
        }
        
        client_id = None
        try:
            async with self.session.post(
                f"{self.base_url}/oauth/register",
                json=client_data
            ) as resp:
                data = await resp.json()
                client_id = data.get("client_id")
                
                self.results.append({
                    "category": "OAuth Flow",
                    "test": "Client Registration",
                    "endpoint": "/oauth/register",
                    "method": "POST",
                    "input": client_data,
                    "status_code": resp.status,
                    "success": resp.status == 201 and bool(client_id),
                    "response": data
                })
        except Exception as e:
            self.results.append({
                "category": "OAuth Flow",
                "test": "Client Registration",
                "error": str(e),
                "success": False
            })
            return
            
        # 2. Authorization request
        if client_id:
            auth_params = {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": client_data["redirect_uris"][0],
                "scope": "read",
                "state": "test-state-123"
            }
            
            try:
                async with self.session.get(
                    f"{self.base_url}/oauth/authorize",
                    params=auth_params,
                    allow_redirects=False
                ) as resp:
                    location = resp.headers.get("Location", "")
                    parsed = urlparse(location)
                    query_params = parse_qs(parsed.query)
                    auth_code = query_params.get("code", [None])[0]
                    
                    self.results.append({
                        "category": "OAuth Flow",
                        "test": "Authorization Request",
                        "endpoint": "/oauth/authorize",
                        "method": "GET",
                        "input": auth_params,
                        "status_code": resp.status,
                        "success": resp.status == 302 and bool(auth_code),
                        "redirect_location": location,
                        "auth_code": auth_code[:10] + "..." if auth_code else None
                    })
                    
                    # 3. Token exchange
                    if auth_code:
                        await self._test_token_exchange(client_id, auth_code, client_data["redirect_uris"][0])
                        
            except Exception as e:
                self.results.append({
                    "category": "OAuth Flow",
                    "test": "Authorization Request",
                    "error": str(e),
                    "success": False
                })
                
    async def _test_token_exchange(self, client_id: str, auth_code: str, redirect_uri: str):
        """Test token exchange"""
        token_data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": client_id,
            "redirect_uri": redirect_uri
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/oauth/token",
                data=token_data
            ) as resp:
                data = await resp.json() if resp.status == 200 else await resp.text()
                
                self.results.append({
                    "category": "OAuth Flow",
                    "test": "Token Exchange",
                    "endpoint": "/oauth/token",
                    "method": "POST",
                    "input": {**token_data, "code": token_data["code"][:10] + "..."},
                    "status_code": resp.status,
                    "success": resp.status == 200 and isinstance(data, dict) and "access_token" in data,
                    "response": data if isinstance(data, dict) else {"error": str(data)},
                    "validations": {
                        "has_access_token": "access_token" in data if isinstance(data, dict) else False,
                        "has_token_type": data.get("token_type") == "Bearer" if isinstance(data, dict) else False,
                        "has_expires_in": "expires_in" in data if isinstance(data, dict) else False
                    }
                })
        except Exception as e:
            self.results.append({
                "category": "OAuth Flow",
                "test": "Token Exchange",
                "error": str(e),
                "success": False
            })
            
    async def test_mcp_integration(self):
        """Test MCP protocol integration"""
        print("\n🔧 Testing MCP Integration")
        
        # Test different MCP methods
        methods = [
            ("initialize", {"protocolVersion": "2025-03-26"}),
            ("tools/list", {}),
            ("prompts/list", {})
        ]
        
        for method, params in methods:
            try:
                async with self.session.post(
                    f"{self.base_url}/messages",
                    json={
                        "jsonrpc": "2.0",
                        "method": method,
                        "params": params,
                        "id": 1
                    }
                ) as resp:
                    data = await resp.json()
                    
                    self.results.append({
                        "category": "MCP Protocol",
                        "test": f"MCP {method}",
                        "endpoint": "/messages",
                        "method": "POST",
                        "input": {"method": method, "params": params},
                        "status_code": resp.status,
                        "success": resp.status == 200 and "result" in data,
                        "response": data,
                        "validations": self._validate_mcp_response(method, data)
                    })
            except Exception as e:
                self.results.append({
                    "category": "MCP Protocol",
                    "test": f"MCP {method}",
                    "error": str(e),
                    "success": False
                })
                
    def _validate_mcp_response(self, method: str, data: dict) -> dict:
        """Validate MCP response"""
        validations = {}
        
        if "result" not in data:
            return {"has_result": False}
            
        result = data["result"]
        
        if method == "initialize":
            validations["has_protocol_version"] = "protocolVersion" in result
            validations["has_capabilities"] = "capabilities" in result
            validations["has_server_info"] = "serverInfo" in result
            
        elif method == "tools/list":
            validations["has_tools"] = "tools" in result
            validations["tools_count"] = len(result.get("tools", []))
            validations["all_tools_have_names"] = all(
                "name" in tool for tool in result.get("tools", [])
            )
            
        elif method == "prompts/list":
            validations["has_prompts"] = "prompts" in result
            validations["prompts_count"] = len(result.get("prompts", []))
            
        return validations
        
    async def test_post_handlers(self):
        """Test POST handlers added for Claude.ai"""
        print("\n📮 Testing POST Handlers")
        
        endpoints = [
            ("/", "Root POST handler"),
            ("/sse", "SSE POST handler")
        ]
        
        for endpoint, name in endpoints:
            try:
                async with self.session.post(f"{self.base_url}{endpoint}") as resp:
                    data = await resp.json() if resp.headers.get("content-type", "").startswith("application/json") else await resp.text()
                    
                    self.results.append({
                        "category": "POST Handlers",
                        "test": name,
                        "endpoint": endpoint,
                        "method": "POST",
                        "status_code": resp.status,
                        "success": resp.status == 200,
                        "response": data if isinstance(data, dict) else {"text": str(data)[:200]}
                    })
            except Exception as e:
                self.results.append({
                    "category": "POST Handlers",
                    "test": name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                })
                
    async def test_callback_endpoint(self):
        """Test OAuth callback endpoint"""
        print("\n🔄 Testing OAuth Callback")
        
        scenarios = [
            {
                "name": "Successful callback",
                "params": {"code": "test-auth-code-123", "state": "test-state"}
            },
            {
                "name": "Error callback",
                "params": {"error": "access_denied", "error_description": "User denied access"}
            }
        ]
        
        for scenario in scenarios:
            try:
                async with self.session.get(
                    f"{self.base_url}/api/mcp/auth_callback",
                    params=scenario["params"]
                ) as resp:
                    content = await resp.text()
                    
                    self.results.append({
                        "category": "OAuth Callback",
                        "test": scenario["name"],
                        "endpoint": "/api/mcp/auth_callback",
                        "method": "GET",
                        "input": scenario["params"],
                        "status_code": resp.status,
                        "success": resp.status in [200, 400],
                        "content_type": resp.headers.get("content-type", ""),
                        "has_html": "<html>" in content.lower(),
                        "has_postmessage": "postMessage" in content
                    })
            except Exception as e:
                self.results.append({
                    "category": "OAuth Callback",
                    "test": scenario["name"],
                    "error": str(e),
                    "success": False
                })
                
    def generate_report(self) -> Tuple[str, str]:
        """Generate comprehensive test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        elapsed_time = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get("success", False))
        by_category = {}
        
        for result in self.results:
            category = result.get("category", "Unknown")
            if category not in by_category:
                by_category[category] = {"total": 0, "passed": 0}
            by_category[category]["total"] += 1
            if result.get("success", False):
                by_category[category]["passed"] += 1
                
        # Generate markdown report
        report = f"""# OAuth2 and Claude.ai Complete Test Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Server**: {self.base_url}  
**Test Duration**: {elapsed_time:.2f} seconds  
**Version**: 0.7.10  

## Executive Summary

- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {(passed_tests/total_tests*100):.1f}%

## Test Results by Category

| Category | Tests | Passed | Failed | Success Rate |
|----------|-------|--------|--------|--------------|
"""
        
        for category, stats in sorted(by_category.items()):
            success_rate = (stats["passed"]/stats["total"]*100)
            report += f"| {category} | {stats['total']} | {stats['passed']} | {stats['total']-stats['passed']} | {success_rate:.1f}% |\n"
            
        # Add detailed results
        report += "\n## Detailed Test Results\n"
        
        current_category = None
        for result in self.results:
            if result.get("category") != current_category:
                current_category = result.get("category")
                report += f"\n### {current_category}\n\n"
                
            status = "✅" if result.get("success") else "❌"
            report += f"**{status} {result.get('test', 'Unknown Test')}**\n"
            
            if "endpoint" in result:
                method = result.get('method', 'GET')
                report += f"- Endpoint: `{method} {result['endpoint']}`\n"
            if "status_code" in result:
                report += f"- Status: {result['status_code']}\n"
            if "error" in result:
                report += f"- Error: {result['error']}\n"
            if "validations" in result and result["validations"]:
                report += "- Validations:\n"
                for key, value in result["validations"].items():
                    report += f"  - {key}: {'✅' if value else '❌'}\n"
            report += "\n"
            
        # Save files
        report_path = f"docs/test-reports/OAUTH2_CLAUDE_AI_COMPLETE_TEST_{timestamp}.md"
        data_path = f"docs/test-reports/oauth2_claude_ai_test_data_{timestamp}.json"
        
        with open(report_path, "w") as f:
            f.write(report)
            
        with open(data_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "server": self.base_url,
                "duration_seconds": elapsed_time,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": total_tests - passed_tests,
                    "success_rate": passed_tests/total_tests*100,
                    "by_category": by_category
                },
                "results": self.results
            }, f, indent=2)
            
        return report_path, data_path

async def main():
    """Run complete OAuth2 and Claude.ai tests"""
    print("🚀 Starting Complete OAuth2 and Claude.ai Integration Tests")
    print("=" * 80)
    
    # Test both local and production if available
    servers = [
        ("Local", "http://localhost:8000"),
        # ("Production", "https://strunz.up.railway.app")  # Uncomment for production testing
    ]
    
    for name, url in servers:
        print(f"\n📍 Testing {name} server: {url}")
        
        async with CompleteOAuth2Tester(url) as tester:
            # Preload data for local testing
            if "localhost" in url:
                await tester.preload_data()
                
            # Run all test suites
            await tester.test_discovery_endpoints()
            await tester.test_claude_ai_flow()
            await tester.test_oauth_flow_complete()
            await tester.test_mcp_integration()
            await tester.test_post_handlers()
            await tester.test_callback_endpoint()
            
            # Generate report
            report_path, data_path = tester.generate_report()
            
            # Print summary
            total = len(tester.results)
            passed = sum(1 for r in tester.results if r.get("success", False))
            
            print("\n" + "=" * 80)
            print(f"✅ Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
            print(f"📄 Report saved to: {report_path}")
            print(f"📊 Raw data saved to: {data_path}")

if __name__ == "__main__":
    asyncio.run(main())