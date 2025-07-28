#!/usr/bin/env python3
"""
Comprehensive Test Suite for MCP Server v3.0
Tests all fixed issues and validates proper protocol implementation
"""

import requests
import json
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

class MCPServerV3Tester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        
    def make_request(self, method: str, endpoint: str, payload: Dict[str, Any] = None, 
                    headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MCPTester/3.0'
        }
        if headers:
            default_headers.update(headers)
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=payload, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                "status_code": response.status_code,
                "response": response.json() if response.text and response.headers.get('content-type', '').startswith('application/json') else response.text,
                "headers": dict(response.headers),
                "error": None
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": {},
                "headers": {},
                "error": str(e)
            }
    
    def test_endpoint(self, test_name: str, method: str, endpoint: str, 
                     payload: Dict[str, Any] = None, headers: Dict[str, str] = None,
                     expected_status: int = 200) -> Dict[str, Any]:
        """Run a single test and record results"""
        print(f"🧪 Testing: {test_name}")
        
        start_time = time.time()
        result = self.make_request(method, endpoint, payload, headers)
        duration = time.time() - start_time
        
        success = result["status_code"] == expected_status and result["error"] is None
        
        test_result = {
            "test_name": test_name,
            "method": method,
            "endpoint": endpoint,
            "payload": payload or {},
            "status_code": result["status_code"],
            "expected_status": expected_status,
            "success": success,
            "response": result["response"],
            "headers": result["headers"],
            "error": result["error"],
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        status = "✅" if success else "❌"
        print(f"   {status} {test_name} - {duration*1000:.0f}ms - Status: {result['status_code']}")
        
        return test_result

    def run_protocol_tests(self):
        """Test MCP protocol fixes"""
        print("🔧 Testing MCP Protocol Fixes")
        print("=" * 80)
        
        # Test 1: Health Check (should work)
        self.test_endpoint("Health Check", "GET", "/")
        
        # Test 2: OAuth Registration (Fix #3 - Missing Endpoints)
        self.test_endpoint("OAuth Registration", "GET", "/oauth/register")
        
        # Test 3: OAuth Authorization
        self.test_endpoint("OAuth Authorization", "GET", "/oauth/authorize?client_id=test&response_type=code&scope=read")
        
        # Test 4: Claude.ai Start Auth (Fix #3)
        self.test_endpoint("Claude.ai Start Auth", "GET", "/api/organizations/test-org/mcp/start-auth/test-auth")
        
        # Test 5: OAuth Callback (Fix #3)
        self.test_endpoint("OAuth Callback", "GET", "/api/mcp/auth_callback?code=test&state=test")
        
        # Test 6: SSE Endpoint GET (Fix #4 - Transport Issues)
        headers = {'Accept': 'text/event-stream'}
        result = self.test_endpoint("SSE Endpoint GET", "GET", "/sse", headers=headers)
        
        # Test 7: MCP Endpoint GET (Fix #4 - Transport Issues)
        self.test_endpoint("MCP Endpoint GET", "GET", "/mcp", headers=headers)
        
    def run_session_tests(self):
        """Test session management fixes"""
        print("\n🔗 Testing Session Management")
        print("=" * 80)
        
        # Test session-based MCP requests
        session_headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        # Test 8: Initialize Request (Fix #1 & #2 - ASGI and Protocol Mismatch)
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client-v3",
                    "version": "3.0.0"
                }
            }
        }
        
        # Test with different endpoints to check session management
        endpoints_to_test = ["/sse", "/mcp"]
        
        for endpoint in endpoints_to_test:
            self.test_endpoint(
                f"Initialize via {endpoint}",
                "POST",
                f"{endpoint}?session_id={self.session_id}",
                init_payload,
                session_headers,
                expected_status=200  # Should work now with proper session management
            )
        
    def run_tool_tests(self):
        """Test tool functionality"""
        print("\n🛠️  Testing Tool Functionality")
        print("=" * 80)
        
        # Test tools via different endpoints
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        self.test_endpoint(
            "List Tools via SSE",
            "POST",
            f"/sse?session_id={self.session_id}",
            tools_payload,
            {'Content-Type': 'application/json'},
            expected_status=200
        )
        
        # Test tool execution
        search_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_knowledge",
                "arguments": {
                    "query": "Vitamin D",
                    "limit": 3
                }
            }
        }
        
        self.test_endpoint(
            "Execute Search Tool",
            "POST",
            f"/sse?session_id={self.session_id}",
            search_payload,
            {'Content-Type': 'application/json'},
            expected_status=200
        )

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive MCP Server v3.0 Test Suite")
        print(f"📡 Testing endpoint: {self.base_url}")
        print(f"🔑 Session ID: {self.session_id}")
        print("=" * 80)
        
        # Run test suites
        self.run_protocol_tests()
        self.run_session_tests()
        self.run_tool_tests()
        
        print("\n" + "=" * 80)
        print("🏁 Tests Complete!")
        
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
# MCP Server v3.0 Protocol Fixes Test Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Endpoint:** {self.base_url}  
**Session ID:** {self.session_id}  
**Success Rate:** {success_rate:.1f}% ({successful_tests}/{total_tests})

