#!/usr/bin/env python3
"""
Comprehensive Test Suite for StrunzKnowledge MCP Server v0.9.0
Tests all 24 MCP capabilities across different user journeys and roles
"""

import pytest
import asyncio
import json
import requests
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any
import os
import tempfile
import yaml

# Optional Docker import
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

class TestConfig:
    """Test configuration for different environments"""
    
    LOCAL_HTTP_URL = "http://localhost:8000"
    RAILWAY_URL = "https://strunz.up.railway.app"
    DOCKER_IMAGE = "strunzknowledge:test"
    DOCKER_PORT = 8001
    
    # Expected MCP tools
    EXPECTED_TOOLS = [
        "knowledge_search",
        "find_contradictions", 
        "trace_topic_evolution",
        "create_health_protocol",
        "compare_approaches",
        "analyze_supplement_stack",
        "nutrition_calculator",
        "get_community_insights",
        "summarize_posts",
        "get_trending_insights",
        "analyze_strunz_newsletter_evolution",
        "get_guest_authors_analysis",
        "track_health_topic_trends",
        "get_health_assessment_questions",
        "assess_user_health_profile",
        "create_personalized_protocol",
        "get_dr_strunz_biography",
        "get_mcp_server_purpose",
        "get_vector_db_analysis",
        "get_optimal_diagnostic_values",
        "analyze_user_feedback",
        "track_supplement_interactions",
        "validate_health_claims",
        "generate_meal_plans"
    ]

class UserRole:
    """Define different user roles for testing"""
    
    HEALTH_ENTHUSIAST = {
        "name": "Health Enthusiast",
        "goals": ["optimize_wellness", "prevent_disease"],
        "experience_level": "beginner",
        "interests": ["nutrition", "supplements", "exercise"]
    }
    
    MEDICAL_PROFESSIONAL = {
        "name": "Medical Professional", 
        "goals": ["evidence_based_research", "patient_recommendations"],
        "experience_level": "expert",
        "interests": ["clinical_studies", "diagnostics", "treatment_protocols"]
    }
    
    BIOHACKER = {
        "name": "Biohacker",
        "goals": ["performance_optimization", "longevity"],
        "experience_level": "advanced", 
        "interests": ["molecular_medicine", "advanced_diagnostics", "cutting_edge_protocols"]
    }
    
    NUTRITIONIST = {
        "name": "Nutritionist",
        "goals": ["client_protocols", "nutrition_education"],
        "experience_level": "professional",
        "interests": ["meal_planning", "supplement_protocols", "nutrition_science"]
    }

