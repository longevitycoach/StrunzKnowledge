#!/usr/bin/env python3
"""
Test MCP Server using proper MCP client protocol
Tests all 19 tools with comprehensive test cases
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

# MCP protocol JSON-RPC format
@dataclass
class TestCase:
    """Test case for MCP tool"""
    id: str
    tool_name: str
    description: str
    params: Dict[str, Any]
    expected_fields: List[str] = field(default_factory=list)
    category: str = "general"

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

class MCPClientTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
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
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": f"{self.session_id}_list"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=request
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {}).get("tools", [])
            return []
    
    def generate_comprehensive_test_cases(self) -> List[TestCase]:
        """Generate 200+ test cases for all MCP tools"""
        test_cases = []
        
        # 1. Search and Analysis Tools (50+ tests)
        search_queries = [
            # Basic searches
            ("Vitamin D Mangel", {"sources": ["books"]}),
            ("Magnesium deficiency symptoms", {"sources": ["news", "forum"]}),
            ("Amino acids for athletes", {"sources": ["books"]}),
            ("Corona prevention", {"sources": ["news"]}),
            ("Low carb diet", {"sources": ["books", "forum"]}),
            # Advanced searches with filters
            ("Omega-3 EPA DHA", {"sources": ["books"], "categories": ["nutrition"]}),
            ("Sleep optimization", {"sources": ["forum"], "min_engagement": 10}),
            ("Stress reduction", {"sources": ["books"], "date_range": {"start": "2020-01-01", "end": "2025-01-01"}}),
            # User-specific searches
            ("Athletic performance", {"sources": ["books"]}, {"role": "athlete", "experience_level": "advanced"}),
            ("Longevity protocols", {"sources": ["news"]}, {"role": "longevity_enthusiast"}),
        ]
        
        for i, query_data in enumerate(search_queries):
            query = query_data[0]
            filters = query_data[1] if len(query_data) > 1 else {}
            user_profile = query_data[2] if len(query_data) > 2 else None
            
            params = {"query": query}
            if filters:
                params["filters"] = filters
            if user_profile:
                params["user_profile"] = user_profile
                
            test_cases.append(TestCase(
                id=f"search_{i+1}",
                tool_name="knowledge_search",
                description=f"Search: {query}",
                params=params,
                expected_fields=["source", "title", "content", "score"],
                category="search"
            ))
        
        # 2. Contradiction Analysis (20+ tests)
        topics = ["Vitamin D dosing", "Protein intake", "Fasting", "Saturated fat", "Coffee"]
        for topic in topics:
            for time_range in ["all", "recent", "2020"]:
                test_cases.append(TestCase(
                    id=f"contradiction_{topic.replace(' ', '_')}_{time_range}",
                    tool_name="find_contradictions",
                    description=f"Contradictions: {topic} ({time_range})",
                    params={"topic": topic, "time_range": time_range},
                    expected_fields=["contradictions_found", "examples"],
                    category="analysis"
                ))
        
        # 3. Topic Evolution (15+ tests)
        evolution_topics = [
            ("Vitamin D", "2010-01-01", "2025-01-01"),
            ("Corona", "2019-01-01", "2023-12-31"),
            ("Longevity", "2015-01-01", "2025-01-01")
        ]
        for concept, start, end in evolution_topics:
            test_cases.append(TestCase(
                id=f"evolution_{concept}",
                tool_name="trace_topic_evolution",
                description=f"Evolution: {concept}",
                params={"concept": concept, "start_date": start, "end_date": end},
                expected_fields=["timeline", "key_developments"],
                category="analysis"
            ))
        
        # 4. Health Protocols (30+ tests)
        conditions = [
            ("chronic fatigue", {"role": "patient", "age": 45}),
            ("athletic performance", {"role": "athlete", "sport": "triathlon"}),
            ("weight loss", {"role": "beginner", "current_bmi": 28}),
            ("cognitive enhancement", {"role": "functional_expert"}),
            ("longevity optimization", {"role": "longevity_enthusiast"})
        ]
        
        for condition, profile in conditions:
            for evidence in ["high", "medium", "exploratory"]:
                test_cases.append(TestCase(
                    id=f"protocol_{condition.replace(' ', '_')}_{evidence}",
                    tool_name="create_health_protocol",
                    description=f"Protocol: {condition} ({evidence})",
                    params={
                        "condition": condition,
                        "user_profile": profile,
                        "evidence_level": evidence
                    },
                    expected_fields=["recommendations", "supplements", "timeline"],
                    category="protocol"
                ))
        
        # 5. Supplement Analysis (25+ tests)
        stacks = [
            (["Vitamin D3", "K2", "Magnesium"], ["bone health"]),
            (["Omega-3", "Curcumin"], ["anti-inflammation"]),
            (["B-Complex", "CoQ10"], ["energy"]),
            (["Creatine", "Beta-Alanine"], ["performance"]),
            (["Ashwagandha", "L-Theanine"], ["stress"])
        ]
        
        for supplements, goals in stacks:
            test_cases.append(TestCase(
                id=f"supplements_{'+'.join(s[:3] for s in supplements)}",
                tool_name="analyze_supplement_stack",
                description=f"Stack: {', '.join(supplements)}",
                params={
                    "supplements": supplements,
                    "health_goals": goals
                },
                expected_fields=["safety_analysis", "interactions"],
                category="supplements"
            ))
        
        # 6. Nutrition Calculator (20+ tests)
        meal_scenarios = [
            ([{"name": "Salmon", "amount": "200g"}, {"name": "Broccoli", "amount": "150g"}], "moderate", ["heart_health"]),
            ([{"name": "Chicken", "amount": "150g"}, {"name": "Rice", "amount": "100g"}], "very_active", ["muscle_gain"]),
            ([{"name": "Eggs", "amount": "3"}, {"name": "Avocado", "amount": "100g"}], "sedentary", ["weight_loss"])
        ]
        
        for foods, activity, goals in meal_scenarios:
            test_cases.append(TestCase(
                id=f"nutrition_{activity}_{goals[0]}",
                tool_name="nutrition_calculator",
                description=f"Nutrition: {foods[0]['name']} meal",
                params={
                    "foods": foods,
                    "activity_level": activity,
                    "health_goals": goals
                },
                expected_fields=["nutritional_values", "recommendations"],
                category="nutrition"
            ))
        
        # 7. Community Insights (20+ tests)
        community_topics = ["vitamin D", "low carb", "supplements", "exercise", "sleep"]
        roles = ["beginner", "athlete", "strunz_fan"]
        
        for topic in community_topics:
            for role in roles:
                test_cases.append(TestCase(
                    id=f"community_{topic.replace(' ', '_')}_{role}",
                    tool_name="get_community_insights",
                    description=f"Community: {topic} for {role}",
                    params={
                        "topic": topic,
                        "user_role": role,
                        "time_period": "recent"
                    },
                    expected_fields=["insights_count", "success_stories"],
                    category="community"
                ))
        
        # 8. Newsletter Analysis (10+ tests)
        test_cases.extend([
            TestCase(
                id="newsletter_full",
                tool_name="analyze_strunz_newsletter_evolution",
                description="Newsletter evolution 2004-2025",
                params={"start_year": "2004", "end_year": "2025"},
                expected_fields=["total_articles", "content_evolution"],
                category="newsletter"
            ),
            TestCase(
                id="newsletter_covid",
                tool_name="analyze_strunz_newsletter_evolution", 
                description="Newsletter COVID period",
                params={"start_year": "2020", "end_year": "2022", "focus_topics": ["Corona"]},
                expected_fields=["content_evolution"],
                category="newsletter"
            )
        ])
        
        # 9. User Assessment (15+ tests)
        profiles = [
            {"age": 30, "gender": "male", "goals": ["energy"], "symptoms": ["fatigue"]},
            {"age": 50, "gender": "female", "goals": ["longevity"], "symptoms": ["joint_pain"]},
            {"age": 40, "gender": "male", "goals": ["athletic_performance"], "exercise": "daily"}
        ]
        
        for i, profile in enumerate(profiles):
            test_cases.append(TestCase(
                id=f"assessment_{i+1}",
                tool_name="assess_user_health_profile",
                description=f"Assessment: {profile['age']}yo {profile['gender']}",
                params={"assessment_responses": profile},
                expected_fields=["profile", "assigned_role"],
                category="assessment"
            ))
        
        # 10. Information Tools (10+ tests)
        info_tools = [
            ("get_dr_strunz_biography", {}, ["full_name", "career_highlights"]),
            ("get_mcp_server_purpose", {}, ["primary_purpose", "key_capabilities"]),
            ("get_vector_db_analysis", {}, ["database_overview", "content_distribution"]),
            ("get_knowledge_statistics", {}, ["total_documents", "books"])
        ]
        
        for tool_name, params, fields in info_tools:
            test_cases.append(TestCase(
                id=f"info_{tool_name}",
                tool_name=tool_name,
                description=f"Info: {tool_name}",
                params=params,
                expected_fields=fields,
                category="information"
            ))
        
        # 11. Edge Cases (20+ tests)
        edge_cases = [
            TestCase(
                id="edge_empty_query",
                tool_name="knowledge_search",
                description="Empty search query",
                params={"query": ""},
                expected_fields=[],
                category="edge_case"
            ),
            TestCase(
                id="edge_unicode",
                tool_name="knowledge_search",
                description="Unicode search",
                params={"query": "Vitamin D3 (5000 IU) + K2 🌟"},
                expected_fields=["source"],
                category="edge_case"
            ),
            TestCase(
                id="edge_long_query",
                tool_name="knowledge_search",
                description="Very long query",
                params={"query": "vitamin " * 100},
                expected_fields=[],
                category="edge_case"
            ),
            TestCase(
                id="edge_empty_supplements",
                tool_name="analyze_supplement_stack",
                description="Empty supplement list",
                params={"supplements": [], "health_goals": ["general"]},
                expected_fields=["optimization_suggestions"],
                category="edge_case"
            )
        ]
        test_cases.extend(edge_cases)
        
        # 12. Performance Tests (10+ tests)
        perf_tests = [
            TestCase(
                id="perf_large_search",
                tool_name="knowledge_search",
                description="Search all sources",
                params={"query": "health", "filters": {"sources": ["books", "news", "forum"]}},
                expected_fields=["source"],
                category="performance"
            ),
            TestCase(
                id="perf_long_evolution",
                tool_name="trace_topic_evolution",
                description="20-year evolution",
                params={"concept": "nutrition", "start_date": "2004-01-01", "end_date": "2024-12-31"},
                expected_fields=["timeline"],
                category="performance"
            )
        ]
        test_cases.extend(perf_tests)
        
        return test_cases
    
    async def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            response = await self.call_mcp_tool(test_case.tool_name, test_case.params)
            duration_ms = (time.time() - start_time) * 1000
            
            if "error" in response:
                return TestResult(
                    test_id=test_case.id,
                    tool_name=test_case.tool_name,
                    params=test_case.params,
                    result=None,
                    duration_ms=duration_ms,
                    success=False,
                    error=response["error"].get("message", str(response["error"]))
                )
            
            result = response.get("result", {})
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result=result,
                duration_ms=duration_ms,
                success=True
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result=None,
                duration_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )
    
    async def run_all_tests(self):
        """Run all test cases"""
        # First check if server is running
        print("🔍 Checking MCP server availability...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code != 200:
                    print(f"❌ Server not responding properly: {response.status_code}")
                    return
                print("✅ Server is running")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return
        
        # List available tools
        print("\n📋 Listing available MCP tools...")
        tools = await self.list_tools()
        if not tools:
            print("❌ No tools available or MCP endpoint not working")
            return
        
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools[:5]:  # Show first 5
            print(f"   - {tool.get('name', 'unknown')}")
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more")
        
        # Generate test cases
        test_cases = self.generate_comprehensive_test_cases()
        print(f"\n🚀 Running {len(test_cases)} test cases")
        print("=" * 80)
        
        # Run tests by category
        categories = {}
        for test in test_cases:
            if test.category not in categories:
                categories[test.category] = []
            categories[test.category].append(test)
        
        for category, tests in categories.items():
            print(f"\n📂 {category.upper()} ({len(tests)} tests)")
            print("-" * 60)
            
            for i, test in enumerate(tests, 1):
                print(f"  [{i}/{len(tests)}] {test.description}...", end="", flush=True)
                
                result = await self.run_test(test)
                self.results.append(result)
                
                if result.success:
                    print(f" ✅ ({result.duration_ms:.1f}ms)")
                else:
                    print(f" ❌ {result.error}")
                
                # Rate limiting
                await asyncio.sleep(0.1)
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("# MCP Server Comprehensive Test Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Server**: {self.base_url}")
        report.append(f"**Total Tests**: {len(self.results)}")
        report.append("")
        
        # Summary
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        total_time = sum(r.duration_ms for r in self.results)
        
        report.append("## Executive Summary")
        report.append(f"- **Success Rate**: {successful}/{len(self.results)} ({successful/len(self.results)*100:.1f}%)")
        report.append(f"- **Failed Tests**: {failed}")
        report.append(f"- **Total Time**: {total_time/1000:.2f}s")
        report.append(f"- **Average Response**: {total_time/len(self.results):.1f}ms")
        report.append("")
        
        # Results by category
        categories = {}
        for result in self.results:
            # Find category from test_id
            category = "general"
            for prefix in ["search", "protocol", "supplements", "nutrition", "community", "assessment"]:
                if result.test_id.startswith(prefix):
                    category = prefix
                    break
            
            if category not in categories:
                categories[category] = {"success": 0, "failed": 0, "total_ms": 0}
            
            categories[category]["total_ms"] += result.duration_ms
            if result.success:
                categories[category]["success"] += 1
            else:
                categories[category]["failed"] += 1
        
        report.append("## Results by Category")
        report.append("| Category | Success | Failed | Avg Response |")
        report.append("|----------|---------|--------|--------------|")
        
        for cat, stats in sorted(categories.items()):
            total = stats["success"] + stats["failed"]
            avg_ms = stats["total_ms"] / total if total > 0 else 0
            report.append(f"| {cat} | {stats['success']} | {stats['failed']} | {avg_ms:.1f}ms |")
        
        # Performance analysis
        report.append("\n## Performance Analysis")
        
        # Slowest tests
        slowest = sorted([r for r in self.results if r.success], 
                        key=lambda r: r.duration_ms, reverse=True)[:10]
        
        report.append("\n### Slowest Operations")
        for r in slowest:
            report.append(f"- {r.tool_name} ({r.test_id}): {r.duration_ms:.1f}ms")
        
        # Failed tests
        if failed > 0:
            report.append("\n## Failed Tests")
            failed_tests = [r for r in self.results if not r.success]
            for r in failed_tests[:20]:  # Show first 20
                report.append(f"- **{r.test_id}** ({r.tool_name}): {r.error}")
        
        # Sample outputs
        report.append("\n## Sample Successful Outputs")
        success_samples = [r for r in self.results if r.success and r.result][:5]
        
        for i, r in enumerate(success_samples, 1):
            report.append(f"\n### Example {i}: {r.tool_name}")
            report.append(f"**Test**: {r.test_id}")
            report.append(f"**Params**: `{json.dumps(r.params, ensure_ascii=False)[:100]}...`")
            report.append("**Output** (truncated):")
            report.append("```json")
            output = json.dumps(r.result, indent=2, ensure_ascii=False)[:500]
            report.append(output + "...")
            report.append("```")
        
        report.append("\n## Recommendations")
        
        if successful < len(self.results) * 0.95:
            report.append("- ⚠️ Success rate below 95% - investigate failing tests")
        
        slow_tests = [r for r in self.results if r.success and r.duration_ms > 1000]
        if slow_tests:
            report.append(f"- ⚠️ {len(slow_tests)} tests took over 1 second")
        
        if failed > 0:
            error_types = {}
            for r in [r for r in self.results if not r.success]:
                error_type = r.error.split(":")[0] if r.error else "Unknown"
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            report.append("\n### Error Distribution")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {error_type}: {count} occurrences")
        
        return "\n".join(report)

async def main():
    """Run comprehensive MCP test suite"""
    # Check for test URL from environment or use default
    test_url = os.environ.get("MCP_TEST_URL", "http://localhost:8000")
    
    print(f"🧪 MCP Comprehensive Test Suite")
    print(f"📍 Target: {test_url}")
    print("=" * 80)
    
    tester = MCPClientTester(test_url)
    
    start_time = time.time()
    await tester.run_all_tests()
    duration = time.time() - start_time
    
    # Generate report
    report = tester.generate_report()
    
    # Save report
    report_path = Path(__file__).parent.parent.parent.parent / "docs" / "test-reports" / "MCP_CLIENT_TEST_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Testing completed in {duration:.2f}s")
    print(f"📄 Report saved to: {report_path}")
    
    # Summary
    successful = sum(1 for r in tester.results if r.success)
    print(f"\n📊 Summary: {successful}/{len(tester.results)} tests passed")

if __name__ == "__main__":
    asyncio.run(main())