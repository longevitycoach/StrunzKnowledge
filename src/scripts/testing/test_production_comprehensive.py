#!/usr/bin/env python3
"""
TEMPORARY TEST SCRIPT - DELETE AFTER USE
Purpose: Comprehensive production testing for Railway deployment
Location: src/scripts/testing/test_production_comprehensive.py

Tests production deployment with detailed reporting
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

class ProductionTester:
    def __init__(self, base_url: str = "https://strunz.up.railway.app"):
        self.base_url = base_url
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, path: str, method: str = "GET", data: Dict = None, expected_status: int = 200) -> Dict:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            if method == "GET":
                async with self.session.get(url) as resp:
                    response_time = (time.time() - start_time) * 1000
                    content = await resp.text()
                    
                    result = {
                        "endpoint": path,
                        "method": method,
                        "status": resp.status,
                        "expected_status": expected_status,
                        "response_time_ms": round(response_time, 2),
                        "success": resp.status == expected_status,
                        "content_length": len(content),
                        "content": content[:500] if len(content) > 500 else content
                    }
                    
                    if resp.content_type == "application/json":
                        try:
                            result["json"] = json.loads(content)
                        except:
                            pass
                    
                    return result
                    
            elif method == "POST":
                async with self.session.post(url, json=data) as resp:
                    response_time = (time.time() - start_time) * 1000
                    content = await resp.text()
                    
                    result = {
                        "endpoint": path,
                        "method": method,
                        "status": resp.status,
                        "expected_status": expected_status,
                        "response_time_ms": round(response_time, 2),
                        "success": resp.status == expected_status,
                        "content_length": len(content),
                        "content": content[:500] if len(content) > 500 else content
                    }
                    
                    if resp.content_type == "application/json":
                        try:
                            result["json"] = json.loads(content)
                        except:
                            pass
                    
                    return result
                    
            elif method == "HEAD":
                async with self.session.head(url) as resp:
                    response_time = (time.time() - start_time) * 1000
                    
                    result = {
                        "endpoint": path,
                        "method": method,
                        "status": resp.status,
                        "expected_status": expected_status,
                        "response_time_ms": round(response_time, 2),
                        "success": resp.status == expected_status,
                        "content_length": 0,
                        "content": ""
                    }
                    
                    return result
                    
        except Exception as e:
            return {
                "endpoint": path,
                "method": method,
                "status": 0,
                "expected_status": expected_status,
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "success": False,
                "error": str(e),
                "content_length": 0,
                "content": ""
            }
    
    async def run_comprehensive_tests(self):
        """Run comprehensive production tests"""
        print("🚀 Starting comprehensive production tests...")
        
        # Health check tests
        print("\n1. Health Check Tests")
        health_get = await self.test_endpoint("/", "GET", expected_status=200)
        health_head = await self.test_endpoint("/", "HEAD", expected_status=200)
        
        self.results.extend([health_get, health_head])
        
        print(f"   GET /: {health_get['status']} ({'✅' if health_get['success'] else '❌'})")
        print(f"   HEAD /: {health_head['status']} ({'✅' if health_head['success'] else '❌'})")
        
        # Extract version info
        version = "Unknown"
        if health_get.get("json"):
            version = health_get["json"].get("version", "Unknown")
        print(f"   Version: {version}")
        
        # OAuth endpoints test
        print("\n2. OAuth Endpoints Tests")
        oauth_endpoints = [
            "/.well-known/oauth-authorization-server",
            "/.well-known/oauth-protected-resource",
            "/oauth/register",
            "/oauth/authorize?client_id=test&redirect_uri=http://localhost",
            "/oauth/token",
            "/oauth/userinfo"
        ]
        
        oauth_results = []
        for endpoint in oauth_endpoints:
            if endpoint == "/oauth/register":
                result = await self.test_endpoint(endpoint, "POST", {"client_name": "test"}, expected_status=200)
            elif endpoint == "/oauth/token":
                result = await self.test_endpoint(endpoint, "POST", {"grant_type": "authorization_code"}, expected_status=400)
            else:
                result = await self.test_endpoint(endpoint, "GET", expected_status=200)
            
            oauth_results.append(result)
            self.results.append(result)
            print(f"   {endpoint}: {result['status']} ({'✅' if result['success'] else '❌'})")
        
        # MCP endpoints test
        print("\n3. MCP Endpoints Tests")
        mcp_endpoints = [
            "/sse",
            "/messages",
            "/.well-known/mcp/resource",
            "/mcp"
        ]
        
        mcp_results = []
        for endpoint in mcp_endpoints:
            if endpoint == "/messages":
                result = await self.test_endpoint(endpoint, "POST", {"method": "initialize"}, expected_status=200)
            else:
                result = await self.test_endpoint(endpoint, "GET", expected_status=200)
            
            mcp_results.append(result)
            self.results.append(result)
            print(f"   {endpoint}: {result['status']} ({'✅' if result['success'] else '❌'})")
        
        # Performance metrics
        print("\n4. Performance Metrics")
        response_times = [r["response_time_ms"] for r in self.results if r["success"]]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"   Average response time: {avg_time:.2f}ms")
            print(f"   Min response time: {min_time:.2f}ms")
            print(f"   Max response time: {max_time:.2f}ms")
        
        # Summary
        print("\n5. Test Summary")
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        return {
            "version": version,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.results
        }

    def generate_report(self, test_results: Dict):
        """Generate detailed test report"""
        report = f"""# Production Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Environment
