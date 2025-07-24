#!/usr/bin/env python3
"""
QA Deployment Validation Script
Validates deployment readiness and environment parity
"""

import requests
import json
import os
import sys
import subprocess
from pathlib import Path

class QADeploymentValidator:
    def __init__(self):
        self.local_version = "0.9.0"
        self.production_url = "https://strunz.up.railway.app"
        self.results = {
            "local_tests": {},
            "production_tests": {},
            "parity_tests": {},
            "critical_issues": [],
            "warnings": []
        }
    
    def validate_local_environment(self):
        """Validate local environment readiness"""
        print("🔍 Validating Local Environment...")
        
        # Check unified main.py exists
        main_py = Path("main.py")
        if main_py.exists():
            self.results["local_tests"]["main_py_exists"] = "✅ PASS"
        else:
            self.results["local_tests"]["main_py_exists"] = "❌ FAIL"
            self.results["critical_issues"].append("main.py missing")
        
        # Check unified requirements exists
        req_unified = Path("requirements-unified.txt")
        if req_unified.exists():
            self.results["local_tests"]["unified_requirements_exists"] = "✅ PASS"
        else:
            self.results["local_tests"]["unified_requirements_exists"] = "❌ FAIL"
            self.results["critical_issues"].append("requirements-unified.txt missing")
        
        # Check old requirements files removed
        old_req_files = ["requirements.txt", "requirements-prod.txt", "requirements-flexible.txt"]
        removed_count = 0
        for req_file in old_req_files:
            if not Path(req_file).exists():
                removed_count += 1
        
        if removed_count == len(old_req_files):
            self.results["local_tests"]["old_requirements_removed"] = "✅ PASS"
        else:
            self.results["local_tests"]["old_requirements_removed"] = "⚠️ WARN"
            self.results["warnings"].append(f"Only {removed_count}/{len(old_req_files)} old requirements files removed")
        
        # Check railway-deploy.py updated
        railway_deploy = Path("railway-deploy.py")
        if railway_deploy.exists():
            content = railway_deploy.read_text()
            if "from main import main" in content:
                self.results["local_tests"]["railway_deploy_updated"] = "✅ PASS"
            else:
                self.results["local_tests"]["railway_deploy_updated"] = "❌ FAIL"
                self.results["critical_issues"].append("railway-deploy.py not updated to use unified main.py")
        
        # Check Dockerfile updated
        dockerfile = Path("Dockerfile")
        if dockerfile.exists():
            content = dockerfile.read_text()
            if "requirements-unified.txt" in content:
                self.results["local_tests"]["dockerfile_updated"] = "✅ PASS"
            else:
                self.results["local_tests"]["dockerfile_updated"] = "❌ FAIL"
                self.results["critical_issues"].append("Dockerfile not updated to use unified requirements")
    
    def validate_production_environment(self):
        """Validate production environment"""
        print("🌐 Validating Production Environment...")
        
        try:
            # Test production health endpoint
            response = requests.get(f"{self.production_url}/", timeout=10)
            if response.status_code == 200:
                self.results["production_tests"]["health_endpoint"] = "✅ PASS"
                
                # Check version
                data = response.json()
                prod_version = data.get("version", "unknown")
                
                if prod_version == self.local_version:
                    self.results["production_tests"]["version_match"] = "✅ PASS"
                else:
                    self.results["production_tests"]["version_match"] = "❌ FAIL"
                    self.results["critical_issues"].append(f"Version mismatch: Production {prod_version} vs Local {self.local_version}")
                
                # Check server name
                server_name = data.get("server", "unknown")
                if "Dr. Strunz Knowledge MCP Server" in server_name:
                    self.results["production_tests"]["server_name"] = "✅ PASS"
                else:
                    self.results["production_tests"]["server_name"] = "⚠️ WARN"
                    self.results["warnings"].append(f"Unexpected server name: {server_name}")
                
            else:
                self.results["production_tests"]["health_endpoint"] = "❌ FAIL"
                self.results["critical_issues"].append(f"Production health check failed: {response.status_code}")
        
        except Exception as e:
            self.results["production_tests"]["health_endpoint"] = "❌ FAIL"
            self.results["critical_issues"].append(f"Production connection failed: {str(e)}")
        
        # Test SSE endpoint
        try:
            response = requests.get(f"{self.production_url}/sse", timeout=5, stream=True)
            if response.status_code == 200:
                self.results["production_tests"]["sse_endpoint"] = "✅ PASS"
            else:
                self.results["production_tests"]["sse_endpoint"] = "❌ FAIL"
                self.results["critical_issues"].append(f"SSE endpoint failed: {response.status_code}")
        except Exception as e:
            self.results["production_tests"]["sse_endpoint"] = "❌ FAIL"
            self.results["warnings"].append(f"SSE endpoint test failed: {str(e)}")
        
        # Test OAuth endpoints
        try:
            response = requests.get(f"{self.production_url}/.well-known/oauth-authorization-server", timeout=5)
            if response.status_code == 200:
                self.results["production_tests"]["oauth_endpoints"] = "✅ PASS"
            else:
                self.results["production_tests"]["oauth_endpoints"] = "❌ FAIL"
                self.results["warnings"].append(f"OAuth discovery failed: {response.status_code}")
        except Exception as e:
            self.results["production_tests"]["oauth_endpoints"] = "❌ FAIL"
            self.results["warnings"].append(f"OAuth endpoint test failed: {str(e)}")
    
    def validate_environment_parity(self):
        """Check for environment parity issues"""
        print("⚖️ Validating Environment Parity...")
        
        # Check railway.toml configuration
        railway_toml = Path("railway.toml")
        if railway_toml.exists():
            content = railway_toml.read_text()
            
            # Check start command
            if "python railway-deploy.py" in content:
                self.results["parity_tests"]["start_command"] = "✅ PASS"
            else:
                self.results["parity_tests"]["start_command"] = "⚠️ WARN"
                self.results["warnings"].append("railway.toml start command may be outdated")
            
            # Check health check path
            if 'healthcheckPath = "/"' in content:
                self.results["parity_tests"]["health_check_path"] = "✅ PASS"
            else:
                self.results["parity_tests"]["health_check_path"] = "⚠️ WARN"
                self.results["warnings"].append("Health check path configuration unclear")
        
        # Check for legacy files that should be removed
        legacy_files = [
            "src/mcp/unified_mcp_server.py",
            "src/mcp/enhanced_server.py"
        ]
        
        legacy_found = []
        for legacy_file in legacy_files:
            if Path(legacy_file).exists():
                legacy_found.append(legacy_file)
        
        if not legacy_found:
            self.results["parity_tests"]["legacy_files_removed"] = "✅ PASS"
        else:
            self.results["parity_tests"]["legacy_files_removed"] = "⚠️ WARN"
            self.results["warnings"].append(f"Legacy files still present: {legacy_found}")
    
    def test_local_server_startup(self):
        """Test local server can start successfully"""
        print("🚀 Testing Local Server Startup...")
        
        # Test HTTP transport
        try:
            env = os.environ.copy()
            env["TRANSPORT"] = "http"
            env["PORT"] = "9999"  # Use different port to avoid conflicts
            
            # Start server in background for a few seconds to test startup
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for startup
            import time
            time.sleep(3)
            
            # Test if server responds
            try:
                response = requests.get("http://localhost:9999/", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("version") == self.local_version:
                        self.results["local_tests"]["http_server_startup"] = "✅ PASS"
                    else:
                        self.results["local_tests"]["http_server_startup"] = "⚠️ WARN"
                        self.results["warnings"].append(f"Local server version mismatch: {data.get('version')}")
                else:
                    self.results["local_tests"]["http_server_startup"] = "❌ FAIL"
                    self.results["critical_issues"].append("Local HTTP server not responding correctly")
            except:
                self.results["local_tests"]["http_server_startup"] = "❌ FAIL"
                self.results["critical_issues"].append("Local HTTP server failed to respond")
            
            # Clean up
            process.terminate()
            process.wait(timeout=5)
            
        except Exception as e:
            self.results["local_tests"]["http_server_startup"] = "❌ FAIL"
            self.results["critical_issues"].append(f"Local server startup test failed: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("🧪 QA DEPLOYMENT VALIDATION REPORT")
        print("="*80)
        
        # Summary
        total_tests = len(self.results["local_tests"]) + len(self.results["production_tests"]) + len(self.results["parity_tests"])
        passed_tests = sum(1 for tests in [self.results["local_tests"], self.results["production_tests"], self.results["parity_tests"]] 
                          for result in tests.values() if "✅" in result)
        
        print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        print(f"🚨 Critical Issues: {len(self.results['critical_issues'])}")
        print(f"⚠️ Warnings: {len(self.results['warnings'])}")
        
        # Local Tests
        print(f"\n🏠 LOCAL ENVIRONMENT TESTS:")
        for test, result in self.results["local_tests"].items():
            print(f"  {result} {test}")
        
        # Production Tests
        print(f"\n🌐 PRODUCTION ENVIRONMENT TESTS:")
        for test, result in self.results["production_tests"].items():
            print(f"  {result} {test}")
        
        # Parity Tests
        print(f"\n⚖️ ENVIRONMENT PARITY TESTS:")
        for test, result in self.results["parity_tests"].items():
            print(f"  {result} {test}")
        
        # Critical Issues
        if self.results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES (MUST FIX BEFORE DEPLOYMENT):")
            for issue in self.results["critical_issues"]:
                print(f"  ❌ {issue}")
        
        # Warnings
        if self.results["warnings"]:
            print(f"\n⚠️ WARNINGS (SHOULD INVESTIGATE):")
            for warning in self.results["warnings"]:
                print(f"  ⚠️ {warning}")
        
        # Deployment Recommendation
        print(f"\n🎯 DEPLOYMENT RECOMMENDATION:")
        if self.results["critical_issues"]:
            print("  ❌ NOT READY FOR DEPLOYMENT - Fix critical issues first")
            return False
        elif len(self.results["warnings"]) > 3:
            print("  ⚠️ PROCEED WITH CAUTION - Many warnings present")
            return True
        else:
            print("  ✅ READY FOR DEPLOYMENT")
            return True

def main():
    validator = QADeploymentValidator()
    
    # Run all validations
    validator.validate_local_environment()
    validator.validate_production_environment()
    validator.validate_environment_parity()
    validator.test_local_server_startup()
    
    # Generate report
    deployment_ready = validator.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if deployment_ready else 1)

if __name__ == "__main__":
    main()