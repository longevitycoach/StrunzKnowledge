#!/usr/bin/env python3
"""
Comprehensive Railway Deployment Test Suite
==========================================

This script runs all valid tests against the Railway deployment
and generates a detailed test report with full input/output.

Tests include:
- Basic connectivity
- OAuth endpoints
- MCP protocol compliance
- Tool functionality
- Prompts capability
- Performance metrics

Author: Claude Code
Created: 2025-07-17
"""

import asyncio
import json
import aiohttp
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import urllib.parse
from pathlib import Path

# Railway deployment URL
RAILWAY_URL = "https://strunz.up.railway.app"

class RailwayTestSuite:
    def __init__(self):
        self.base_url = RAILWAY_URL
        self.session = None
        self.results = []
        self.start_time = None
        self.end_time = None
        
    async def setup(self):
        """Initialize test session"""
        self.session = aiohttp.ClientSession()
        self.start_time = datetime.now()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        self.end_time = datetime.now()
    
    def add_result(self, test_name: str, status: str, details: Dict):
        """Add test result"""
        self.results.append({
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
    
    async def test_health_check(self) -> Tuple[bool, Dict]:
        """Test 1: Basic Health Check"""
        test_name = "Health Check"
        endpoint = "/"
        
        try:
            start = time.time()
            async with self.session.get(f"{self.base_url}{endpoint}") as resp:
                duration = time.time() - start
                data = await resp.json()
                
                result = {
                    "endpoint": endpoint,
                    "method": "GET",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": {
                        "url": f"{self.base_url}{endpoint}",
                        "headers": dict(resp.request_info.headers)
                    },
                    "response": data
                }
                
                # Check critical fields
                success = (
                    resp.status == 200 and
                    data.get("status") == "healthy" and
                    "version" in data and
                    "protocol_version" in data
                )
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_oauth_discovery(self) -> Tuple[bool, Dict]:
        """Test 2: OAuth Discovery Endpoints"""
        test_name = "OAuth Discovery"
        endpoints = [
            "/.well-known/oauth-authorization-server",
            "/.well-known/oauth-protected-resource",
            "/.well-known/mcp/resource"
        ]
        
        all_success = True
        all_results = []
        
        for endpoint in endpoints:
            try:
                start = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}") as resp:
                    duration = time.time() - start
                    data = await resp.json()
                    
                    result = {
                        "endpoint": endpoint,
                        "method": "GET",
                        "status_code": resp.status,
                        "duration_ms": round(duration * 1000, 2),
                        "response": data
                    }
                    
                    success = resp.status == 200
                    all_success = all_success and success
                    all_results.append(result)
                    
            except Exception as e:
                result = {"endpoint": endpoint, "error": str(e)}
                all_results.append(result)
                all_success = False
        
        self.add_result(test_name, "PASS" if all_success else "FAIL", {"endpoints": all_results})
        return all_success, {"endpoints": all_results}
    
    async def test_oauth_registration(self) -> Tuple[bool, Dict]:
        """Test 3: OAuth Client Registration"""
        test_name = "OAuth Client Registration"
        endpoint = "/oauth/register"
        
        request_body = {
            "client_name": "Railway Test Client",
            "redirect_uris": ["https://test.railway.app/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"]
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data
                }
                
                success = (
                    resp.status == 200 and
                    "client_id" in data and
                    "redirect_uris" in data
                )
                
                if success:
                    self.client_id = data.get("client_id")
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_mcp_initialize(self) -> Tuple[bool, Dict]:
        """Test 4: MCP Initialize"""
        test_name = "MCP Initialize"
        endpoint = "/messages"
        
        request_body = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "clientInfo": {
                    "name": "Railway Test Suite",
                    "version": "1.0"
                }
            },
            "id": 1
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data
                }
                
                # Check for prompts capability
                prompts_present = False
                if "result" in data and "capabilities" in data["result"]:
                    prompts_present = "prompts" in data["result"]["capabilities"]
                
                success = (
                    resp.status == 200 and
                    "result" in data and
                    "protocolVersion" in data.get("result", {}) and
                    prompts_present  # Check for prompts capability
                )
                
                result["prompts_capability_present"] = prompts_present
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_mcp_tools_list(self) -> Tuple[bool, Dict]:
        """Test 5: MCP Tools List"""
        test_name = "MCP Tools List"
        endpoint = "/messages"
        
        request_body = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                # Extract tool names for summary
                tool_names = []
                if "result" in data and "tools" in data["result"]:
                    tool_names = [tool["name"] for tool in data["result"]["tools"]]
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data,
                    "tool_count": len(tool_names),
                    "tool_names": tool_names
                }
                
                success = (
                    resp.status == 200 and
                    "result" in data and
                    "tools" in data.get("result", {}) and
                    len(tool_names) > 0
                )
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_mcp_prompts_list(self) -> Tuple[bool, Dict]:
        """Test 6: MCP Prompts List"""
        test_name = "MCP Prompts List"
        endpoint = "/messages"
        
        request_body = {
            "jsonrpc": "2.0",
            "method": "prompts/list",
            "params": {},
            "id": 3
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                # Extract prompt names if available
                prompt_names = []
                if "result" in data and "prompts" in data["result"]:
                    prompt_names = [prompt["name"] for prompt in data["result"]["prompts"]]
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data,
                    "prompt_count": len(prompt_names),
                    "prompt_names": prompt_names
                }
                
                # This might fail if prompts aren't implemented yet
                success = resp.status == 200 and "error" not in data
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_mcp_tool_call(self) -> Tuple[bool, Dict]:
        """Test 7: MCP Tool Call"""
        test_name = "MCP Tool Call - get_dr_strunz_biography"
        endpoint = "/messages"
        
        request_body = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_dr_strunz_biography",
                "arguments": {}
            },
            "id": 4
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data
                }
                
                success = (
                    resp.status == 200 and
                    "result" in data and
                    "content" in data.get("result", {})
                )
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_search_functionality(self) -> Tuple[bool, Dict]:
        """Test 8: Search Functionality"""
        test_name = "MCP Tool Call - knowledge_search"
        endpoint = "/messages"
        
        request_body = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "knowledge_search",
                "arguments": {
                    "query": "Vitamin D",
                    "limit": 3
                }
            },
            "id": 5
        }
        
        try:
            start = time.time()
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=request_body
            ) as resp:
                duration = time.time() - start
                data = await resp.json()
                
                result = {
                    "endpoint": endpoint,
                    "method": "POST",
                    "status_code": resp.status,
                    "duration_ms": round(duration * 1000, 2),
                    "request": request_body,
                    "response": data
                }
                
                success = (
                    resp.status == 200 and
                    "result" in data and
                    "content" in data.get("result", {}) and
                    duration < 10  # Should complete within 10 seconds
                )
                
                self.add_result(test_name, "PASS" if success else "FAIL", result)
                return success, result
                
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint, "request": request_body}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_sse_endpoint(self) -> Tuple[bool, Dict]:
        """Test 9: SSE Endpoint"""
        test_name = "SSE Endpoint"
        endpoint = "/sse"
        
        try:
            # Test HEAD method
            start = time.time()
            async with self.session.head(f"{self.base_url}{endpoint}") as resp:
                head_duration = time.time() - start
                head_status = resp.status
            
            # Test GET method
            start = time.time()
            async with self.session.get(f"{self.base_url}{endpoint}") as resp:
                get_duration = time.time() - start
                get_status = resp.status
                
                # Read a small portion of the SSE stream
                content = ""
                if get_status == 200:
                    try:
                        content = await resp.content.read(100)
                        content = content.decode('utf-8') if content else ""
                    except:
                        content = "Could not read SSE stream"
            
            result = {
                "endpoint": endpoint,
                "head_method": {
                    "status_code": head_status,
                    "duration_ms": round(head_duration * 1000, 2)
                },
                "get_method": {
                    "status_code": get_status,
                    "duration_ms": round(get_duration * 1000, 2),
                    "sample_content": content[:100] if content else None
                }
            }
            
            success = head_status == 200 and get_status == 200
            
            self.add_result(test_name, "PASS" if success else "FAIL", result)
            return success, result
            
        except Exception as e:
            result = {"error": str(e), "endpoint": endpoint}
            self.add_result(test_name, "ERROR", result)
            return False, result
    
    async def test_performance_metrics(self) -> Tuple[bool, Dict]:
        """Test 10: Performance Metrics"""
        test_name = "Performance Metrics"
        
        # Run multiple requests to measure performance
        endpoints = [
            ("/", "GET", None),
            ("/messages", "POST", {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 10
            })
        ]
        
        metrics = []
        
        for endpoint, method, body in endpoints:
            try:
                times = []
                for i in range(3):  # 3 requests per endpoint
                    start = time.time()
                    
                    if method == "GET":
                        async with self.session.get(f"{self.base_url}{endpoint}") as resp:
                            await resp.text()
                            times.append((time.time() - start) * 1000)
                    else:
                        async with self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=body
                        ) as resp:
                            await resp.text()
                            times.append((time.time() - start) * 1000)
                
                metrics.append({
                    "endpoint": endpoint,
                    "method": method,
                    "requests": len(times),
                    "min_ms": round(min(times), 2),
                    "max_ms": round(max(times), 2),
                    "avg_ms": round(sum(times) / len(times), 2)
                })
                
            except Exception as e:
                metrics.append({
                    "endpoint": endpoint,
                    "method": method,
                    "error": str(e)
                })
        
        result = {"performance_metrics": metrics}
        
        # Success if all requests completed and average response time < 1 second
        success = all(
            "error" not in m and m.get("avg_ms", float('inf')) < 1000 
            for m in metrics
        )
        
        self.add_result(test_name, "PASS" if success else "FAIL", result)
        return success, result
    
    async def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Railway Deployment Tests")
        print(f"Target: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Basic Connectivity", self.test_health_check),
            ("OAuth Discovery", self.test_oauth_discovery),
            ("OAuth Registration", self.test_oauth_registration),
            ("MCP Initialize", self.test_mcp_initialize),
            ("MCP Tools List", self.test_mcp_tools_list),
            ("MCP Prompts List", self.test_mcp_prompts_list),
            ("Tool Execution", self.test_mcp_tool_call),
            ("Search Functionality", self.test_search_functionality),
            ("SSE Transport", self.test_sse_endpoint),
            ("Performance", self.test_performance_metrics)
        ]
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}...", end="", flush=True)
            
            try:
                success, _ = await test_func()
                if success:
                    print(" ✅ PASS")
                    passed += 1
                else:
                    print(" ❌ FAIL")
                    failed += 1
            except Exception as e:
                print(f" 💥 ERROR: {e}")
                errors += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {len(tests)}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💥 Errors: {errors}")
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            print(f"   Duration: {duration:.2f}s")
        
        return passed, failed, errors
    
    def generate_detailed_report(self) -> str:
        """Generate detailed test report"""
        report = []
        report.append("# Railway Deployment Test Report")
        report.append(f"\n**Generated**: {datetime.now().isoformat()}")
        report.append(f"**Target**: {self.base_url}")
        if self.start_time and self.end_time:
            report.append(f"**Duration**: {(self.end_time - self.start_time).total_seconds():.2f}s")
        elif self.start_time:
            report.append(f"**Duration**: {(datetime.now() - self.start_time).total_seconds():.2f}s")
        report.append("\n---\n")
        
        # Summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        
        report.append("## Summary")
        report.append(f"- **Total Tests**: {len(self.results)}")
        report.append(f"- **Passed**: {passed} ✅")
        report.append(f"- **Failed**: {failed} ❌")
        report.append(f"- **Errors**: {errors} 💥")
        report.append(f"- **Success Rate**: {(passed / len(self.results) * 100):.1f}%")
        report.append("\n---\n")
        
        # Detailed Results
        report.append("## Detailed Test Results")
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n### Test {i}: {result['test_name']}")
            report.append(f"**Status**: {result['status']}")
            report.append(f"**Timestamp**: {result['timestamp']}")
            
            # Format details based on test type
            details = result["details"]
            
            if "endpoint" in details:
                report.append(f"\n**Endpoint**: `{details.get('endpoint')}`")
                report.append(f"**Method**: {details.get('method', 'N/A')}")
                
                if "status_code" in details:
                    report.append(f"**Status Code**: {details['status_code']}")
                
                if "duration_ms" in details:
                    report.append(f"**Response Time**: {details['duration_ms']}ms")
            
            # Request details
            if "request" in details and isinstance(details["request"], dict):
                report.append("\n**Request**:")
                report.append("```json")
                report.append(json.dumps(details["request"], indent=2))
                report.append("```")
            
            # Response details
            if "response" in details:
                report.append("\n**Response**:")
                report.append("```json")
                # Truncate large responses
                response_str = json.dumps(details["response"], indent=2)
                if len(response_str) > 1000:
                    response_str = response_str[:1000] + "\n... (truncated)"
                report.append(response_str)
                report.append("```")
            
            # Special fields
            if "prompts_capability_present" in details:
                report.append(f"\n**Prompts Capability**: {'✅ Present' if details['prompts_capability_present'] else '❌ Missing'}")
            
            if "tool_count" in details:
                report.append(f"\n**Tools Found**: {details['tool_count']}")
                if details.get("tool_names"):
                    report.append("**Tool Names**: " + ", ".join(details["tool_names"][:5]) + 
                                ("..." if len(details["tool_names"]) > 5 else ""))
            
            if "prompt_count" in details:
                report.append(f"\n**Prompts Found**: {details['prompt_count']}")
                if details.get("prompt_names"):
                    report.append("**Prompt Names**: " + ", ".join(details["prompt_names"][:5]) + 
                                ("..." if len(details["prompt_names"]) > 5 else ""))
            
            if "performance_metrics" in details:
                report.append("\n**Performance Metrics**:")
                for metric in details["performance_metrics"]:
                    report.append(f"- {metric['endpoint']} ({metric['method']}): " +
                                f"avg={metric.get('avg_ms', 'N/A')}ms, " +
                                f"min={metric.get('min_ms', 'N/A')}ms, " +
                                f"max={metric.get('max_ms', 'N/A')}ms")
            
            if "error" in details:
                report.append(f"\n**Error**: {details['error']}")
            
            report.append("\n---")
        
        # Key Findings
        report.append("\n## Key Findings")
        
        # Check for prompts capability
        prompts_test = next((r for r in self.results if r["test_name"] == "MCP Initialize"), None)
        if prompts_test and "prompts_capability_present" in prompts_test["details"]:
            if prompts_test["details"]["prompts_capability_present"]:
                report.append("- ✅ **Prompts capability is present** (required for Claude.ai)")
            else:
                report.append("- ❌ **Prompts capability is missing** (will cause Claude.ai to show as disabled)")
        
        # Check version
        health_test = next((r for r in self.results if r["test_name"] == "Health Check"), None)
        if health_test and "response" in health_test["details"]:
            version = health_test["details"]["response"].get("version", "Unknown")
            report.append(f"- **Server Version**: {version}")
        
        # Performance summary
        perf_test = next((r for r in self.results if r["test_name"] == "Performance Metrics"), None)
        if perf_test and "performance_metrics" in perf_test["details"]:
            avg_times = [m.get("avg_ms", 0) for m in perf_test["details"]["performance_metrics"] if "avg_ms" in m]
            if avg_times:
                overall_avg = sum(avg_times) / len(avg_times)
                report.append(f"- **Average Response Time**: {overall_avg:.2f}ms")
        
        return "\n".join(report)


async def main():
    """Main test runner"""
    tester = RailwayTestSuite()
    
    try:
        await tester.setup()
        passed, failed, errors = await tester.run_all_tests()
        
        # Generate and save report
        report = tester.generate_detailed_report()
        
        # Save to file
        report_path = Path("src/tests/reports/railway_test_report.md")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Also save JSON results
        json_path = Path("src/tests/reports/railway_test_results.json")
        with open(json_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "target": RAILWAY_URL,
                "summary": {
                    "total": len(tester.results),
                    "passed": passed,
                    "failed": failed,
                    "errors": errors
                },
                "results": tester.results
            }, f, indent=2)
        
        print(f"📊 JSON results saved to: {json_path}")
        
        # Exit with appropriate code
        sys.exit(0 if failed == 0 and errors == 0 else 1)
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())