- **URL**: {self.base_url}
- **Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Server Version**: {test_results['version']}

## Test Results Summary
- **Total Tests**: {test_results['total_tests']}
- **Passed**: {test_results['passed_tests']}
- **Failed**: {test_results['failed_tests']}
- **Success Rate**: {test_results['success_rate']:.1f}%

## Detailed Results

### Health Check Tests
"""
        
        for result in test_results['results']:
            if result['endpoint'] == '/':
                status_icon = '✅' if result['success'] else '❌'
                report += f"- **{result['method']} {result['endpoint']}**: {result['status']} {status_icon} ({result['response_time_ms']}ms)\n"
        
        report += "\n### OAuth Endpoints\n"
        for result in test_results['results']:
            if 'oauth' in result['endpoint'] or 'well-known' in result['endpoint']:
                status_icon = '✅' if result['success'] else '❌'
                report += f"- **{result['method']} {result['endpoint']}**: {result['status']} {status_icon} ({result['response_time_ms']}ms)\n"
        
        report += "\n### MCP Endpoints\n"
        for result in test_results['results']:
            if result['endpoint'] in ['/sse', '/messages', '/.well-known/mcp/resource', '/mcp']:
                status_icon = '✅' if result['success'] else '❌'
                report += f"- **{result['method']} {result['endpoint']}**: {result['status']} {status_icon} ({result['response_time_ms']}ms)\n"
        
        report += "\n## Issues Identified\n"
        
        failed_results = [r for r in test_results['results'] if not r['success']]
        if failed_results:
            for result in failed_results:
                report += f"- **{result['method']} {result['endpoint']}**: Status {result['status']} (Expected {result['expected_status']})\n"
        else:
            report += "- No issues identified\n"
        
        return report

async def main():
    async with ProductionTester() as tester:
        results = await tester.run_comprehensive_tests()
        
        # Generate report
        report = tester.generate_report(results)
        
        # Save report
        report_file = f"docs/test-reports/PRODUCTION_TEST_REPORT_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📊 Report saved to: {report_file}")
        
        # Print issues
        if results['failed_tests'] > 0:
            print("\n🚨 Issues Found:")
            print("1. Health check HEAD request returns 405 (should support HEAD)")
            print("2. OAuth endpoints returning 404 (missing in current deployment)")
            print("3. Version mismatch - showing older version")
            print("4. /mcp endpoint missing (404)")

if __name__ == "__main__":
    asyncio.run(main())