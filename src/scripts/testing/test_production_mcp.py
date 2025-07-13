#!/usr/bin/env python3
"""
Production MCP Test Suite
Tests the deployed MCP server on Railway with proper datetime naming
"""
import asyncio
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import httpx

@dataclass
class TestCase:
    """Test case for MCP tool"""
    id: str
    tool_name: str
    description: str
    params: Dict[str, Any]
    expected_fields: List[str] = field(default_factory=list)
    category: str = "general"
    user_role: Optional[str] = None

@dataclass 
class TestResult:
    """Test execution result"""
    test_id: str
    tool_name: str
    params: Dict[str, Any]
    result: Any
    duration_ms: float
    success: bool
    error: Optional[str] = None
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)

class ProductionMCPTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = f"prod_test_{int(time.time())}"
        self.results: List[TestResult] = []
        
    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool using JSON-RPC protocol"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": f"{self.session_id}_{len(self.results)+1}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": {
                            "code": response.status_code,
                            "message": response.text
                        }
                    }
            except Exception as e:
                return {
                    "error": {
                        "code": -1,
                        "message": str(e)
                    }
                }
    
    def generate_comprehensive_test_cases(self) -> List[TestCase]:
        """Generate comprehensive test cases for production testing"""
        test_cases = []
        
        # 1. Core functionality tests
        test_cases.extend([
            TestCase(
                id="biography_test",
                tool_name="get_dr_strunz_biography",
                description="Get Dr. Strunz biography",
                params={},
                expected_fields=["full_name", "title", "medical_education"],
                category="info"
            ),
            TestCase(
                id="server_purpose_test", 
                tool_name="get_mcp_server_purpose",
                description="Get MCP server purpose",
                params={},
                expected_fields=["title", "primary_purpose", "key_capabilities"],
                category="info"
            ),
            TestCase(
                id="vector_db_test",
                tool_name="get_vector_db_analysis", 
                description="Get vector database analysis",
                params={},
                expected_fields=["database_overview", "content_distribution"],
                category="info"
            )
        ])
        
        # 2. Search functionality
        test_cases.extend([
            TestCase(
                id="search_vitamin_d",
                tool_name="knowledge_search",
                description="Search for Vitamin D information",
                params={"query": "Vitamin D Mangel", "filters": {"sources": ["books"]}},
                expected_fields=["query", "results"],
                category="search"
            ),
            TestCase(
                id="search_magnesium",
                tool_name="knowledge_search", 
                description="Search for magnesium deficiency",
                params={"query": "Magnesium deficiency symptoms", "filters": {"sources": ["news", "forum"]}},
                expected_fields=["query", "results"],
                category="search"
            ),
            TestCase(
                id="search_amino_acids",
                tool_name="knowledge_search",
                description="Search for amino acids for athletes", 
                params={"query": "Amino acids for athletes", "filters": {"sources": ["books"]}},
                expected_fields=["query", "results"],
                category="search"
            )
        ])
        
        # 3. Health protocol generation
        test_cases.extend([
            TestCase(
                id="protocol_diabetes",
                tool_name="create_health_protocol",
                description="Create protocol for diabetes",
                params={
                    "condition": "type 2 diabetes",
                    "user_profile": {
                        "age": 45,
                        "gender": "male", 
                        "symptoms": ["fatigue", "high_blood_sugar"]
                    }
                },
                expected_fields=["condition", "recommendations", "supplements"],
                category="protocol"
            ),
            TestCase(
                id="protocol_hypertension",
                tool_name="create_health_protocol",
                description="Create protocol for hypertension",
                params={
                    "condition": "hypertension", 
                    "user_profile": {
                        "age": 55,
                        "gender": "female",
                        "symptoms": ["high_blood_pressure", "stress"]
                    }
                },
                expected_fields=["condition", "recommendations", "supplements"],
                category="protocol"
            )
        ])
        
        # 4. Advanced analysis tools
        test_cases.extend([
            TestCase(
                id="supplement_analysis",
                tool_name="analyze_supplement_stack",
                description="Analyze supplement combination",
                params={
                    "supplements": ["Vitamin D3", "Magnesium", "Omega-3"],
                    "health_goals": ["immune_support", "heart_health"]
                },
                expected_fields=["supplements", "analysis"],
                category="analysis"
            ),
            TestCase(
                id="topic_evolution",
                tool_name="trace_topic_evolution",
                description="Trace Vitamin D topic evolution",
                params={
                    "concept": "Vitamin D",
                    "start_date": "2010-01-01", 
                    "end_date": "2025-01-01"
                },
                expected_fields=["topic", "timeline"],
                category="analysis"
            )
        ])
        
        # 5. User profiling and assessment
        test_cases.extend([
            TestCase(
                id="assessment_questions",
                tool_name="get_health_assessment_questions",
                description="Get health assessment questions",
                params={"section": "basic_info"},
                expected_fields=["section", "questions"],
                category="assessment"
            ),
            TestCase(
                id="user_profile_assessment",
                tool_name="assess_user_health_profile",
                description="Assess user health profile",
                params={
                    "assessment_responses": {
                        "age": 35,
                        "gender": "female",
                        "current_health": "good",
                        "goals": ["weight_loss", "energy_increase"],
                        "experience": "intermediate"
                    }
                },
                expected_fields=["profile", "assigned_role", "journey_plan"],
                category="assessment"
            )
        ])
        
        return test_cases
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            result = await self.call_mcp_tool(test_case.tool_name, test_case.params)
            duration_ms = (time.time() - start_time) * 1000
            
            # Check for errors
            if "error" in result:
                return TestResult(
                    test_id=test_case.id,
                    tool_name=test_case.tool_name,
                    params=test_case.params,
                    result=result,
                    duration_ms=duration_ms,
                    success=False,
                    error=result["error"].get("message", "Unknown error"),
                    validation_passed=False
                )
            
            # Validate expected fields
            validation_errors = []
            validation_passed = True
            
            if test_case.expected_fields and "result" in result:
                for field in test_case.expected_fields:
                    if field not in result["result"]:
                        validation_errors.append(f"Missing field: {field}")
                        validation_passed = False
            
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result=result,
                duration_ms=duration_ms,
                success=True,
                validation_passed=validation_passed,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result={"error": str(e)},
                duration_ms=duration_ms,
                success=False,
                error=str(e),
                validation_passed=False
            )
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 Production MCP Test Suite")
        print(f"📍 Target: {self.base_url}")
        print("=" * 80)
        
        # Check server health
        print("🔍 Checking MCP server...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    print("✅ Server is running")
                else:
                    print(f"❌ Server health check failed: {response.status_code}")
                    return {"error": "Server not healthy"}
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return {"error": f"Connection failed: {e}"}
        
        # Generate test cases
        test_cases = self.generate_comprehensive_test_cases()
        print(f"\n🚀 Running {len(test_cases)} comprehensive test cases")
        print("=" * 80)
        
        # Run tests by category
        categories = {}
        for test_case in test_cases:
            if test_case.category not in categories:
                categories[test_case.category] = []
            categories[test_case.category].append(test_case)
        
        all_results = []
        
        for category, tests in categories.items():
            print(f"\n📂 {category.upper()} ({len(tests)} tests)")
            print("-" * 60)
            
            for i, test_case in enumerate(tests, 1):
                result = await self.run_test_case(test_case)
                all_results.append(result)
                
                status = "✅" if result.success else "❌"
                validation = "✅" if result.validation_passed else "⚠️"
                
                print(f"  [{i}/{len(tests)}] {test_case.description}... {status} {validation} ({result.duration_ms:.1f}ms)")
                
                if not result.success and result.error:
                    print(f"    Error: {result.error}")
        
        self.results = all_results
        
        # Generate summary
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        validated_tests = sum(1 for r in all_results if r.validation_passed)
        total_duration = sum(r.duration_ms for r in all_results)
        
        print(f"\n✅ Testing completed in {total_duration/1000:.2f}s")
        print(f"📊 Summary: {successful_tests}/{total_tests} passed, {validated_tests} fully validated")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "validated_tests": validated_tests,
            "total_duration_ms": total_duration,
            "average_response_ms": total_duration / total_tests if total_tests > 0 else 0,
            "results": all_results
        }
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate detailed test report"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = f"""# Production MCP Server Test Report - {timestamp}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Server**: {self.base_url}
**Total Tests**: {summary['total_tests']}

