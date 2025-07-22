#!/usr/bin/env python3
"""
Final Comprehensive Production Test Report for v0.7.8
Focused on actual capabilities and past issues
"""

import asyncio
import json
import httpx
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

class ProductionTestReport:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=False)
        self.report = {
            "title": "Production Test Report v0.7.8",
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "sections": {}
        }
    
    async def test_version_and_health(self) -> Dict[str, Any]:
        """Test version display and health endpoints"""
        print("\n1️⃣ Testing Version & Health Endpoints...")
        
        results = {}
        
        # Test main health endpoint
        response = await self.client.get(f"{self.base_url}/")
        if response.status_code == 200:
            data = response.json()
            results["main_health"] = {
                "status": "✅ PASS",
                "version": data.get("version"),
                "server": data.get("server"),
                "uptime": data.get("uptime_seconds", 0),
                "tools_count": data.get("tools_available", 0),
                "correct_version": data.get("version") == "0.7.8"
            }
        else:
            results["main_health"] = {"status": "❌ FAIL", "status_code": response.status_code}
        
        # Test other health endpoints
        for endpoint in ["/health", "/railway-health"]:
            try:
                resp = await self.client.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                    "status_code": resp.status_code
                }
            except Exception as e:
                results[endpoint] = {"status": "❌ FAIL", "error": str(e)}
        
        return results
    
    async def test_claude_ai_endpoint(self) -> Dict[str, Any]:
        """Test Claude.ai specific endpoint"""
        print("\n2️⃣ Testing Claude.ai Authentication Endpoint...")
        
        org_id = "test-org-123"
        auth_id = "test-auth-456"
        
        response = await self.client.get(
            f"{self.base_url}/api/organizations/{org_id}/mcp/start-auth/{auth_id}"
        )
        
        result = {
            "endpoint": f"/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
            "status_code": response.status_code,
            "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        }
        
        if response.status_code == 200:
            data = response.json()
            result["response"] = {
                "status": data.get("status"),
                "server_url": data.get("server_url"),
                "auth_not_required": data.get("auth_not_required"),
                "message": data.get("message")
            }
            result["correct_response"] = (
                data.get("status") == "success" and 
                data.get("auth_not_required") == True
            )
        
        return result
    
    async def test_mcp_capabilities(self) -> Dict[str, Any]:
        """Test MCP protocol capabilities"""
        print("\n3️⃣ Testing MCP Protocol Capabilities...")
        
        results = {}
        
        # Test discovery
        response = await self.client.get(f"{self.base_url}/.well-known/mcp/resource")
        if response.status_code == 200:
            data = response.json()
            results["discovery"] = {
                "status": "✅ PASS",
                "mcp_version": data.get("mcpVersion"),
                "server_info": data.get("serverInfo"),
                "capabilities": data.get("capabilities"),
                "transport": data.get("transport"),
                "authentication": data.get("authentication", {}).get("type")
            }
        
        # Test initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {}
            },
            "id": "1"
        }
        response = await self.client.post(f"{self.base_url}/messages", json=init_request)
        results["initialize"] = {
            "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
            "response": response.json() if response.status_code == 200 else None
        }
        
        return results
    
    async def test_tools_functionality(self) -> Dict[str, Any]:
        """Test tools listing and execution"""
        print("\n4️⃣ Testing Tools Functionality...")
        
        results = {"tools": []}
        
        # List tools
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "1"
        }
        
        response = await self.client.post(f"{self.base_url}/messages", json=list_request)
        if response.status_code == 200:
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            results["total_tools"] = len(tools)
            results["status"] = "✅ PASS" if len(tools) > 0 else "⚠️ WARNING"
            
            # Test each tool
            for tool in tools:
                tool_name = tool.get("name")
                print(f"   Testing tool: {tool_name}")
                
                # Call tool
                call_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {}
                    },
                    "id": "1"
                }
                
                call_response = await self.client.post(f"{self.base_url}/messages", json=call_request)
                tool_result = {
                    "name": tool_name,
                    "description": tool.get("description"),
                    "execution_status": "✅ PASS" if call_response.status_code == 200 else "❌ FAIL"
                }
                
                if call_response.status_code == 200:
                    result_data = call_response.json()
                    if "result" in result_data and "content" in result_data["result"]:
                        content = result_data["result"]["content"]
                        if content and len(content) > 0:
                            tool_result["output_preview"] = content[0].get("text", "")[:100] + "..."
                
                results["tools"].append(tool_result)
        
        return results
    
    async def test_prompts_functionality(self) -> Dict[str, Any]:
        """Test prompts listing and execution"""
        print("\n5️⃣ Testing Prompts Functionality...")
        
        results = {"prompts": []}
        
        # List prompts
        list_request = {
            "jsonrpc": "2.0",
            "method": "prompts/list",
            "params": {},
            "id": "1"
        }
        
        response = await self.client.post(f"{self.base_url}/messages", json=list_request)
        if response.status_code == 200:
            data = response.json()
            prompts = data.get("result", {}).get("prompts", [])
            results["total_prompts"] = len(prompts)
            results["status"] = "✅ PASS" if len(prompts) > 0 else "⚠️ WARNING"
            
            # Test first prompt if available
            if prompts:
                prompt = prompts[0]
                prompt_name = prompt.get("name")
                print(f"   Testing prompt: {prompt_name}")
                
                get_request = {
                    "jsonrpc": "2.0",
                    "method": "prompts/get",
                    "params": {
                        "name": prompt_name,
                        "arguments": {"symptoms": "test", "history": "none"}
                    },
                    "id": "1"
                }
                
                get_response = await self.client.post(f"{self.base_url}/messages", json=get_request)
                results["prompts"].append({
                    "name": prompt_name,
                    "execution_status": "✅ PASS" if get_response.status_code == 200 else "❌ FAIL"
                })
        
        return results
    
    async def test_oauth2_flow(self) -> Dict[str, Any]:
        """Test OAuth2 implementation"""
        print("\n6️⃣ Testing OAuth2 Flow...")
        
        results = {}
        
        # Test client registration
        reg_data = {
            "client_name": "Test Client",
            "redirect_uris": ["https://example.com/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "read"
        }
        
        response = await self.client.post(f"{self.base_url}/oauth/register", json=reg_data)
        results["registration"] = {
            "status": "✅ PASS" if response.status_code in [200, 201] else "❌ FAIL",
            "status_code": response.status_code
        }
        
        if response.status_code in [200, 201]:
            client_data = response.json()
            client_id = client_data.get("client_id")
            
            # Test authorization
            auth_url = f"{self.base_url}/oauth/authorize?client_id={client_id}&redirect_uri=https://example.com/callback&response_type=code&state=test"
            auth_response = await self.client.get(auth_url)
            
            results["authorization"] = {
                "status": "✅ PASS" if auth_response.status_code in [200, 302, 307] else "❌ FAIL",
                "status_code": auth_response.status_code,
                "is_redirect": auth_response.status_code in [302, 307]
            }
        
        return results
    
    async def test_performance(self) -> Dict[str, Any]:
        """Test basic performance metrics"""
        print("\n7️⃣ Testing Performance Metrics...")
        
        endpoints = [
            ("/", "health"),
            ("/.well-known/mcp/resource", "discovery"),
            ("/api/organizations/test/mcp/start-auth/test", "claude_ai")
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            times = []
            for _ in range(3):
                start = time.time()
                try:
                    await self.client.get(f"{self.base_url}{endpoint}")
                    times.append((time.time() - start) * 1000)
                except:
                    pass
            
            if times:
                results[name] = {
                    "avg_ms": round(sum(times) / len(times), 2),
                    "status": "✅ PASS" if sum(times) / len(times) < 1000 else "⚠️ SLOW"
                }
        
        return results
    
    async def test_past_issues(self) -> Dict[str, Any]:
        """Test resolution of past issues"""
        print("\n8️⃣ Testing Past Issues Resolution...")
        
        results = {}
        
        # Issue 1: Version stuck on 0.7.2
        response = await self.client.get(f"{self.base_url}/")
        version = response.json().get("version") if response.status_code == 200 else None
        results["version_stuck_issue"] = {
            "status": "✅ RESOLVED" if version == "0.7.8" else "❌ NOT RESOLVED",
            "current_version": version,
            "expected": "0.7.8"
        }
        
        # Issue 2: Claude.ai endpoint 404
        claude_response = await self.client.get(
            f"{self.base_url}/api/organizations/test/mcp/start-auth/test"
        )
        results["claude_ai_404_issue"] = {
            "status": "✅ RESOLVED" if claude_response.status_code == 200 else "❌ NOT RESOLVED",
            "status_code": claude_response.status_code
        }
        
        # Issue 3: Limited tools (should be 19)
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "1"
        }
        tools_response = await self.client.post(f"{self.base_url}/messages", json=list_request)
        if tools_response.status_code == 200:
            tools_count = len(tools_response.json().get("result", {}).get("tools", []))
            results["limited_tools_issue"] = {
                "status": "⚠️ PARTIAL" if tools_count < 19 else "✅ RESOLVED",
                "current_tools": tools_count,
                "expected": 19
            }
        
        return results
    
    async def generate_final_report(self):
        """Generate the final comprehensive report"""
        print(f"\n🔬 COMPREHENSIVE PRODUCTION TEST REPORT")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Target: {self.base_url}")
        print("=" * 80)
        
        # Run all tests
        self.report["sections"]["version_health"] = await self.test_version_and_health()
        self.report["sections"]["claude_ai"] = await self.test_claude_ai_endpoint()
        self.report["sections"]["mcp_capabilities"] = await self.test_mcp_capabilities()
        self.report["sections"]["tools"] = await self.test_tools_functionality()
        self.report["sections"]["prompts"] = await self.test_prompts_functionality()
        self.report["sections"]["oauth2"] = await self.test_oauth2_flow()
        self.report["sections"]["performance"] = await self.test_performance()
        self.report["sections"]["past_issues"] = await self.test_past_issues()
        
        # Generate summary
        self.report["summary"] = self._generate_summary()
        
        # Save report
        with open("production_test_report_final.json", "w") as f:
            json.dump(self.report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 EXECUTIVE SUMMARY")
        print("=" * 80)
        
        summary = self.report["summary"]
        print(f"\n🎯 Production Status: {summary['production_status']}")
        print(f"📌 Version: {summary['version']}")
        print(f"🛠️ Tools Available: {summary['tools_count']}")
        print(f"📝 Prompts Available: {summary['prompts_count']}")
        print(f"🤖 Claude.ai Compatible: {summary['claude_ai_ready']}")
        print(f"⚡ Performance: {summary['performance_status']}")
        
        print("\n✅ PASSED TESTS:")
        for test in summary["passed_tests"]:
            print(f"   • {test}")
        
        if summary["failed_tests"]:
            print("\n❌ FAILED TESTS:")
            for test in summary["failed_tests"]:
                print(f"   • {test}")
        
        if summary["warnings"]:
            print("\n⚠️ WARNINGS:")
            for warning in summary["warnings"]:
                print(f"   • {warning}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary["recommendations"]:
            print(f"   • {rec}")
        
        print(f"\n🏁 OVERALL RESULT: {summary['overall_result']}")
        
        await self.client.aclose()
        return self.report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        passed_tests = []
        failed_tests = []
        warnings = []
        recommendations = []
        
        # Check version
        version = self.report["sections"]["version_health"].get("main_health", {}).get("version", "Unknown")
        if self.report["sections"]["version_health"].get("main_health", {}).get("correct_version"):
            passed_tests.append("Version display (0.7.8)")
        else:
            failed_tests.append(f"Version display (showing {version})")
        
        # Check Claude.ai
        if self.report["sections"]["claude_ai"].get("correct_response"):
            passed_tests.append("Claude.ai authentication endpoint")
        else:
            failed_tests.append("Claude.ai authentication endpoint")
        
        # Check tools
        tools_count = self.report["sections"]["tools"].get("total_tools", 0)
        if tools_count > 0:
            passed_tests.append(f"Tools functionality ({tools_count} tools)")
            if tools_count < 19:
                warnings.append(f"Only {tools_count} tools available instead of 19")
                recommendations.append("Deploy with full tool registry (all 19 tools)")
        else:
            failed_tests.append("Tools functionality")
        
        # Check prompts
        prompts_count = self.report["sections"]["prompts"].get("total_prompts", 0)
        if prompts_count > 0:
            passed_tests.append(f"Prompts functionality ({prompts_count} prompts)")
        else:
            warnings.append("No prompts available")
            recommendations.append("Enable prompt capabilities")
        
        # Check OAuth2
        if self.report["sections"]["oauth2"].get("registration", {}).get("status") == "✅ PASS":
            passed_tests.append("OAuth2 client registration")
        else:
            failed_tests.append("OAuth2 client registration")
        
        if not self.report["sections"]["oauth2"].get("authorization", {}).get("is_redirect"):
            warnings.append("OAuth2 authorization not returning proper redirect")
        
        # Check performance
        perf = self.report["sections"]["performance"]
        avg_response_times = [v.get("avg_ms", 0) for v in perf.values() if "avg_ms" in v]
        avg_response = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
        
        performance_status = "✅ GOOD" if avg_response < 500 else "⚠️ SLOW" if avg_response < 1000 else "❌ POOR"
        
        # Overall result
        critical_passes = (
            self.report["sections"]["version_health"].get("main_health", {}).get("correct_version", False) and
            self.report["sections"]["claude_ai"].get("correct_response", False) and
            tools_count > 0
        )
        
        overall_result = "✅ PRODUCTION READY" if critical_passes and not failed_tests else "⚠️ OPERATIONAL WITH ISSUES" if critical_passes else "❌ NOT READY"
        
        return {
            "production_status": "LIVE" if version else "DOWN",
            "version": version,
            "tools_count": tools_count,
            "prompts_count": prompts_count,
            "claude_ai_ready": "✅ YES" if self.report["sections"]["claude_ai"].get("correct_response") else "❌ NO",
            "performance_status": performance_status,
            "avg_response_time_ms": round(avg_response, 2),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warnings": warnings,
            "recommendations": recommendations,
            "overall_result": overall_result
        }

async def main():
    tester = ProductionTestReport()
    await tester.generate_final_report()

if __name__ == "__main__":
    asyncio.run(main())