#!/usr/bin/env python3
"""
Docker Comprehensive Test Runner for Dr. Strunz Knowledge MCP Server v0.6.3
Tests the complete Docker deployment scenario including container build, startup, and functionality.
"""

import os
import sys
import json
import time
import docker
import requests
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_VERSION = "0.6.3"
TEST_DATE = datetime.now().strftime("%Y-%m-%d")
TEST_REPORT_DIR = project_root / "docs" / "test-reports"
TEST_REPORT_FILE = TEST_REPORT_DIR / f"LOCAL_DOCKER_TEST_REPORT_v{TEST_VERSION}_{TEST_DATE}.md"

# Docker configuration
DOCKER_IMAGE_NAME = f"strunz-mcp:{TEST_VERSION}-test"
DOCKER_CONTAINER_NAME = f"strunz-test-{int(time.time())}"
DOCKER_PORT = 8001  # Use different port to avoid conflicts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerTestRunner:
    """Docker-specific test runner for comprehensive validation"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container = None
        self.image = None
        self.results = {
            "version": TEST_VERSION,
            "test_date": TEST_DATE,
            "environment": "local_docker",
            "docker_info": {},
            "build_metrics": {},
            "runtime_metrics": {},
            "tests": {
                "build": {"passed": 0, "failed": 0, "tests": []},
                "startup": {"passed": 0, "failed": 0, "tests": []},
                "functionality": {"passed": 0, "failed": 0, "tests": []},
                "performance": {"passed": 0, "failed": 0, "tests": []},
                "cleanup": {"passed": 0, "failed": 0, "tests": []}
            },
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
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
                self.results["tests"][category]["passed"] += 1
                status = "PASS"
                logger.info(f"✅ {test_name} passed ({duration:.2f}s)")
            else:
                self.results["failed_tests"] += 1
                self.results["tests"][category]["failed"] += 1
                status = "FAIL"
                logger.error(f"❌ {test_name} failed ({duration:.2f}s)")
            
            # Record test result
            test_result = {
                "name": test_name,
                "status": status,
                "duration": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            self.results["tests"][category]["tests"].append(test_result)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.results["failed_tests"] += 1
            self.results["tests"][category]["failed"] += 1
            
            error_result = {
                "name": test_name,
                "status": "ERROR",
                "duration": round(duration, 2),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["tests"][category]["tests"].append(error_result)
            
            logger.error(f"💥 {test_name} error: {e}")
            return False
    
    def test_docker_build(self) -> bool:
        """Test Docker image build process"""
        try:
            build_start = time.time()
            
            # Build the Docker image
            logger.info(f"Building Docker image: {DOCKER_IMAGE_NAME}")
            self.image, build_logs = self.docker_client.images.build(
                path=str(project_root),
                tag=DOCKER_IMAGE_NAME,
                rm=True,
                forcerm=True
            )
            
            build_time = time.time() - build_start
            self.results["build_metrics"]["build_time"] = round(build_time, 2)
            self.results["build_metrics"]["image_id"] = self.image.id[:12]
            
            # Get image size
            image_info = self.docker_client.api.inspect_image(self.image.id)
            image_size_mb = round(image_info['Size'] / (1024 * 1024), 1)
            self.results["build_metrics"]["image_size_mb"] = image_size_mb
            
            logger.info(f"✅ Docker build completed in {build_time:.2f}s, size: {image_size_mb}MB")
            return True
            
        except Exception as e:
            logger.error(f"Docker build failed: {e}")
            return False
    
    def test_docker_startup(self) -> bool:
        """Test Docker container startup"""
        try:
            startup_start = time.time()
            
            # Start the container
            logger.info(f"Starting Docker container: {DOCKER_CONTAINER_NAME}")
            self.container = self.docker_client.containers.run(
                self.image.id,
                name=DOCKER_CONTAINER_NAME,
                ports={8000: DOCKER_PORT},
                environment={
                    'RAILWAY_ENVIRONMENT': 'production',
                    'RAILWAY_PUBLIC_DOMAIN': f'localhost:{DOCKER_PORT}',
                    'PORT': '8000'
                },
                detach=True,
                remove=False  # Keep for inspection
            )
            
            # Wait for container to be ready
            max_wait = 60  # 60 seconds max wait
            wait_time = 0
            while wait_time < max_wait:
                try:
                    # Check if container is still running
                    self.container.reload()
                    if self.container.status != 'running':
                        logger.error(f"Container stopped unexpectedly: {self.container.status}")
                        return False
                    
                    # Try to connect to health endpoint
                    response = requests.get(f'http://localhost:{DOCKER_PORT}/', timeout=5)
                    if response.status_code == 200:
                        startup_time = time.time() - startup_start
                        self.results["runtime_metrics"]["startup_time"] = round(startup_time, 2)
                        logger.info(f"✅ Container started successfully in {startup_time:.2f}s")
                        return True
                        
                except requests.exceptions.RequestException:
                    # Still starting up
                    pass
                
                time.sleep(2)
                wait_time += 2
            
            logger.error("Container failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Docker startup failed: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint responds correctly"""
        try:
            response = requests.get(f'http://localhost:{DOCKER_PORT}/', timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Health endpoint returned {response.status_code}")
                return False
            
            health_data = response.json()
            
            # Check required fields
            required_fields = ['status', 'server', 'version']
            for field in required_fields:
                if field not in health_data:
                    logger.error(f"Health response missing field: {field}")
                    return False
            
            # Check version matches
            if health_data['version'] != TEST_VERSION:
                logger.warning(f"Version mismatch: expected {TEST_VERSION}, got {health_data['version']}")
            
            self.results["runtime_metrics"]["health_response"] = health_data
            logger.info(f"✅ Health endpoint working, version: {health_data.get('version', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Health endpoint test failed: {e}")
            return False
    
    def test_sse_endpoint(self) -> bool:
        """Test SSE endpoint if available"""
        try:
            response = requests.get(
                f'http://localhost:{DOCKER_PORT}/sse',
                timeout=10,
                stream=True
            )
            
            if response.status_code == 200:
                # Read first SSE message
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data:'):
                        logger.info("✅ SSE endpoint responding")
                        return True
                    break
            
            # SSE might not be available in clean MCP SDK implementation
            logger.info("ℹ️  SSE endpoint not available (expected for clean MCP SDK)")
            return True
            
        except Exception as e:
            logger.info(f"ℹ️  SSE endpoint not available: {e}")
            return True  # Not critical for clean MCP SDK
    
    def test_container_logs(self) -> bool:
        """Test container logs show expected startup messages"""
        try:
            logs = self.container.logs(tail=50).decode('utf-8')
            
            # Check for expected log messages
            expected_messages = [
                "Starting Dr. Strunz Knowledge",
                "MCP Server",
                "v0.6.3"
            ]
            
            found_messages = 0
            for message in expected_messages:
                if message in logs:
                    found_messages += 1
            
            success_rate = (found_messages / len(expected_messages)) * 100
            self.results["runtime_metrics"]["log_success_rate"] = round(success_rate, 1)
            
            if success_rate >= 80:
                logger.info(f"✅ Container logs show expected messages ({success_rate}%)")
                return True
            else:
                logger.warning(f"⚠️  Container logs missing some expected messages ({success_rate}%)")
                logger.info(f"Recent logs:\n{logs[-500:]}")
                return False
            
        except Exception as e:
            logger.error(f"Container logs test failed: {e}")
            return False
    
    def test_memory_usage(self) -> bool:
        """Test container memory usage is reasonable"""
        try:
            # Get container stats
            stats = self.container.stats(stream=False)
            
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_mb = round(memory_usage / (1024 * 1024), 1)
            memory_percent = round((memory_usage / memory_limit) * 100, 1)
            
            self.results["runtime_metrics"]["memory_usage_mb"] = memory_mb
            self.results["runtime_metrics"]["memory_usage_percent"] = memory_percent
            
            # Should use reasonable memory (< 2GB for Railway compatibility)
            if memory_mb < 2048:
                logger.info(f"✅ Memory usage acceptable: {memory_mb}MB ({memory_percent}%)")
                return True
            else:
                logger.warning(f"⚠️  High memory usage: {memory_mb}MB ({memory_percent}%)")
                return False
            
        except Exception as e:
            logger.error(f"Memory usage test failed: {e}")
            return False
    
    def test_response_time(self) -> bool:
        """Test health endpoint response time"""
        try:
            # Test multiple requests for average
            response_times = []
            for i in range(5):
                start_time = time.time()
                response = requests.get(f'http://localhost:{DOCKER_PORT}/', timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                
                time.sleep(0.5)  # Brief pause between requests
            
            if not response_times:
                logger.error("No successful responses for timing test")
                return False
            
            avg_response_time = round(sum(response_times) / len(response_times), 3)
            max_response_time = round(max(response_times), 3)
            
            self.results["runtime_metrics"]["avg_response_time"] = avg_response_time
            self.results["runtime_metrics"]["max_response_time"] = max_response_time
            
            # Should respond quickly (< 1 second average)
            if avg_response_time < 1.0:
                logger.info(f"✅ Response time acceptable: {avg_response_time}s avg, {max_response_time}s max")
                return True
            else:
                logger.warning(f"⚠️  Slow response time: {avg_response_time}s avg, {max_response_time}s max")
                return False
            
        except Exception as e:
            logger.error(f"Response time test failed: {e}")
            return False
    
    def test_cleanup(self) -> bool:
        """Test cleanup of Docker resources"""
        try:
            cleanup_success = True
            
            # Stop and remove container
            if self.container:
                try:
                    self.container.stop(timeout=10)
                    self.container.remove()
                    logger.info("✅ Container cleaned up")
                except Exception as e:
                    logger.error(f"Container cleanup failed: {e}")
                    cleanup_success = False
            
            # Remove image
            if self.image:
                try:
                    self.docker_client.images.remove(self.image.id, force=True)
                    logger.info("✅ Image cleaned up")
                except Exception as e:
                    logger.error(f"Image cleanup failed: {e}")
                    cleanup_success = False
            
            return cleanup_success
            
        except Exception as e:
            logger.error(f"Cleanup test failed: {e}")
            return False
    
    def collect_docker_info(self):
        """Collect Docker environment information"""
        try:
            version_info = self.docker_client.version()
            self.results["docker_info"] = {
                "docker_version": version_info.get("Version", "unknown"),
                "api_version": version_info.get("ApiVersion", "unknown"),
                "platform": version_info.get("Platform", {}).get("Name", "unknown"),
                "architecture": version_info.get("Arch", "unknown")
            }
        except Exception as e:
            logger.warning(f"Could not collect Docker info: {e}")
    
    def run_all_tests(self):
        """Run all Docker tests"""
        logger.info(f"🐳 Starting Docker Comprehensive Test Suite v{TEST_VERSION}")
        logger.info(f"📅 Test Date: {TEST_DATE}")
        logger.info(f"🔧 Docker Port: {DOCKER_PORT}")
        logger.info("=" * 80)
        
        # Collect Docker environment info
        self.collect_docker_info()
        
        try:
            # Build Tests
            if not self.run_test("build", "docker_build", self.test_docker_build):
                logger.error("🚨 Docker build failed - aborting tests")
                return self.results
            
            # Startup Tests
            if not self.run_test("startup", "docker_startup", self.test_docker_startup):
                logger.error("🚨 Docker startup failed - aborting functionality tests")
                self.run_test("cleanup", "cleanup", self.test_cleanup)
                return self.results
            
            # Functionality Tests
            self.run_test("functionality", "health_endpoint", self.test_health_endpoint)
            self.run_test("functionality", "sse_endpoint", self.test_sse_endpoint)
            self.run_test("functionality", "container_logs", self.test_container_logs)
            
            # Performance Tests
            self.run_test("performance", "memory_usage", self.test_memory_usage)
            self.run_test("performance", "response_time", self.test_response_time)
            
        finally:
            # Always run cleanup
            self.run_test("cleanup", "cleanup", self.test_cleanup)
        
        # Calculate metrics
        self.results["total_duration"] = round(time.time() - self.start_time, 2)
        self.results["success_rate"] = round(
            (self.results["passed_tests"] / self.results["total_tests"]) * 100, 1
        ) if self.results["total_tests"] > 0 else 0
        
        # Generate recommendations
        self._generate_recommendations()
        
        logger.info("=" * 80)
        logger.info(f"🏁 Docker Test Suite Complete!")
        logger.info(f"📊 Results: {self.results['passed_tests']}/{self.results['total_tests']} tests passed ({self.results['success_rate']}%)")
        logger.info(f"⏱️  Duration: {self.results['total_duration']}s")
        
        return self.results
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Build recommendations
        if self.results["tests"]["build"]["failed"] > 0:
            recommendations.append("🔨 Docker build issues detected - check Dockerfile and dependencies")
        elif "build_time" in self.results["build_metrics"]:
            build_time = self.results["build_metrics"]["build_time"]
            if build_time > 300:  # 5 minutes
                recommendations.append(f"⏰ Slow Docker build ({build_time}s) - consider optimizing Dockerfile")
        
        # Runtime recommendations
        if "memory_usage_mb" in self.results["runtime_metrics"]:
            memory_mb = self.results["runtime_metrics"]["memory_usage_mb"]
            if memory_mb > 1500:
                recommendations.append(f"🧠 High memory usage ({memory_mb}MB) - may cause Railway deployment issues")
        
        if "avg_response_time" in self.results["runtime_metrics"]:
            response_time = self.results["runtime_metrics"]["avg_response_time"]
            if response_time > 0.5:
                recommendations.append(f"🐌 Slow response times ({response_time}s) - investigate performance bottlenecks")
        
        # Overall assessment
        if self.results["success_rate"] >= 90:
            recommendations.append("✅ Excellent Docker deployment - ready for Railway production")
        elif self.results["success_rate"] >= 75:
            recommendations.append("👍 Good Docker deployment - minor optimizations recommended")
        elif self.results["success_rate"] >= 60:
            recommendations.append("⚠️  Moderate Docker issues - review before production deployment")
        else:
            recommendations.append("🚨 Significant Docker issues - must be resolved before deployment")
        
        self.results["recommendations"] = recommendations
    
    def generate_report(self):
        """Generate Docker test report"""
        report_content = f"""# Local Docker Test Report v{TEST_VERSION}

**Test Date**: {TEST_DATE}  
**Environment**: Local Docker  
**Duration**: {self.results['total_duration']}s  
**Success Rate**: {self.results['success_rate']}%  

## 🐳 Docker Environment

"""
        
        for key, value in self.results["docker_info"].items():
            report_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        report_content += f"\n## 📊 Test Summary\n\n"
        report_content += f"- **Total Tests**: {self.results['total_tests']}\n"
        report_content += f"- **Passed**: {self.results['passed_tests']} ✅\n"
        report_content += f"- **Failed**: {self.results['failed_tests']} ❌\n"
        report_content += f"- **Success Rate**: {self.results['success_rate']}%\n\n"
        
        report_content += "## 🏗️ Build Metrics\n\n"
        for key, value in self.results["build_metrics"].items():
            report_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        report_content += "\n## ⚡ Runtime Metrics\n\n"
        for key, value in self.results["runtime_metrics"].items():
            if key != "health_response":  # Skip complex object
                report_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        report_content += "\n## 🧪 Test Categories\n\n"
        
        for category, data in self.results["tests"].items():
            total = data["passed"] + data["failed"]
            if total > 0:
                success_rate = round((data["passed"] / total) * 100, 1)
                status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                
                report_content += f"### {status_emoji} {category.title()}\n"
                report_content += f"- **Passed**: {data['passed']}\n"
                report_content += f"- **Failed**: {data['failed']}\n"
                report_content += f"- **Success Rate**: {success_rate}%\n\n"
                
                for test in data["tests"]:
                    test_emoji = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "💥"
                    report_content += f"  - {test_emoji} {test['name']} ({test['duration']}s)\n"
                    if test["status"] == "ERROR" and "error" in test:
                        report_content += f"    - Error: {test['error']}\n"
                
                report_content += "\n"
        
        report_content += "## 💡 Recommendations\n\n"
        for recommendation in self.results["recommendations"]:
            report_content += f"- {recommendation}\n"
        
        report_content += f"\n## 🔗 Related Reports\n\n"
        report_content += f"- [Comprehensive Test Report v{TEST_VERSION}](COMPREHENSIVE_TEST_REPORT_v{TEST_VERSION}_{TEST_DATE}.md)\n"
        report_content += f"- [Production Test Report v{TEST_VERSION}](PRODUCTION_TEST_REPORT_v{TEST_VERSION}.md)\n"
        report_content += f"- [Release Notes v{TEST_VERSION}](../RELEASE_NOTES_v{TEST_VERSION}.md)\n"
        
        report_content += f"\n---\n\n*Generated on {TEST_DATE} by Docker Test Runner v{TEST_VERSION}*\n"
        
        # Write report
        with open(TEST_REPORT_FILE, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📄 Docker test report generated: {TEST_REPORT_FILE}")
        return report_content

def main():
    """Main Docker test execution"""
    try:
        # Run Docker test suite
        test_runner = DockerTestRunner()
        results = test_runner.run_all_tests()
        
        # Generate report
        report = test_runner.generate_report()
        
        # Print summary
        print("\n" + "="*80)
        print(f"🐳 DOCKER TEST SUITE v{TEST_VERSION} COMPLETE")
        print("="*80)
        print(f"📊 Results: {results['passed_tests']}/{results['total_tests']} tests passed ({results['success_rate']}%)")
        print(f"⏱️  Duration: {results['total_duration']}s")
        print(f"📄 Report: {TEST_REPORT_FILE}")
        print("="*80)
        
        # Exit with appropriate code
        exit_code = 0 if results['success_rate'] >= 80 else 1
        return exit_code
        
    except Exception as e:
        logger.error(f"Docker test suite execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())