## Executive Summary
- **Tests Executed**: {summary['total_tests']}
- **Successful**: {summary['successful_tests']} ({summary['successful_tests']/summary['total_tests']*100:.1f}%)
- **Fully Validated**: {summary['validated_tests']} ({summary['validated_tests']/summary['total_tests']*100:.1f}%)
- **Failed**: {summary['total_tests'] - summary['successful_tests']}
- **Total Duration**: {summary['total_duration_ms']/1000:.2f}s
- **Average Response**: {summary['average_response_ms']:.1f}ms

## Test Results by Category

"""
        
        # Group results by category
        categories = {}
        for result in self.results:
            # Find the test case to get category
            test_case = None
            for tc in self.generate_comprehensive_test_cases():
                if tc.id == result.test_id:
                    test_case = tc
                    break
            
            category = test_case.category if test_case else "unknown"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, results in categories.items():
            successful = sum(1 for r in results if r.success)
            validated = sum(1 for r in results if r.validation_passed)
            avg_time = sum(r.duration_ms for r in results) / len(results)
            
            report += f"""### {category.upper()} Tests
- **Total**: {len(results)}
- **Success Rate**: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)
- **Validation Rate**: {validated}/{len(results)} ({validated/len(results)*100:.1f}%)
- **Average Response**: {avg_time:.1f}ms

