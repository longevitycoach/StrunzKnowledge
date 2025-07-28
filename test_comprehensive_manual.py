#!/usr/bin/env python3
"""
Comprehensive MCP Server Test Suite
Generates detailed report with input/output values in table format
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class MCPTester:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        
    def make_request(self, method: str, params: Dict[str, Any] = None, endpoint: str = "/messages/") -> Dict[str, Any]:
        """Make MCP request and return response"""
        url = f"{self.base_url}{endpoint}"
        if endpoint == "/messages/":
            url += f"?session_id={self.session_id}"
            
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or {}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return {
                "status_code": response.status_code,
                "response": response.json() if response.text else {},
                "error": None
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": {},
                "error": str(e)
            }
    
    def test_endpoint(self, test_name: str, method: str, params: Dict[str, Any] = None, 
                     endpoint: str = "/messages/") -> Dict[str, Any]:
        """Run a single test and record results"""
        print(f"🧪 Testing: {test_name}")
        
        start_time = time.time()
        result = self.make_request(method, params, endpoint)
        duration = time.time() - start_time
        
        success = result["status_code"] == 200 and result["error"] is None
        
        test_result = {
            "test_name": test_name,
            "method": method,
            "params": params or {},
            "endpoint": endpoint,
            "status_code": result["status_code"],
            "success": success,
            "response": result["response"],
            "error": result["error"],
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        status = "✅" if success else "❌"
        print(f"   {status} {test_name} - {duration*1000:.0f}ms")
        
        return test_result

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive MCP Server Test Suite")
        print(f"📡 Testing endpoint: {self.base_url}")
        print(f"🔑 Session ID: {self.session_id}")
        print("=" * 80)
        
        # Test 1: Health Check
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            health_result = {
                "test_name": "Health Check",
                "method": "GET",
                "params": {},
                "endpoint": "/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.text else {},
                "error": None,
                "duration_ms": 0,
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(health_result)
            print(f"✅ Health Check - {response.status_code}")
        except Exception as e:
            print(f"❌ Health Check failed: {e}")
        
        # Test 2: Initialize
        self.test_endpoint(
            "Initialize Connection",
            "initialize",
            {
                "protocolVersion": "2025-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        )
        
        # Test 3: List Resources
        self.test_endpoint("List Resources", "resources/list")
        
        # Test 4: List Tools
        self.test_endpoint("List Tools", "tools/list")
        
        # Test 5: List Prompts
        self.test_endpoint("List Prompts", "prompts/list")
        
        # Test 6: Search Tool Test
        self.test_endpoint(
            "Search Knowledge - Basic",
            "tools/call",
            {
                "name": "search_knowledge",
                "arguments": {
                    "query": "Vitamin D",
                    "limit": 5
                }
            }
        )
        
        # Test 7: Advanced Search
        self.test_endpoint(
            "Search Knowledge - Advanced",
            "tools/call",
            {
                "name": "search_knowledge_advanced",
                "arguments": {
                    "query": "Magnesium deficiency",
                    "content_types": ["books", "news"],
                    "limit": 3
                }
            }
        )
        
        # Test 8: Get Book Content
        self.test_endpoint(
            "Get Book Content",
            "tools/call",
            {
                "name": "get_book_content",
                "arguments": {
                    "book_title": "Die Amino-Revolution",
                    "page_range": "1-5"
                }
            }
        )
        
        # Test 9: News Search
        self.test_endpoint(
            "Search News",
            "tools/call",
            {
                "name": "search_news",
                "arguments": {
                    "query": "Omega-3",
                    "limit": 3
                }
            }
        )
        
        # Test 10: Get Health Stats
        self.test_endpoint(
            "Get Health Stats",
            "tools/call",
            {
                "name": "get_health_stats",
                "arguments": {}
            }
        )
        
        print("=" * 80)
        print("🏁 Tests Complete!")
        
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
# Comprehensive MCP Server Test Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Endpoint:** {self.base_url}  
**Session ID:** {self.session_id}  
**Success Rate:** {success_rate:.1f}% ({successful_tests}/{total_tests})

## Test Summary

| Test Name | Method | Status | Duration (ms) | Status Code |
|-----------|--------|--------|---------------|-------------|
"""
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report += f"| {result['test_name']} | {result['method']} | {status} | {result['duration_ms']} | {result['status_code']} |\n"
        
        report += "\n## Detailed Test Results\n\n"
        
        for i, result in enumerate(self.test_results, 1):
            report += f"### {i}. {result['test_name']}\n\n"
            report += f"**Method:** `{result['method']}`  \n"
            report += f"**Endpoint:** `{result['endpoint']}`  \n"
            report += f"**Status:** {'✅ PASS' if result['success'] else '❌ FAIL'}  \n"
            report += f"**Duration:** {result['duration_ms']}ms  \n"
            report += f"**Status Code:** {result['status_code']}  \n"
            
            if result['params']:
                report += f"**Input Parameters:**\n```json\n{json.dumps(result['params'], indent=2)}\n```\n\n"
            
            if result['response']:
                report += f"**Response:**\n```json\n{json.dumps(result['response'], indent=2)}\n```\n\n"
            
            if result['error']:
                report += f"**Error:** {result['error']}\n\n"
            
            report += "---\n\n"
        
        # Analysis Section
        report += "## Analysis\n\n"
        
        if success_rate >= 80:
            report += "🟢 **Overall Status: GOOD** - Most tests passing successfully.\n\n"
        elif success_rate >= 60:
            report += "🟡 **Overall Status: WARNING** - Some issues detected.\n\n"
        else:
            report += "🔴 **Overall Status: CRITICAL** - Multiple failures detected.\n\n"
        
        # Failed tests analysis
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            report += "### Failed Tests Analysis\n\n"
            for result in failed_tests:
                report += f"- **{result['test_name']}**: "
                if result['error']:
                    report += f"Connection error - {result['error']}\n"
                elif result['status_code'] == 400:
                    report += "Bad request - likely parameter validation issue\n"
                elif result['status_code'] == 500:
                    report += "Server error - internal server issue\n"
                else:
                    report += f"HTTP {result['status_code']}\n"
        
        return report

def main():
    """Run comprehensive tests and generate report"""
    tester = MCPTester()
    tester.run_comprehensive_tests()
    
    # Generate and save report
    report = tester.generate_report()
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"src/tests/reports/comprehensive_test_report_{timestamp}.md"
    
    try:
        with open(filename, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {filename}")
    except Exception as e:
        print(f"❌ Could not save report: {e}")
    
    # Print report to console
    print("\n" + "=" * 80)
    print(report)
    
    return tester.test_results

if __name__ == "__main__":
    main()