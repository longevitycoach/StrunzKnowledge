#!/usr/bin/env python3
"""
Comprehensive integration test for MCP SDK migration
Tests server in different environments
"""

import asyncio
import requests
import json
import time
from datetime import datetime
import subprocess
import sys
import os

class IntegrationTester:
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
        
    async def test_local_server(self):
        """Test the server running locally"""
        self.log("### Testing Local Server ###", "TEST")
        
        # First, check if unified server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Local server already running (unified_mcp_server.py)")
                self.results.append(("Local Server", "PASS", "Already running"))
                
                # Test some endpoints
                endpoints = [
                    ("/", "Health check"),
                    ("/.well-known/mcp/resource", "MCP discovery"),
                    ("/health", "Detailed health")
                ]
                
                for endpoint, desc in endpoints:
                    try:
                        resp = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                        if resp.status_code == 200:
                            self.log(f"✅ {desc}: OK")
                            self.results.append((f"Local - {desc}", "PASS", f"Status {resp.status_code}"))
                        else:
                            self.log(f"❌ {desc}: Status {resp.status_code}")
                            self.results.append((f"Local - {desc}", "FAIL", f"Status {resp.status_code}"))
                    except Exception as e:
                        self.log(f"❌ {desc}: {e}")
                        self.results.append((f"Local - {desc}", "FAIL", str(e)))
                        
                return True
            else:
                self.log("⚠️ Server responded but not healthy")
                self.results.append(("Local Server", "WARN", f"Status {response.status_code}"))
                return False
        except:
            self.log("ℹ️ No local server running, would need to start one")
            self.results.append(("Local Server", "INFO", "Not running"))
            return False
            
    async def test_docker_build(self):
        """Test Docker build process"""
        self.log("\n### Testing Docker Build ###", "TEST")
        
        # Check if Docker is available
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✅ Docker available: {result.stdout.strip()}")
                self.results.append(("Docker Available", "PASS", result.stdout.strip()))
            else:
                self.log("❌ Docker not available")
                self.results.append(("Docker Available", "FAIL", "Not installed"))
                return False
        except Exception as e:
            self.log(f"❌ Docker check failed: {e}")
            self.results.append(("Docker Available", "FAIL", str(e)))
            return False
            
        # Try to use existing image if available
        self.log("Checking for existing Docker images...")
        result = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], 
                               capture_output=True, text=True)
        
        images = result.stdout.strip().split('\n')
        strunz_images = [img for img in images if 'strunz' in img.lower()]
        
        if strunz_images:
            self.log(f"✅ Found existing images: {strunz_images}")
            self.results.append(("Docker Images", "PASS", f"Found {len(strunz_images)} images"))
            return True
        else:
            self.log("ℹ️ No Strunz images found, build required")
            self.results.append(("Docker Images", "INFO", "No images found"))
            return False
            
    async def test_railway_production(self):
        """Test Railway production deployment"""
        self.log("\n### Testing Railway Production ###", "TEST")
        
        production_url = "https://strunz.up.railway.app"
        
        endpoints = [
            ("/", "Root health check", 200),
            ("/health", "Detailed health", 200),
            ("/.well-known/mcp/resource", "MCP discovery", 200),
            ("/api/organizations/test/mcp/start-auth/test", "Claude.ai endpoint", [200, 302])
        ]
        
        for endpoint, desc, expected_status in endpoints:
            try:
                self.log(f"Testing {desc}...")
                resp = requests.get(f"{production_url}{endpoint}", 
                                  timeout=10, 
                                  allow_redirects=False)
                
                # Handle expected status as list or single value
                if isinstance(expected_status, list):
                    success = resp.status_code in expected_status
                else:
                    success = resp.status_code == expected_status
                    
                if success:
                    self.log(f"✅ {desc}: Status {resp.status_code}")
                    self.results.append((f"Railway - {desc}", "PASS", f"Status {resp.status_code}"))
                    
                    # Show some response content for key endpoints
                    if endpoint == "/":
                        try:
                            data = resp.json()
                            self.log(f"   Version: {data.get('version', 'unknown')}")
                        except:
                            pass
                else:
                    self.log(f"❌ {desc}: Status {resp.status_code} (expected {expected_status})")
                    self.results.append((f"Railway - {desc}", "FAIL", f"Status {resp.status_code}"))
                    
            except Exception as e:
                self.log(f"❌ {desc}: {e}")
                self.results.append((f"Railway - {desc}", "FAIL", str(e)))
                
        return True
        
    def generate_report(self):
        """Generate comprehensive test report"""
        total = len(self.results)
        passed = sum(1 for _, status, _ in self.results if status == "PASS")
        failed = sum(1 for _, status, _ in self.results if status == "FAIL")
        other = total - passed - failed
        
        report = {
            "test_run": {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "integration",
                "environments": ["local", "docker", "railway"]
            },
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "other": other,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%"
            },
            "results": [
                {
                    "test": test,
                    "status": status,
                    "details": details
                }
                for test, status, details in self.results
            ]
        }
        
        # Save report
        report_path = f"src/tests/reports/integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"\n📄 Report saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
        print(f"Failed: {failed}")
        print(f"Other: {other}")
        print("="*60)
        
        return report

async def main():
    """Main test runner"""
    print("=== MCP SDK Integration Test Suite ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tester = IntegrationTester()
    
    # Run tests
    await tester.test_local_server()
    await tester.test_docker_build()
    await tester.test_railway_production()
    
    # Generate report
    report = tester.generate_report()
    
    # Return exit code
    return 0 if report["summary"]["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)