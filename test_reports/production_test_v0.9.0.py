#!/usr/bin/env python3
"""
Production Test Suite for StrunzKnowledge v0.9.0
Comprehensive validation of Railway deployment
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ProductionTestSuite:
    def __init__(self):
        self.base_url = "https://strunz.up.railway.app"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.9.0",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def log_test(self, name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}")
        if details:
            print(f"     Details: {details}")
        if error:
            print(f"     Error: {error}")
    
    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                self.log_test("health_endpoint", True, f"Version: {version}, Status: {data.get('status')}")
                return data
            else:
                self.log_test("health_endpoint", False, error=f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("health_endpoint", False, error=str(e))
            return None
    
    def test_mcp_tools(self):
        """Test MCP tools availability"""
        try:
            # Test tools/list endpoint
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "test-tools-list"
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    tool_names = [tool["name"] for tool in tools]
                    self.log_test("mcp_tools_list", True, f"Found {len(tools)} tools")
                    return tool_names
                else:
                    self.log_test("mcp_tools_list", False, error="Invalid response format")
                    return []
            else:
                self.log_test("mcp_tools_list", False, error=f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("mcp_tools_list", False, error=str(e))
            return []
    
    def test_specific_tool(self, tool_name: str, params: Dict = None):
        """Test a specific MCP tool"""
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params or {}
                },
                "id": f"test-{tool_name}"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/messages",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    self.log_test(f"tool_{tool_name}", True, f"Response time: {response_time:.2f}s")
                    return True
                else:
                    error = data.get("error", {}).get("message", "Unknown error")
                    self.log_test(f"tool_{tool_name}", False, error=error)
                    return False
            else:
                self.log_test(f"tool_{tool_name}", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"tool_{tool_name}", False, error=str(e))
            return False
    
    def test_sse_endpoint(self):
        """Test SSE endpoint"""
        try:
            response = requests.get(f"{self.base_url}/sse", timeout=5, stream=True)
            if response.status_code == 200:
                self.log_test("sse_endpoint", True, "SSE endpoint accessible")
                return True
            else:
                self.log_test("sse_endpoint", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("sse_endpoint", False, error=str(e))
            return False
    
    def test_oauth_endpoints(self):
        """Test OAuth endpoints"""
        endpoints = [
            ("/oauth/authorize", "GET"),
            ("/oauth/token", "POST"),
            ("/.well-known/mcp/resource", "GET")
        ]
        
        all_passed = True
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=5)
                
                # OAuth endpoints may return various status codes
                if response.status_code in [200, 400, 401, 405]:
                    self.log_test(f"oauth_{endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"oauth_{endpoint}", False, error=f"Unexpected status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"oauth_{endpoint}", False, error=str(e))
                all_passed = False
        
        return all_passed
    
    def test_performance(self):
        """Test response times for various operations"""
        # Test health check performance
        times = []
        for i in range(5):
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}/", timeout=10)
                if response.status_code == 200:
                    times.append(time.time() - start)
            except:
                pass
        
        if times:
            avg_time = sum(times) / len(times)
            self.log_test("health_check_performance", avg_time < 1.0, 
                         f"Average response time: {avg_time:.3f}s")
        else:
            self.log_test("health_check_performance", False, error="No successful requests")
    
    def run_all_tests(self):
        """Run all production tests"""
        print("\n🧪 PRODUCTION TEST SUITE - StrunzKnowledge v0.9.0")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # Basic health check
        print("1. HEALTH CHECK TESTS")
        print("-" * 30)
        health_data = self.test_health_endpoint()
        
        # MCP Protocol tests
        print("\n2. MCP PROTOCOL TESTS")
        print("-" * 30)
        tools = self.test_mcp_tools()
        
        # Test sample tools
        if tools:
            print("\n3. TOOL FUNCTIONALITY TESTS")
            print("-" * 30)
            # Test a few key tools
            test_tools = [
                ("get_dr_strunz_biography", {}),
                ("get_mcp_server_purpose", {}),
                ("knowledge_search", {"query": "vitamin D", "max_results": 3}),
            ]
            
            for tool_name, params in test_tools:
                if tool_name in tools:
                    self.test_specific_tool(tool_name, params)
        
        # Transport tests
        print("\n4. TRANSPORT TESTS")
        print("-" * 30)
        self.test_sse_endpoint()
        
        # OAuth tests
        print("\n5. OAUTH INTEGRATION TESTS")
        print("-" * 30)
        self.test_oauth_endpoints()
        
        # Performance tests
        print("\n6. PERFORMANCE TESTS")
        print("-" * 30)
        self.test_performance()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed == 0:
            print("\n✅ ALL TESTS PASSED - Production deployment successful!")
        else:
            print("\n❌ SOME TESTS FAILED - Review failures above")
        
        # Save detailed report
        report_file = f"test_reports/production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    suite = ProductionTestSuite()
    suite.run_all_tests()