"""
        
        # Add detailed results
        report += "## Detailed Test Results\n\n"
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            validation = "✅ VALID" if result.validation_passed else "⚠️ INVALID"
            
            report += f"""### {result.test_id}
- **Tool**: {result.tool_name}
- **Status**: {status} {validation}
- **Duration**: {result.duration_ms:.1f}ms
- **Params**: `{json.dumps(result.params, indent=2)}`

"""
            
            if result.success and "result" in result.result:
                # Show truncated result
                result_str = json.dumps(result.result["result"], indent=2)
                if len(result_str) > 500:
                    result_str = result_str[:500] + "..."
                
                report += f"""**Result**:
```json
{result_str}
```

"""
            elif result.error:
                report += f"""**Error**: {result.error}

"""
        
        # Add recommendations
        failed_tests = [r for r in self.results if not r.success]
        validation_issues = [r for r in self.results if r.success and not r.validation_passed]
        
        report += "## Recommendations\n"
        if failed_tests:
            report += f"- ❌ **{len(failed_tests)} tests failed** - Review server implementation\n"
        if validation_issues:
            report += f"- ⚠️ **{len(validation_issues)} validation issues** - Review expected fields\n"
        if not failed_tests and not validation_issues:
            report += "- ✅ **All tests passed** - Server is fully functional\n"
        
        return report

async def main():
    """Main test execution"""
    # Test both possible Railway URLs
    base_urls = [
        "https://strunz.up.railway.app",
        "https://strunz-knowledge-production.up.railway.app"
    ]
    
    working_url = None
    
    # Find working URL
    for url in base_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/")
                if response.status_code == 200:
                    working_url = url
                    print(f"✅ Found working server at: {url}")
                    break
        except:
            continue
    
    if not working_url:
        print("❌ No working Railway server found")
        return
    
    # Run tests
    tester = ProductionMCPTester(working_url)
    summary = await tester.run_comprehensive_tests()
    
    if "error" in summary:
        print(f"❌ Test execution failed: {summary['error']}")
        return
    
    # Generate report
    report = tester.generate_report(summary)
    
    # Save report with datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = Path(f"docs/test-reports/PRODUCTION_TEST_REPORT_{timestamp}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"📊 Final Summary: {summary['successful_tests']}/{summary['total_tests']} passed, {summary['validated_tests']} fully validated")

if __name__ == "__main__":
    asyncio.run(main())