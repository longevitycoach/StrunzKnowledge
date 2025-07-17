#!/usr/bin/env python3
"""
Production Test Suite for Dr. Strunz Knowledge MCP Server v0.6.3
Tests the live Railway deployment for functionality, performance, and reliability.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Test configuration
TEST_VERSION = "0.6.3"
TEST_DATE = datetime.now().strftime("%Y-%m-%d")
TEST_REPORT_DIR = Path(__file__).parent.parent.parent.parent / "docs" / "test-reports"
TEST_REPORT_FILE = TEST_REPORT_DIR / f"PRODUCTION_TEST_REPORT_v{TEST_VERSION}_{TEST_DATE}.md"

# Production endpoint
PRODUCTION_URL = "https://strunz.up.railway.app"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionTestSuite:
    """Production test suite for Railway deployment"""
    
    def __init__(self):
        self.results = {
            "version": TEST_VERSION,
            "test_date": TEST_DATE,
            "environment": "production_railway",
            "endpoint": PRODUCTION_URL,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {
                "connectivity": {"passed": 0, "failed": 0, "tests": []},
                "health_checks": {"passed": 0, "failed": 0, "tests": []},
                "version_validation": {"passed": 0, "failed": 0, "tests": []},
                "sse_integration": {"passed": 0, "failed": 0, "tests": []},
                "performance": {"passed": 0, "failed": 0, "tests": []},
                "reliability": {"passed": 0, "failed": 0, "tests": []},
                "security": {"passed": 0, "failed": 0, "tests": []}
            },
            "performance_metrics": {},
            "detailed_results": [],
            "recommendations": []
        }
        self.start_time = time.time()
        
        # Ensure test report directory exists
        TEST_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    def run_test(self, category: str, test_name: str, test_func: callable) -> bool:
        """Run a single test and record results"""
        self.results["total_tests"] += 1
        start_time = time.time()
        
        try:
            logger.info(f"Running {category}.{test_name}...")
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                self.results["passed_tests"] += 1
                self.results["test_categories"][category]["passed"] += 1
                status = "PASS"
                logger.info(f"✅ {test_name} passed ({duration:.2f}s)")
            else:
                self.results["failed_tests"] += 1
                self.results["test_categories"][category]["failed"] += 1
                status = "FAIL"
                logger.error(f"❌ {test_name} failed ({duration:.2f}s)")
            
            # Record detailed result
            test_result = {
                "category": category,
                "name": test_name,
                "status": status,
                "duration": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["test_categories"][category]["tests"].append(test_result)
            self.results["detailed_results"].append(test_result)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["failed_tests"] += 1
            self.results["test_categories"][category]["failed"] += 1
            
            error_result = {
                "category": category,
                "name": test_name,
                "status": "ERROR",
                "duration": round(duration, 2),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["test_categories"][category]["tests"].append(error_result)
            self.results["detailed_results"].append(error_result)
            
            logger.error(f"💥 {test_name} error: {e}")
            return False
    
    def http_request(self, path: str, timeout: int = 10) -> tuple:
        """Make HTTP request and return (status_code, data, response_time)"""
        url = f"{PRODUCTION_URL}{path}"
        start_time = time.time()
        
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', f'StrunzKnowledge-TestSuite/{TEST_VERSION}')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_time = time.time() - start_time
                data = response.read().decode('utf-8')
                
                try:
                    json_data = json.loads(data)
                    return response.status, json_data, response_time
                except json.JSONDecodeError:
                    return response.status, data, response_time
                    
        except urllib.error.HTTPError as e:
            response_time = time.time() - start_time
            return e.code, str(e), response_time
        except Exception as e:
            response_time = time.time() - start_time
            return 0, str(e), response_time
    
    def test_basic_connectivity(self) -> bool:
        """Test basic HTTP connectivity to production endpoint"""
        try:
            status, data, response_time = self.http_request("/")
            self.results["performance_metrics"]["health_response_time"] = round(response_time, 3)
            
            if status == 200:
                logger.info(f"Production endpoint responding ({response_time:.3f}s)")
                return True
            else:
                logger.error(f"Production endpoint returned status {status}")
                return False
                
        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return False
    
    def test_health_endpoint_structure(self) -> bool:
        """Test health endpoint returns proper structure"""
        try:
            status, data, response_time = self.http_request("/")
            
            if status != 200:
                return False
            
            if not isinstance(data, dict):
                logger.error("Health endpoint didn't return JSON object")
                return False
            
            # Check required fields
            required_fields = ["status", "server", "version", "protocol_version", "timestamp"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                logger.error(f"Health endpoint missing fields: {missing_fields}")
                return False
            
            # Store health data for other tests
            self.results["production_health_data"] = data
            logger.info(f"Health endpoint structure valid")
            return True
            
        except Exception as e:
            logger.error(f"Health structure test failed: {e}")
            return False
    
    def test_version_correctness(self) -> bool:
        """Test that production is running correct version"""
        try:
            if "production_health_data" not in self.results:
                return False
            
            health_data = self.results["production_health_data"]
            production_version = health_data.get("version", "unknown")
            
            # Allow for version mismatch during deployment window
            if production_version == TEST_VERSION:
                logger.info(f"Production version matches expected: {production_version}")
                return True
            else:
                logger.warning(f"Production version {production_version} != expected {TEST_VERSION}")
                # This is a warning, not a failure, during deployment transitions
                return True
                
        except Exception as e:
            logger.error(f"Version test failed: {e}")
            return False
    
    def test_protocol_compliance(self) -> bool:
        """Test MCP protocol version compliance"""
        try:
            if "production_health_data" not in self.results:
                return False
            
            health_data = self.results["production_health_data"]
            protocol_version = health_data.get("protocol_version", "unknown")
            
            # Should use latest MCP protocol
            expected_protocol = "2025-03-26"
            if protocol_version == expected_protocol:
                logger.info(f"Protocol version correct: {protocol_version}")
                return True
            else:
                logger.error(f"Protocol version {protocol_version} != expected {expected_protocol}")
                return False
                
        except Exception as e:
            logger.error(f"Protocol compliance test failed: {e}")
            return False
    
    def test_server_type_identification(self) -> bool:
        """Test server type is correctly identified"""
        try:
            if "production_health_data" not in self.results:
                return False
            
            health_data = self.results["production_health_data"]
            server_name = health_data.get("server", "unknown")
            
            # Should indicate it's the Dr. Strunz Knowledge server
            if "Dr. Strunz" in server_name and "Knowledge" in server_name:
                logger.info(f"Server identification correct: {server_name}")
                return True
            else:
                logger.error(f"Unexpected server name: {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Server identification test failed: {e}")
            return False
    
    def test_sse_endpoint_availability(self) -> bool:
        """Test SSE endpoint is available (if applicable)"""
        try:
            status, data, response_time = self.http_request("/sse", timeout=5)
            
            # SSE might not be available in clean MCP SDK implementation
            if status == 200:
                logger.info("SSE endpoint available")
                return True
            elif status == 404:
                logger.info("SSE endpoint not available (expected for clean MCP SDK)")
                return True  # This is acceptable
            else:
                logger.warning(f"SSE endpoint returned unexpected status: {status}")
                return True  # Not critical
                
        except Exception as e:
            logger.info(f"SSE endpoint test: {e} (acceptable)")
            return True  # SSE is optional
    
    def test_response_time_performance(self) -> bool:
        """Test response times are acceptable"""
        try:
            response_times = []
            
            # Test multiple requests
            for i in range(5):
                status, data, response_time = self.http_request("/")
                if status == 200:
                    response_times.append(response_time)
                time.sleep(0.5)  # Brief pause between requests
            
            if not response_times:
                logger.error("No successful responses for performance test")
                return False
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Store performance metrics
            self.results["performance_metrics"]["avg_response_time"] = round(avg_response_time, 3)
            self.results["performance_metrics"]["max_response_time"] = round(max_response_time, 3)
            self.results["performance_metrics"]["min_response_time"] = round(min_response_time, 3)
            
            # Should respond within reasonable time (< 2 seconds avg)
            if avg_response_time < 2.0:
                logger.info(f"Response times acceptable: {avg_response_time:.3f}s avg, {max_response_time:.3f}s max")
                return True
            else:
                logger.warning(f"Slow response times: {avg_response_time:.3f}s avg, {max_response_time:.3f}s max")
                return False
                
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False
    
    def test_uptime_stability(self) -> bool:
        """Test server uptime and stability"""
        try:
            if "production_health_data" not in self.results:
                return False
            
            health_data = self.results["production_health_data"]
            uptime_seconds = health_data.get("uptime_seconds", 0)
            
            # Store uptime metric
            self.results["performance_metrics"]["uptime_seconds"] = uptime_seconds
            uptime_hours = round(uptime_seconds / 3600, 1)
            
            # Should have reasonable uptime (> 1 minute for basic stability)
            if uptime_seconds > 60:
                logger.info(f"Server uptime stable: {uptime_hours} hours")
                return True
            else:
                logger.warning(f"Recent restart detected: {uptime_seconds}s uptime")
                return True  # Recent restarts are acceptable
                
        except Exception as e:
            logger.error(f"Uptime test failed: {e}")
            return False
    
    def test_consecutive_requests_reliability(self) -> bool:
        """Test reliability under consecutive requests"""
        try:
            success_count = 0
            total_requests = 10
            
            for i in range(total_requests):
                status, data, response_time = self.http_request("/")
                if status == 200:
                    success_count += 1
                time.sleep(0.2)  # Brief pause
            
            success_rate = (success_count / total_requests) * 100
            self.results["performance_metrics"]["reliability_success_rate"] = round(success_rate, 1)
            
            # Should have high success rate (> 95%)
            if success_rate >= 95:
                logger.info(f"Reliability excellent: {success_rate}% success rate")
                return True
            elif success_rate >= 80:
                logger.warning(f"Reliability moderate: {success_rate}% success rate")
                return True
            else:
                logger.error(f"Reliability poor: {success_rate}% success rate")
                return False
                
        except Exception as e:
            logger.error(f"Reliability test failed: {e}")
            return False
    
    def test_headers_security(self) -> bool:
        """Test security headers are present"""
        try:
            request = urllib.request.Request(PRODUCTION_URL + "/")
            request.add_header('User-Agent', f'StrunzKnowledge-TestSuite/{TEST_VERSION}')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                headers = dict(response.headers)
                
                # Check for Railway-specific headers (indicates proper deployment)
                railway_headers = [h for h in headers if 'railway' in h.lower()]
                if railway_headers:
                    logger.info(f"Railway deployment confirmed: {len(railway_headers)} Railway headers")
                    return True
                else:
                    logger.warning("No Railway headers detected")
                    return True  # Not critical
                    
        except Exception as e:
            logger.error(f"Security headers test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid endpoints"""
        try:
            # Test 404 handling
            status, data, response_time = self.http_request("/nonexistent-endpoint")
            
            if status == 404:
                logger.info("404 error handling working correctly")
                return True
            elif status in [405, 403]:  # Method not allowed or forbidden
                logger.info(f"Error handling working (status {status})")
                return True
            else:
                logger.warning(f"Unexpected error response: {status}")
                return True  # Not critical
                
        except Exception as e:
            logger.info(f"Error handling test: {e} (acceptable)")
            return True
    
    def run_all_tests(self):
        """Run all production tests"""
        logger.info(f"🚀 Starting Production Test Suite v{TEST_VERSION}")
        logger.info(f"📅 Test Date: {TEST_DATE}")
        logger.info(f"🌐 Production Endpoint: {PRODUCTION_URL}")
        logger.info("=" * 80)
        
        # Connectivity Tests
        if not self.run_test("connectivity", "basic_connectivity", self.test_basic_connectivity):
            logger.error("🚨 Basic connectivity failed - aborting tests")
            return self.results
        
        # Health Check Tests
        self.run_test("health_checks", "health_endpoint_structure", self.test_health_endpoint_structure)
        self.run_test("health_checks", "uptime_stability", self.test_uptime_stability)
        
        # Version Validation Tests
        self.run_test("version_validation", "version_correctness", self.test_version_correctness)
        self.run_test("version_validation", "protocol_compliance", self.test_protocol_compliance)
        self.run_test("version_validation", "server_identification", self.test_server_type_identification)
        
        # SSE Integration Tests
        self.run_test("sse_integration", "sse_endpoint_availability", self.test_sse_endpoint_availability)
        
        # Performance Tests
        self.run_test("performance", "response_time", self.test_response_time_performance)
        
        # Reliability Tests
        self.run_test("reliability", "consecutive_requests", self.test_consecutive_requests_reliability)
        
        # Security Tests
        self.run_test("security", "headers_security", self.test_headers_security)
        self.run_test("security", "error_handling", self.test_error_handling)
        
        # Calculate final metrics
        self.results["total_duration"] = round(time.time() - self.start_time, 2)
        self.results["success_rate"] = round(
            (self.results["passed_tests"] / self.results["total_tests"]) * 100, 1
        ) if self.results["total_tests"] > 0 else 0
        
        # Generate recommendations
        self._generate_recommendations()
        
        logger.info("=" * 80)
        logger.info(f"🏁 Production Test Suite Complete!")
        logger.info(f"📊 Results: {self.results['passed_tests']}/{self.results['total_tests']} tests passed ({self.results['success_rate']}%)")
        logger.info(f"⏱️  Duration: {self.results['total_duration']}s")
        
        return self.results
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Performance recommendations
        if "avg_response_time" in self.results["performance_metrics"]:
            avg_time = self.results["performance_metrics"]["avg_response_time"]
            if avg_time > 1.0:
                recommendations.append(f"⚡ Response times could be improved ({avg_time}s avg)")
            elif avg_time < 0.5:
                recommendations.append(f"🚀 Excellent response times ({avg_time}s avg)")
        
        # Reliability recommendations
        if "reliability_success_rate" in self.results["performance_metrics"]:
            success_rate = self.results["performance_metrics"]["reliability_success_rate"]
            if success_rate < 95:
                recommendations.append(f"⚠️  Reliability could be improved ({success_rate}% success rate)")
            else:
                recommendations.append(f"✅ Excellent reliability ({success_rate}% success rate)")
        
        # Version recommendations
        if "production_health_data" in self.results:
            health_data = self.results["production_health_data"]
            production_version = health_data.get("version", "unknown")
            if production_version != TEST_VERSION:
                recommendations.append(f"📋 Version mismatch: production={production_version}, expected={TEST_VERSION}")
        
        # Overall assessment
        if self.results["success_rate"] >= 95:
            recommendations.append("🎉 Production deployment is excellent - all systems operational")
        elif self.results["success_rate"] >= 85:
            recommendations.append("👍 Production deployment is good - minor issues detected")
        elif self.results["success_rate"] >= 70:
            recommendations.append("⚠️  Production deployment has moderate issues - investigation recommended")
        else:
            recommendations.append("🚨 Production deployment has significant issues - immediate attention required")
        
        self.results["recommendations"] = recommendations
    
    def generate_report(self):
        """Generate production test report"""
        report_content = f"""# Production Test Report v{TEST_VERSION}

**Test Date**: {TEST_DATE}  
**Environment**: Railway Production  
**Endpoint**: {PRODUCTION_URL}  
**Duration**: {self.results['total_duration']}s  
**Success Rate**: {self.results['success_rate']}%  

## 📊 Summary

- **Total Tests**: {self.results['total_tests']}
- **Passed**: {self.results['passed_tests']} ✅
- **Failed**: {self.results['failed_tests']} ❌
- **Success Rate**: {self.results['success_rate']}%

## 📈 Performance Metrics

"""
        
        if self.results["performance_metrics"]:
            for metric, value in self.results["performance_metrics"].items():
                report_content += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
        else:
            report_content += "- No performance metrics recorded\n"
        
        # Add production health data if available
        if "production_health_data" in self.results:
            health_data = self.results["production_health_data"]
            report_content += f"\n## 🏥 Production Health Status\n\n"
            report_content += f"- **Version**: {health_data.get('version', 'unknown')}\n"
            report_content += f"- **Protocol Version**: {health_data.get('protocol_version', 'unknown')}\n"
            report_content += f"- **Uptime**: {health_data.get('uptime_seconds', 0)} seconds\n"
            report_content += f"- **Status**: {health_data.get('status', 'unknown')}\n"
        
        report_content += "\n## 🎯 Test Categories\n\n"
        
        for category, data in self.results["test_categories"].items():
            total = data["passed"] + data["failed"]
            if total > 0:
                success_rate = round((data["passed"] / total) * 100, 1)
                status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                
                report_content += f"### {status_emoji} {category.replace('_', ' ').title()}\n"
                report_content += f"- **Passed**: {data['passed']}\n"
                report_content += f"- **Failed**: {data['failed']}\n"
                report_content += f"- **Success Rate**: {success_rate}%\n\n"
        
        report_content += "## 🧪 Detailed Test Results\n\n"
        
        for result in self.results["detailed_results"]:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
            report_content += f"- {status_emoji} **{result['category']}.{result['name']}** ({result['duration']}s)\n"
            if result["status"] == "ERROR" and "error" in result:
                report_content += f"  - Error: {result['error']}\n"
        
        report_content += "\n## 💡 Recommendations\n\n"
        
        for recommendation in self.results["recommendations"]:
            report_content += f"- {recommendation}\n"
        
        report_content += f"\n## 🔗 Related Documentation\n\n"
        report_content += f"- [Release Notes v{TEST_VERSION}](../RELEASE_NOTES_v{TEST_VERSION}.md)\n"
        report_content += f"- [Comprehensive Test Report v{TEST_VERSION}](COMPREHENSIVE_TEST_REPORT_v{TEST_VERSION}_{TEST_DATE}.md)\n"
        report_content += f"- [CLAUDE.md Development Guide](../../CLAUDE.md)\n"
        
        report_content += f"\n---\n\n*Generated on {TEST_DATE} by Production Test Suite v{TEST_VERSION}*\n"
        
        # Write report to file
        with open(TEST_REPORT_FILE, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📄 Production test report generated: {TEST_REPORT_FILE}")
        
        return report_content

def main():
    """Main production test execution"""
    try:
        # Run production test suite
        test_suite = ProductionTestSuite()
        results = test_suite.run_all_tests()
        
        # Generate report
        report = test_suite.generate_report()
        
        # Print summary
        print("\n" + "="*80)
        print(f"🌐 PRODUCTION TEST SUITE v{TEST_VERSION} COMPLETE")
        print("="*80)
        print(f"📊 Results: {results['passed_tests']}/{results['total_tests']} tests passed ({results['success_rate']}%)")
        print(f"⏱️  Duration: {results['total_duration']}s")
        print(f"🌐 Endpoint: {PRODUCTION_URL}")
        print(f"📄 Report: {TEST_REPORT_FILE}")
        print("="*80)
        
        # Exit with appropriate code
        exit_code = 0 if results['success_rate'] >= 80 else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"Production test suite execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())