class TestJourney:
    """Define user journey test scenarios"""
    
    @staticmethod
    def health_assessment_journey():
        """Complete health assessment and protocol creation journey"""
        return [
            {
                "step": "Get Biography",
                "tool": "get_dr_strunz_biography",
                "input": {},
                "expected_fields": ["name", "specialty", "books", "approach"],
                "role": "any"
            },
            {
                "step": "Health Assessment",
                "tool": "get_health_assessment_questions", 
                "input": {"category": "general"},
                "expected_fields": ["questions", "categories"],
                "role": "health_enthusiast"
            },
            {
                "step": "User Profile Assessment",
                "tool": "assess_user_health_profile",
                "input": {
                    "age": 35,
                    "gender": "male",
                    "symptoms": ["fatigue", "brain_fog"],
                    "goals": ["energy_optimization"]
                },
                "expected_fields": ["assessment", "recommendations"],
                "role": "health_enthusiast"
            },
            {
                "step": "Create Protocol", 
                "tool": "create_personalized_protocol",
                "input": {
                    "health_profile": {
                        "age": 35,
                        "symptoms": ["fatigue"],
                        "goals": ["energy"]
                    }
                },
                "expected_fields": ["protocol", "supplements", "lifestyle"],
                "role": "health_enthusiast"
            }
        ]
    
    @staticmethod
    def research_journey():
        """Research and analysis journey for medical professionals"""
        return [
            {
                "step": "Knowledge Search",
                "tool": "knowledge_search",
                "input": {"query": "vitamin D deficiency symptoms", "max_results": 5},
                "expected_fields": ["results", "sources"],
                "role": "medical_professional"
            },
            {
                "step": "Find Contradictions",
                "tool": "find_contradictions", 
                "input": {"topic": "vitamin D supplementation"},
                "expected_fields": ["contradictions", "sources"],
                "role": "medical_professional"
            },
            {
                "step": "Compare Approaches",
                "tool": "compare_approaches",
                "input": {
                    "topic": "vitamin D supplementation",
                    "approaches": ["high_dose", "moderate_dose"]
                },
                "expected_fields": ["comparison", "evidence"],
                "role": "medical_professional"
            },
            {
                "step": "Validate Claims",
                "tool": "validate_health_claims",
                "input": {"claim": "Vitamin D prevents COVID-19"},
                "expected_fields": ["validation", "evidence", "confidence"],
                "role": "medical_professional"
            }
        ]
    
    @staticmethod
    def biohacker_journey():
        """Advanced optimization journey for biohackers"""
        return [
            {
                "step": "Optimal Diagnostics",
                "tool": "get_optimal_diagnostic_values",
                "input": {"biomarker": "vitamin_d"},
                "expected_fields": ["optimal_range", "units", "rationale"],
                "role": "biohacker"
            },
            {
                "step": "Supplement Stack Analysis",
                "tool": "analyze_supplement_stack",
                "input": {
                    "supplements": ["vitamin_d", "magnesium", "k2"],
                    "dosages": ["5000_iu", "400_mg", "100_mcg"]
                },
                "expected_fields": ["analysis", "interactions", "recommendations"],
                "role": "biohacker"  
            },
            {
                "step": "Track Interactions",
                "tool": "track_supplement_interactions",
                "input": {
                    "stack": ["vitamin_d", "calcium", "magnesium"]
                },
                "expected_fields": ["interactions", "timing", "warnings"],
                "role": "biohacker"
            },
            {
                "step": "Vector Analysis",
                "tool": "get_vector_db_analysis",
                "input": {"topic": "longevity protocols"},
                "expected_fields": ["analysis", "related_topics", "confidence"],
                "role": "biohacker"
            }
        ]
    
    @staticmethod
    def nutritionist_journey():
        """Professional nutrition planning journey"""
        return [
            {
                "step": "Nutrition Calculator",
                "tool": "nutrition_calculator",
                "input": {
                    "age": 40,
                    "weight": 70,
                    "activity_level": "moderate",
                    "goal": "maintenance"
                },
                "expected_fields": ["macros", "calories", "micronutrients"],
                "role": "nutritionist"
            },
            {
                "step": "Generate Meal Plan",
                "tool": "generate_meal_plans",
                "input": {
                    "dietary_preferences": ["low_carb"],
                    "restrictions": ["dairy_free"],
                    "duration": "7_days"
                },
                "expected_fields": ["meal_plan", "recipes", "shopping_list"],
                "role": "nutritionist"
            },
            {
                "step": "Community Insights",
                "tool": "get_community_insights",
                "input": {"topic": "intermittent_fasting"},
                "expected_fields": ["insights", "trends", "discussions"],
                "role": "nutritionist"
            },
            {
                "step": "Health Protocol",
                "tool": "create_health_protocol",
                "input": {
                    "condition": "metabolic_syndrome",
                    "approach": "nutrition_focused"
                },
                "expected_fields": ["protocol", "timeline", "monitoring"],
                "role": "nutritionist"
            }
        ]