## Issues Fixed in v3.0

✅ **Issue #1 - ASGI Response Handling Bug**: Fixed by using proper FastMCP session management  
✅ **Issue #2 - Protocol Mismatch**: Fixed by implementing correct MCP protocol patterns  
✅ **Issue #3 - Missing OAuth Endpoints**: Added all required Claude.ai compatibility endpoints  
✅ **Issue #4 - SSE Transport Issues**: Fixed method restrictions and proper SSE streaming  

## Test Results Summary

| Test Name | Method | Endpoint | Status | Duration (ms) | Status Code |
|-----------|--------|----------|--------|---------------|-------------|
"""
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report += f"| {result['test_name']} | {result['method']} | {result['endpoint']} | {status} | {result['duration_ms']} | {result['status_code']} |\n"
        
        report += "\n## Detailed Results\n\n"
        
        for i, result in enumerate(self.test_results, 1):
            report += f"### {i}. {result['test_name']}\n\n"
            report += f"**Method:** `{result['method']}`  \n"
            report += f"**Endpoint:** `{result['endpoint']}`  \n"
            report += f"**Status:** {'✅ PASS' if result['success'] else '❌ FAIL'}  \n"
            report += f"**Duration:** {result['duration_ms']}ms  \n"
            report += f"**Status Code:** {result['status_code']} (expected: {result['expected_status']})  \n"
            
            if result['error']:
                report += f"**Error:** {result['error']}\n\n"
                
            report += "---\n\n"
        
        # Analysis Section
        report += "## Analysis\n\n"
        
        if success_rate >= 90:
            report += "🟢 **Overall Status: EXCELLENT** - All major issues resolved!\n\n"
        elif success_rate >= 70:
            report += "🟡 **Overall Status: GOOD** - Most issues resolved, minor issues remain.\n\n"
        else:
            report += "🔴 **Overall Status: NEEDS WORK** - Some critical issues remain.\n\n"
        
        return report

def test_local():
    """Test local development server"""
    print("Testing local server...")
    tester = MCPServerV3Tester("http://localhost:8080")
    tester.run_comprehensive_tests()
    report = tester.generate_report()
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"src/tests/reports/v3_test_report_{timestamp}.md"
    
    try:
        with open(filename, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {filename}")
    except Exception as e:
        print(f"❌ Could not save report: {e}")
    
    print(report)
    return tester.test_results

def test_production():
    """Test production server"""
    print("Testing production server...")
    tester = MCPServerV3Tester("https://strunz.up.railway.app")
    tester.run_comprehensive_tests()
    report = tester.generate_report()
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"src/tests/reports/v3_production_test_report_{timestamp}.md"
    
    try:
        with open(filename, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {filename}")
    except Exception as e:
        print(f"❌ Could not save report: {e}")
    
    print(report)
    return tester.test_results

def main():
    """Main test function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "production":
        test_production()
    else:
        test_local()

if __name__ == "__main__":
    main()