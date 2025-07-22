#!/usr/bin/env python3
"""
Comprehensive Production Test Suite for v0.7.8
Tests all MCP capabilities, past issues, and full coverage
"""

import asyncio
import json
import httpx
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.parse

class ComprehensiveProductionTest:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=False)
        self.start_time = time.time()
        self.results = {
            "test_suite": "Comprehensive Production Test v0.7.8",
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "categories": {},
            "past_issues_resolved": {},
            "summary": {}
        }
    
    async def test_past_issues(self) -> Dict[str, Any]:
        """Test all past issues to ensure they're resolved"""
        print("\n🔍 Testing Past Issues Resolution...")
        
        past_issues = {}
        
        # Issue 1: Version stuck on 0.7.2
        print("  📌 Testing version display...")
        response = await self.client.get(f"{self.base_url}/")
        data = response.json() if response.status_code == 200 else {}
        past_issues["version_stuck_on_0.7.2"] = {
            "resolved": data.get("version") == "0.7.8",
            "current_version": data.get("version"),
            "expected": "0.7.8"
        }
        
        # Issue 2: Claude.ai endpoint returning 404
        print("  📌 Testing Claude.ai endpoint availability...")
        claude_response = await self.client.get(
            f"{self.base_url}/api/organizations/test/mcp/start-auth/test123"
        )
        past_issues["claude_ai_endpoint_404"] = {
            "resolved": claude_response.status_code == 200,
            "status_code": claude_response.status_code,
            "expected": 200
        }
        
        # Issue 3: Tool execution error
        print("  📌 Testing tool execution...")
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_mcp_server_purpose",
                "arguments": {}
            },
            "id": str(uuid.uuid4())
        }
        tool_response = await self.client.post(f"{self.base_url}/messages", json=tool_request)
        tool_result = tool_response.json() if tool_response.status_code == 200 else {}
        past_issues["tool_execution_error"] = {
            "resolved": "result" in tool_result and "content" in tool_result.get("result", {}),
            "has_result": "result" in tool_result,
            "has_content": "content" in tool_result.get("result", {})
        }
        
        # Issue 4: Missing health endpoints
        print("  📌 Testing health endpoints...")
        health_endpoints = ["/", "/health", "/railway-health"]
        health_results = {}
        for endpoint in health_endpoints:
            resp = await self.client.get(f"{self.base_url}{endpoint}")
            health_results[endpoint] = resp.status_code == 200
        past_issues["missing_health_endpoints"] = {
            "resolved": all(health_results.values()),
            "endpoints": health_results
        }
        
        return past_issues
    
    async def test_all_tools(self) -> Dict[str, Any]:
        """Test all available tools with input/output validation"""
        print("\n🛠️ Testing All Tools with Input/Output...")
        
        tools_results = {
            "total_tools": 0,
            "tools_tested": [],
            "tools_failed": []
        }
        
        # First, get list of all tools
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        response = await self.client.post(f"{self.base_url}/messages", json=list_request)
        if response.status_code != 200:
            return {"error": "Failed to list tools", "status_code": response.status_code}
        
        tools_data = response.json()
        tools = tools_data.get("result", {}).get("tools", [])
        tools_results["total_tools"] = len(tools)
        
        # Test each tool
        for tool in tools:
            tool_name = tool.get("name")
            print(f"    🔧 Testing tool: {tool_name}")
            
            # Define test inputs for each tool
            test_inputs = self._get_test_inputs_for_tool(tool_name)
            
            tool_test = {
                "name": tool_name,
                "description": tool.get("description"),
                "test_cases": []
            }
            
            for test_case in test_inputs:
                call_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test_case["input"]
                    },
                    "id": str(uuid.uuid4())
                }
                
                start = time.time()
                call_response = await self.client.post(f"{self.base_url}/messages", json=call_request)
                duration = time.time() - start
                
                test_result = {
                    "input": test_case["input"],
                    "expected_output_type": test_case.get("expected_type"),
                    "status_code": call_response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "success": call_response.status_code == 200
                }
                
                if call_response.status_code == 200:
                    result_data = call_response.json()
                    if "result" in result_data and "content" in result_data["result"]:
                        content = result_data["result"]["content"]
                        if content and len(content) > 0:
                            test_result["output_preview"] = content[0].get("text", "")[:200]
                            test_result["output_type"] = content[0].get("type")
                    elif "error" in result_data:
                        test_result["error"] = result_data["error"]
                        test_result["success"] = False
                
                tool_test["test_cases"].append(test_result)
            
            # Determine if tool passed all tests
            tool_passed = all(tc.get("success", False) for tc in tool_test["test_cases"])
            if tool_passed:
                tools_results["tools_tested"].append(tool_test)
            else:
                tools_results["tools_failed"].append(tool_test)
        
        return tools_results
    
    async def test_all_prompts(self) -> Dict[str, Any]:
        """Test all available prompts with various arguments"""
        print("\n📝 Testing All Prompts with Input/Output...")
        
        prompts_results = {
            "total_prompts": 0,
            "prompts_tested": [],
            "prompts_failed": []
        }
        
        # Get list of all prompts
        list_request = {
            "jsonrpc": "2.0",
            "method": "prompts/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        response = await self.client.post(f"{self.base_url}/messages", json=list_request)
        if response.status_code != 200:
            return {"error": "Failed to list prompts", "status_code": response.status_code}
        
        prompts_data = response.json()
        prompts = prompts_data.get("result", {}).get("prompts", [])
        prompts_results["total_prompts"] = len(prompts)
        
        # Test each prompt
        for prompt in prompts:
            prompt_name = prompt.get("name")
            print(f"    📄 Testing prompt: {prompt_name}")
            
            prompt_test = {
                "name": prompt_name,
                "description": prompt.get("description"),
                "arguments": prompt.get("arguments", []),
                "test_cases": []
            }
            
            # Get test arguments for this prompt
            test_args = self._get_test_arguments_for_prompt(prompt_name)
            
            for test_case in test_args:
                get_request = {
                    "jsonrpc": "2.0",
                    "method": "prompts/get",
                    "params": {
                        "name": prompt_name,
                        "arguments": test_case
                    },
                    "id": str(uuid.uuid4())
                }
                
                start = time.time()
                get_response = await self.client.post(f"{self.base_url}/messages", json=get_request)
                duration = time.time() - start
                
                test_result = {
                    "arguments": test_case,
                    "status_code": get_response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "success": get_response.status_code == 200
                }
                
                if get_response.status_code == 200:
                    result_data = get_response.json()
                    if "result" in result_data and "messages" in result_data["result"]:
                        messages = result_data["result"]["messages"]
                        if messages and len(messages) > 0:
                            test_result["message_count"] = len(messages)
                            test_result["first_message_preview"] = str(messages[0])[:200]
                elif get_response.status_code != 200:
                    test_result["error"] = get_response.text[:200]
                
                prompt_test["test_cases"].append(test_result)
            
            # Determine if prompt passed all tests
            prompt_passed = all(tc.get("success", False) for tc in prompt_test["test_cases"])
            if prompt_passed:
                prompts_results["prompts_tested"].append(prompt_test)
            else:
                prompts_results["prompts_failed"].append(prompt_test)
        
        return prompts_results
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance metrics and response times"""
        print("\n⚡ Testing Performance Metrics...")
        
        metrics = {
            "endpoint_response_times": {},
            "concurrent_requests": {},
            "large_payload_handling": {}
        }
        
        # Test endpoint response times
        endpoints = [
            ("/", "health_check"),
            ("/.well-known/mcp/resource", "mcp_discovery"),
            ("/messages", "messages_endpoint"),
            ("/sse", "sse_endpoint")
        ]
        
        for endpoint, name in endpoints:
            times = []
            for _ in range(5):  # 5 requests per endpoint
                start = time.time()
                if endpoint == "/messages":
                    await self.client.post(f"{self.base_url}{endpoint}", json={"jsonrpc": "2.0", "method": "initialize", "id": "1"})
                else:
                    await self.client.get(f"{self.base_url}{endpoint}", timeout=5.0)
                times.append((time.time() - start) * 1000)
            
            metrics["endpoint_response_times"][name] = {
                "avg_ms": round(sum(times) / len(times), 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2)
            }
        
        # Test concurrent requests
        print("    🔄 Testing concurrent requests...")
        async def make_request():
            start = time.time()
            try:
                response = await self.client.get(f"{self.base_url}/")
                return {"success": response.status_code == 200, "time_ms": (time.time() - start) * 1000}
            except:
                return {"success": False, "time_ms": (time.time() - start) * 1000}
        
        # Make 10 concurrent requests
        concurrent_results = await asyncio.gather(*[make_request() for _ in range(10)])
        success_count = sum(1 for r in concurrent_results if r["success"])
        avg_time = sum(r["time_ms"] for r in concurrent_results) / len(concurrent_results)
        
        metrics["concurrent_requests"] = {
            "total_requests": 10,
            "successful": success_count,
            "average_time_ms": round(avg_time, 2)
        }
        
        return metrics
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases"""
        print("\n🚨 Testing Error Handling...")
        
        error_tests = {}
        
        # Test invalid JSON-RPC method
        invalid_method = {
            "jsonrpc": "2.0",
            "method": "invalid/method",
            "params": {},
            "id": "1"
        }
        response = await self.client.post(f"{self.base_url}/messages", json=invalid_method)
        error_tests["invalid_method"] = {
            "status_code": response.status_code,
            "has_error": "error" in response.json() if response.status_code == 200 else False,
            "error_code": response.json().get("error", {}).get("code") if response.status_code == 200 else None
        }
        
        # Test malformed request
        malformed = {"not": "jsonrpc"}
        response = await self.client.post(f"{self.base_url}/messages", json=malformed)
        error_tests["malformed_request"] = {
            "status_code": response.status_code,
            "handled_gracefully": response.status_code in [200, 400]
        }
        
        # Test missing required parameters
        missing_params = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {},  # Missing 'name' parameter
            "id": "1"
        }
        response = await self.client.post(f"{self.base_url}/messages", json=missing_params)
        error_tests["missing_parameters"] = {
            "status_code": response.status_code,
            "has_error": "error" in response.json() if response.status_code == 200 else False
        }
        
        return error_tests
    
    async def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers and CORS configuration"""
        print("\n🔒 Testing Security Headers...")
        
        response = await self.client.options(f"{self.base_url}/messages")
        headers = dict(response.headers)
        
        security_tests = {
            "cors_enabled": "access-control-allow-origin" in headers,
            "cors_origin": headers.get("access-control-allow-origin"),
            "cors_methods": headers.get("access-control-allow-methods"),
            "cors_headers": headers.get("access-control-allow-headers"),
            "content_type_options": headers.get("x-content-type-options"),
            "frame_options": headers.get("x-frame-options")
        }
        
        return security_tests
    
    def _get_test_inputs_for_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get test inputs for specific tools"""
        test_cases = {
            "get_mcp_server_purpose": [
                {"input": {}, "expected_type": "object"}
            ],
            "get_dr_strunz_biography": [
                {"input": {}, "expected_type": "object"}
            ],
            "knowledge_search": [
                {"input": {"query": "vitamin D"}, "expected_type": "array"},
                {"input": {"query": "omega 3", "k": 5}, "expected_type": "array"}
            ],
            "create_health_protocol": [
                {"input": {
                    "symptoms": ["fatigue", "brain fog"],
                    "age": 45,
                    "gender": "male"
                }, "expected_type": "object"}
            ],
            "analyze_supplement_stack": [
                {"input": {
                    "supplements": ["vitamin D", "magnesium", "omega 3"],
                    "health_goals": ["energy", "cognitive function"]
                }, "expected_type": "object"}
            ]
        }
        
        return test_cases.get(tool_name, [{"input": {}, "expected_type": "any"}])
    
    def _get_test_arguments_for_prompt(self, prompt_name: str) -> List[Dict[str, Any]]:
        """Get test arguments for specific prompts"""
        test_args = {
            "health_assessment": [
                {"symptoms": "fatigue", "history": "none"},
                {"symptoms": "joint pain", "history": "arthritis"}
            ],
            "supplement_protocol": [
                {"goals": "energy", "conditions": "none"},
                {"goals": "immune support", "conditions": "autoimmune"}
            ],
            "nutrition_optimization": [
                {"current_diet": "standard", "objectives": "weight loss"},
                {"current_diet": "vegetarian", "objectives": "muscle gain"}
            ]
        }
        
        return test_args.get(prompt_name, [{}])
    
    async def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate test coverage report"""
        print("\n📊 Generating Coverage Report...")
        
        total_tests = 0
        passed_tests = 0
        
        # Count tests from each category
        for category, results in self.results["categories"].items():
            if isinstance(results, dict):
                for test_name, test_result in results.items():
                    if isinstance(test_result, dict):
                        total_tests += 1
                        if test_result.get("success") or test_result.get("resolved"):
                            passed_tests += 1
        
        # Count past issues
        for issue, result in self.results["past_issues_resolved"].items():
            total_tests += 1
            if result.get("resolved"):
                passed_tests += 1
        
        coverage = {
            "total_tests_run": total_tests,
            "tests_passed": passed_tests,
            "tests_failed": total_tests - passed_tests,
            "success_rate": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
            "execution_time_seconds": round(time.time() - self.start_time, 2)
        }
        
        return coverage
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print(f"\n🚀 Comprehensive Production Test Suite")
        print(f"📍 Target: {self.base_url}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run all test categories
        print("\n📋 Running All Test Categories...")
        
        # 1. Past Issues
        self.results["past_issues_resolved"] = await self.test_past_issues()
        
        # 2. All Tools
        self.results["categories"]["tools"] = await self.test_all_tools()
        
        # 3. All Prompts
        self.results["categories"]["prompts"] = await self.test_all_prompts()
        
        # 4. Performance
        self.results["categories"]["performance"] = await self.test_performance_metrics()
        
        # 5. Error Handling
        self.results["categories"]["error_handling"] = await self.test_error_handling()
        
        # 6. Security
        self.results["categories"]["security"] = await self.test_security_headers()
        
        # Generate coverage report
        self.results["coverage"] = await self.generate_coverage_report()
        
        # Generate summary
        await self._generate_summary()
        
        # Save results
        with open("comprehensive_production_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Past Issues Resolved: {sum(1 for r in self.results['past_issues_resolved'].values() if r.get('resolved'))}/{len(self.results['past_issues_resolved'])}")
        print(f"🛠️ Tools Tested: {self.results['categories']['tools'].get('total_tools', 0)}")
        print(f"📝 Prompts Tested: {self.results['categories']['prompts'].get('total_prompts', 0)}")
        print(f"⚡ Average Response Time: {self._calculate_avg_response_time()}ms")
        print(f"📈 Overall Success Rate: {self.results['coverage']['success_rate']}%")
        print(f"⏱️ Total Execution Time: {self.results['coverage']['execution_time_seconds']}s")
        
        await self.client.aclose()
        return self.results
    
    async def _generate_summary(self):
        """Generate executive summary"""
        self.results["summary"] = {
            "production_ready": self._is_production_ready(),
            "critical_issues": self._find_critical_issues(),
            "warnings": self._find_warnings(),
            "recommendations": self._generate_recommendations()
        }
    
    def _is_production_ready(self) -> bool:
        """Determine if system is production ready"""
        # Check critical criteria
        past_issues_ok = all(r.get("resolved") for r in self.results["past_issues_resolved"].values())
        tools_ok = self.results["categories"]["tools"].get("total_tools", 0) > 0
        performance_ok = self._calculate_avg_response_time() < 1000  # Under 1 second
        
        return past_issues_ok and tools_ok and performance_ok
    
    def _find_critical_issues(self) -> List[str]:
        """Find critical issues"""
        issues = []
        
        # Check past issues
        for issue, result in self.results["past_issues_resolved"].items():
            if not result.get("resolved"):
                issues.append(f"Past issue not resolved: {issue}")
        
        # Check tools
        tools = self.results["categories"]["tools"]
        if tools.get("total_tools", 0) < 19:
            issues.append(f"Only {tools.get('total_tools', 0)} tools available instead of 19")
        
        # Check failed tools
        if tools.get("tools_failed"):
            issues.append(f"{len(tools.get('tools_failed', []))} tools failed testing")
        
        return issues
    
    def _find_warnings(self) -> List[str]:
        """Find warnings"""
        warnings = []
        
        # Check performance
        avg_response = self._calculate_avg_response_time()
        if avg_response > 500:
            warnings.append(f"High average response time: {avg_response}ms")
        
        # Check error handling
        error_handling = self.results["categories"].get("error_handling", {})
        if not all(test.get("handled_gracefully", False) for test in error_handling.values()):
            warnings.append("Some error cases not handled gracefully")
        
        return warnings
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        tools = self.results["categories"]["tools"]
        if tools.get("total_tools", 0) < 19:
            recommendations.append("Deploy with full tool registry (all 19 tools)")
        
        if self.results["categories"]["prompts"].get("total_prompts", 0) == 0:
            recommendations.append("Enable prompt capabilities")
        
        security = self.results["categories"].get("security", {})
        if not security.get("content_type_options"):
            recommendations.append("Add security headers (X-Content-Type-Options, X-Frame-Options)")
        
        return recommendations
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all endpoints"""
        perf = self.results["categories"].get("performance", {}).get("endpoint_response_times", {})
        if not perf:
            return 0.0
        
        all_times = []
        for endpoint_data in perf.values():
            if "avg_ms" in endpoint_data:
                all_times.append(endpoint_data["avg_ms"])
        
        return round(sum(all_times) / len(all_times), 2) if all_times else 0.0

async def main():
    tester = ComprehensiveProductionTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())