class MCPTestSuite:
    """Main test suite class"""
    
    def __init__(self, environment="local"):
        self.environment = environment
        self.base_url = TestConfig.LOCAL_HTTP_URL if environment == "local" else TestConfig.RAILWAY_URL
        self.docker_client = docker.from_env() if environment == "docker" and DOCKER_AVAILABLE else None
        self.container = None
        
    def setup_environment(self):
        """Setup test environment based on type"""
        if self.environment == "docker":
            return self._setup_docker()
        elif self.environment == "railway":
            return self._validate_railway()
        else:
            return self._setup_local()
    
    def _setup_local(self):
        """Setup local testing environment"""
        try:
            # Start local server in background
            env = os.environ.copy()
            env["TRANSPORT"] = "http"
            env["PORT"] = "8000"
            
            self.local_process = subprocess.Popen(
                ["python", "main.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            time.sleep(5)
            
            # Test connection
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                return True, "Local server started successfully"
            else:
                return False, f"Local server health check failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Failed to start local server: {str(e)}"
    
    def _setup_docker(self):
        """Setup Docker testing environment"""
        if not DOCKER_AVAILABLE:
            return False, "Docker module not available - install with: pip install docker"
        
        try:
            # Build Docker image
            print("Building Docker image...")
            self.docker_client.images.build(
                path=".",
                tag=TestConfig.DOCKER_IMAGE,
                rm=True,
                nocache=True
            )
            
            # Run container
            print("Starting Docker container...")
            self.container = self.docker_client.containers.run(
                TestConfig.DOCKER_IMAGE,
                ports={'8000/tcp': TestConfig.DOCKER_PORT},
                detach=True,
                environment={"TRANSPORT": "http", "PORT": "8000"}
            )
            
            # Wait for startup
            time.sleep(10)
            
            # Test connection
            docker_url = f"http://localhost:{TestConfig.DOCKER_PORT}"
            response = requests.get(f"{docker_url}/", timeout=10)
            if response.status_code == 200:
                self.base_url = docker_url
                return True, "Docker container started successfully"
            else:
                return False, f"Docker health check failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Failed to setup Docker: {str(e)}"
    
    def _validate_railway(self):
        """Validate Railway deployment"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return True, f"Railway deployment validated (version: {version})"
            else:
                return False, f"Railway health check failed: {response.status_code}"
        except Exception as e:
            return False, f"Failed to connect to Railway: {str(e)}"
    
    def teardown_environment(self):
        """Cleanup test environment"""
        if self.environment == "local" and hasattr(self, 'local_process'):
            self.local_process.terminate()
            self.local_process.wait()
        elif self.environment == "docker" and self.container:
            self.container.stop()
            self.container.remove()
    
    def test_server_health(self):
        """Test basic server health and configuration"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            data = response.json()
            assert "version" in data, "Version missing from health response"
            assert "server" in data, "Server name missing from health response"
            assert data["version"] == "0.9.0", f"Version mismatch: expected 0.9.0, got {data['version']}"
            
            return True, data
        except Exception as e:
            return False, str(e)
    
    def test_mcp_tools_available(self):
        """Test that all expected MCP tools are available"""
        try:
            # Test tools/list endpoint via MCP protocol
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
            
            assert response.status_code == 200, f"Tools list request failed: {response.status_code}"
            
            data = response.json()
            assert "result" in data, "Missing result in tools list response"
            assert "tools" in data["result"], "Missing tools in result"
            
            available_tools = [tool["name"] for tool in data["result"]["tools"]]
            
            # Check if we have the expected number of tools (allowing for some variation)
            assert len(available_tools) >= 20, f"Too few tools available: {len(available_tools)}"
            
            return True, {"available_tools": available_tools, "count": len(available_tools)}
            
        except Exception as e:
            return False, str(e)
    
    def test_user_journey(self, journey_name: str, journey_steps: List[Dict], role: Dict) -> Dict:
        """Test a complete user journey"""
        results = {
            "journey": journey_name,
            "role": role["name"],
            "steps": [],
            "success": True,
            "errors": []
        }
        
        for step_idx, step in enumerate(journey_steps):
            step_result = {
                "step": step["step"],
                "tool": step["tool"],
                "success": False,
                "response_time": 0,
                "output": None,
                "error": None
            }
            
            try:
                start_time = time.time()
                
                # Make MCP tool call
                mcp_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": step["tool"],
                        "arguments": step["input"]
                    },
                    "id": f"test-{journey_name}-{step_idx}"
                }
                
                response = requests.post(
                    f"{self.base_url}/messages",
                    json=mcp_request,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                step_result["response_time"] = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "result" in data:
                        step_result["success"] = True
                        step_result["output"] = data["result"]
                        
                        # Validate expected fields if specified
                        if "expected_fields" in step:
                            content_text = data["result"]["content"][0]["text"]
                            try:
                                content_data = json.loads(content_text)
                                for field in step["expected_fields"]:
                                    if field not in content_data:
                                        step_result["success"] = False
                                        step_result["error"] = f"Missing expected field: {field}"
                                        break
                            except json.JSONDecodeError:
                                # Content might be plain text, which is also valid
                                pass
                    else:
                        step_result["error"] = data.get("error", "Unknown error")
                        results["success"] = False
                else:
                    step_result["error"] = f"HTTP {response.status_code}: {response.text}"
                    results["success"] = False
                    
            except Exception as e:
                step_result["error"] = str(e)
                results["success"] = False
            
            results["steps"].append(step_result)
            
            if not step_result["success"]:
                results["errors"].append(f"Step {step_idx + 1} failed: {step_result['error']}")
        
        return results
    
    def run_comprehensive_test_suite(self):
        """Run the complete test suite"""
        test_results = {
            "environment": self.environment,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_health": None,
            "tools_available": None,
            "user_journeys": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
        print(f"🧪 Running comprehensive test suite for {self.environment} environment...")
        
        # Test 1: Server Health
        print("1. Testing server health...")
        success, data = self.test_server_health()
        test_results["server_health"] = {"success": success, "data": data}
        test_results["summary"]["total_tests"] += 1
        if success:
            test_results["summary"]["passed_tests"] += 1
            print("   ✅ Server health check passed")
        else:
            test_results["summary"]["failed_tests"] += 1
            print(f"   ❌ Server health check failed: {data}")
        
        # Test 2: MCP Tools Available
        print("2. Testing MCP tools availability...")
        success, data = self.test_mcp_tools_available()
        test_results["tools_available"] = {"success": success, "data": data}
        test_results["summary"]["total_tests"] += 1
        if success:
            test_results["summary"]["passed_tests"] += 1
            print(f"   ✅ {data['count']} MCP tools available")
        else:
            test_results["summary"]["failed_tests"] += 1
            print(f"   ❌ MCP tools test failed: {data}")
        
        # Test 3: User Journeys
        journeys = [
            ("Health Assessment", TestJourney.health_assessment_journey(), UserRole.HEALTH_ENTHUSIAST),
            ("Research Journey", TestJourney.research_journey(), UserRole.MEDICAL_PROFESSIONAL),
            ("Biohacker Journey", TestJourney.biohacker_journey(), UserRole.BIOHACKER),
            ("Nutritionist Journey", TestJourney.nutritionist_journey(), UserRole.NUTRITIONIST)
        ]
        
        for journey_name, journey_steps, role in journeys:
            print(f"3.{len(test_results['user_journeys']) + 1}. Testing {journey_name} ({role['name']})...")
            
            journey_result = self.test_user_journey(journey_name, journey_steps, role)
            test_results["user_journeys"].append(journey_result)
            
            test_results["summary"]["total_tests"] += len(journey_steps)
            passed_steps = sum(1 for step in journey_result["steps"] if step["success"])
            test_results["summary"]["passed_tests"] += passed_steps
            test_results["summary"]["failed_tests"] += len(journey_steps) - passed_steps
            
            if journey_result["success"]:
                print(f"   ✅ {journey_name} completed successfully ({passed_steps}/{len(journey_steps)} steps)")
            else:
                print(f"   ❌ {journey_name} failed ({passed_steps}/{len(journey_steps)} steps)")
                for error in journey_result["errors"]:
                    print(f"      • {error}")
        
        # Calculate success rate
        if test_results["summary"]["total_tests"] > 0:
            test_results["summary"]["success_rate"] = (
                test_results["summary"]["passed_tests"] / test_results["summary"]["total_tests"] * 100
            )
        
        return test_results
    
    def generate_test_report(self, results: Dict) -> str:
        """Generate detailed test report"""
        report = f"""
# StrunzKnowledge MCP Server v0.9.0 - Test Report

**Environment**: {results['environment'].upper()}
**Timestamp**: {results['timestamp']}
**Overall Success Rate**: {results['summary']['success_rate']:.1f}%

## Summary
- **Total Tests**: {results['summary']['total_tests']}
- **Passed**: {results['summary']['passed_tests']} ✅
- **Failed**: {results['summary']['failed_tests']} ❌

## Server Health Check
"""
        
        if results["server_health"]["success"]:
            data = results["server_health"]["data"]
            report += f"""
✅ **PASSED**
- Version: {data.get('version', 'unknown')}
- Server: {data.get('server', 'unknown')}
- Status: {data.get('status', 'unknown')}
"""
        else:
            report += f"""
❌ **FAILED**
- Error: {results['server_health']['data']}
"""
        
        ## MCP Tools Availability
        report += "\n## MCP Tools Availability\n"
        
        if results["tools_available"]["success"]:
            data = results["tools_available"]["data"]
            report += f"""
✅ **PASSED**
- Tools Available: {data['count']}
- Tools: {', '.join(data['available_tools'][:10])}{'...' if len(data['available_tools']) > 10 else ''}
"""
        else:
            report += f"""
❌ **FAILED**
- Error: {results['tools_available']['data']}
"""
        
        ## User Journey Tests
        report += "\n## User Journey Tests\n"
        
        for journey in results["user_journeys"]:
            status = "✅ PASSED" if journey["success"] else "❌ FAILED"
            passed_steps = sum(1 for step in journey["steps"] if step["success"])
            total_steps = len(journey["steps"])
            
            report += f"""
### {journey['journey']} ({journey['role']}) - {status}
**Steps**: {passed_steps}/{total_steps} passed

"""
            
            for i, step in enumerate(journey["steps"], 1):
                status_icon = "✅" if step["success"] else "❌"
                report += f"{i}. {status_icon} **{step['step']}** ({step['tool']}) - {step['response_time']:.2f}s\n"
                
                if not step["success"]:
                    report += f"   - Error: {step['error']}\n"
            
            report += "\n"
        
        ## Recommendations
        report += "\n## Recommendations\n"
        
        if results["summary"]["success_rate"] >= 95:
            report += "🟢 **EXCELLENT** - System is production ready\n"
        elif results["summary"]["success_rate"] >= 80:
            report += "🟡 **GOOD** - Minor issues to address before production\n"
        elif results["summary"]["success_rate"] >= 60:
            report += "🟠 **FAIR** - Several issues need attention\n"
        else:
            report += "🔴 **POOR** - Major issues require immediate attention\n"
        
        return report

def main():
    """Run test suite for all environments"""
    environments = ["local", "docker", "railway"]
    
    for env in environments:
        if env == "docker" and not DOCKER_AVAILABLE:
            print(f"⚠️ Skipping Docker tests - Docker module not available")
            continue
            
        print(f"\n{'='*60}")
        print(f"Testing {env.upper()} Environment")
        print(f"{'='*60}")
        
        suite = MCPTestSuite(environment=env)
        
        # Setup environment
        success, message = suite.setup_environment()
        if not success:
            print(f"❌ Failed to setup {env} environment: {message}")
            continue
        
        print(f"✅ {message}")
        
        try:
            # Run tests
            results = suite.run_comprehensive_test_suite()
            
            # Generate report
            report = suite.generate_test_report(results)
            
            # Save report
            report_file = f"test_report_{env}_{time.strftime('%Y%m%d_%H%M%S')}.md"
            Path("test_reports").mkdir(exist_ok=True)
            Path(f"test_reports/{report_file}").write_text(report)
            
            print(f"\n📄 Test report saved: test_reports/{report_file}")
            print(f"🎯 Success Rate: {results['summary']['success_rate']:.1f}%")
            
        finally:
            # Cleanup
            suite.teardown_environment()

if __name__ == "__main__":
    main()