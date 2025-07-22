#!/usr/bin/env python3
"""
Comprehensive MCP Tools and Prompts Testing
Tests all MCP tools and prompts with detailed input/output documentation
"""

import sys
import os
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Test data for various scenarios
TEST_CASES = {
    "knowledge_search": [
        {"query": "vitamin D deficiency symptoms", "sources": ["books", "news"], "limit": 5},
        {"query": "magnesium supplementation", "limit": 3},
        {"query": "Dr. Strunz low carb diet", "sources": ["books"]}
    ],
    "find_contradictions": [
        {"topic": "vitamin C dosage"},
        {"topic": "intermittent fasting", "include_reasoning": True}
    ],
    "trace_topic_evolution": [
        {"topic": "amino acids", "start_year": 2010},
        {"topic": "supplements"}
    ],
    "create_health_protocol": [
        {
            "condition": "chronic fatigue",
            "user_profile": {"age": 45, "gender": "female", "lifestyle": "sedentary"}
        },
        {"condition": "diabetes prevention"}
    ],
    "compare_approaches": [
        {
            "health_issue": "weight loss",
            "alternative_approaches": ["low-carb", "intermittent fasting", "calorie restriction"]
        }
    ],
    "analyze_supplement_stack": [
        {
            "supplements": ["vitamin D", "magnesium", "omega-3"],
            "health_goals": ["energy", "immunity"]
        }
    ],
    "nutrition_calculator": [
        {
            "age": 35,
            "gender": "male",
            "weight": 75.0,
            "height": 180.0,
            "activity_level": "moderate",
            "health_goals": ["muscle building"]
        }
    ],
    "get_community_insights": [
        {"topic": "vitamin supplements"},
        {"topic": "exercise routines", "min_engagement": 3}
    ],
    "summarize_posts": [
        {"category": "nutrition", "limit": 5},
        {"category": "supplements"}
    ],
    "get_trending_insights": [
        {"days": 30},
        {"days": 7, "user_role": "athlete"}
    ],
    "analyze_strunz_newsletter_evolution": [
        {"timeframe": "5_years"},
        {"timeframe": "all", "topic_focus": "supplements"}
    ],
    "get_guest_authors_analysis": [
        {"timeframe": "5_years"},
        {"specialty_focus": "nutrition"}
    ],
    "track_health_topic_trends": [
        {"topic": "immune system", "timeframe": "3_years"}
    ],
    "get_health_assessment_questions": [
        {"user_role": "athlete"},
        {"assessment_depth": "basic"}
    ],
    "assess_user_health_profile": [
        {
            "responses": {
                "age": 40,
                "energy_level": "low",
                "sleep_quality": "poor",
                "exercise_frequency": "rarely"
            },
            "include_recommendations": True
        }
    ],
    "create_personalized_protocol": [
        {
            "user_profile": {
                "age": 50,
                "gender": "male",
                "health_goals": ["longevity", "energy"],
                "current_condition": "good"
            }
        }
    ],
    "get_dr_strunz_biography": [
        {"include_achievements": True, "include_philosophy": True},
        {"include_achievements": False}
    ],
    "get_mcp_server_purpose": [
        {}
    ],
    "get_vector_db_analysis": [
        {}
    ],
    "get_optimal_diagnostic_values": [
        {"age": 40, "gender": "male", "weight": 80.0, "athlete": False},
        {"age": 25, "gender": "female", "athlete": True}
    ]
}

# Prompt test cases
PROMPT_TEST_CASES = {
    "health_assessment_prompt": [
        {
            "age": 45,
            "gender": "female",
            "health_goals": "weight loss and energy",
            "current_symptoms": "fatigue, joint pain",
            "lifestyle_factors": "sedentary job, high stress",
            "current_supplements": "multivitamin"
        }
    ],
    "supplement_analysis_prompt": [
        {
            "supplement_list": "vitamin D, magnesium, omega-3",
            "health_condition": "chronic fatigue"
        }
    ],
    "nutrition_optimization_prompt": [
        {
            "dietary_preferences": "low-carb",
            "health_goals": "weight loss and muscle building"
        }
    ],
    "research_query_prompt": [
        {
            "topic": "intermittent fasting",
            "focus_area": "longevity"
        }
    ],
    "longevity_protocol_prompt": [
        {
            "age": 55,
            "gender": "male",
            "current_health_status": "good",
            "family_history": "heart disease"
        }
    ],
    "diagnostic_interpretation_prompt": [
        {
            "lab_results": "Vitamin D: 15 ng/ml, B12: 250 pg/ml",
            "age": 40,
            "gender": "female"
        }
    ]
}

class MCPTestResults:
    """Store and format test results"""
    
    def __init__(self):
        self.results = {
            "tools": {},
            "prompts": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "start_time": None,
                "end_time": None
            }
        }
    
    def add_tool_result(self, tool_name: str, test_case: Dict, success: bool, result: Any, error: str = None, execution_time: float = 0):
        """Add tool test result"""
        if tool_name not in self.results["tools"]:
            self.results["tools"][tool_name] = []
        
        self.results["tools"][tool_name].append({
            "test_case": test_case,
            "success": success,
            "result": result if success else None,
            "error": error,
            "execution_time_ms": round(execution_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["summary"]["total_tests"] += 1
        if success:
            self.results["summary"]["passed_tests"] += 1
        else:
            self.results["summary"]["failed_tests"] += 1
    
    def add_prompt_result(self, prompt_name: str, test_case: Dict, success: bool, result: Any, error: str = None):
        """Add prompt test result"""
        if prompt_name not in self.results["prompts"]:
            self.results["prompts"][prompt_name] = []
        
        self.results["prompts"][prompt_name].append({
            "test_case": test_case,
            "success": success,
            "result": result if success else None,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["summary"]["total_tests"] += 1
        if success:
            self.results["summary"]["passed_tests"] += 1
        else:
            self.results["summary"]["failed_tests"] += 1
    
    def get_summary(self) -> Dict:
        """Get test summary"""
        total = self.results["summary"]["total_tests"]
        passed = self.results["summary"]["passed_tests"]
        failed = self.results["summary"]["failed_tests"]
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": round((passed / total * 100) if total > 0 else 0, 1),
            "tools_tested": len(self.results["tools"]),
            "prompts_tested": len(self.results["prompts"])
        }

async def test_enhanced_server():
    """Test enhanced server with all tools and prompts"""
    
    print("🚀 Starting Comprehensive MCP Testing...")
    print("=" * 80)
    
    # Initialize test results
    test_results = MCPTestResults()
    test_results.results["summary"]["start_time"] = datetime.now().isoformat()
    
    try:
        # Initialize enhanced server
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        server = StrunzKnowledgeMCP()
        
        print(f"✅ Enhanced server initialized with {len(server.tool_registry)} tools")
        print()
        
        # Test all tools
        print("🛠️ TESTING MCP TOOLS")
        print("-" * 40)
        
        for tool_name, test_cases in TEST_CASES.items():
            if tool_name in server.tool_registry:
                print(f"\n📋 Testing {tool_name}")
                
                for i, test_case in enumerate(test_cases, 1):
                    print(f"  Test {i}: {json.dumps(test_case, ensure_ascii=False)[:100]}...")
                    
                    start_time = time.time()
                    try:
                        # Get tool function (handle FastMCP FunctionTool objects)
                        tool_info = server.tool_registry[tool_name]
                        
                        # Extract function (same logic as unified server)
                        if hasattr(tool_info, 'fn'):
                            tool_func = tool_info.fn  # FastMCP FunctionTool.fn is the actual function
                        elif hasattr(tool_info, 'run'):
                            # FastMCP FunctionTool.run method
                            tool_func = lambda **kwargs: tool_info.run(**kwargs)
                        elif hasattr(tool_info, 'func'):
                            tool_func = tool_info.func  # Other FunctionTool variants
                        elif hasattr(tool_info, 'function'):
                            tool_func = tool_info.function  # Other wrappers
                        elif callable(tool_info):
                            tool_func = tool_info  # Direct function
                        else:
                            # Try to get the original function
                            tool_func = getattr(tool_info, '__call__', tool_info)
                        
                        # Execute tool
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(**test_case)
                        else:
                            result = tool_func(**test_case)
                        
                        execution_time = time.time() - start_time
                        
                        # Record success
                        test_results.add_tool_result(
                            tool_name, test_case, True, result, execution_time=execution_time
                        )
                        
                        print(f"    ✅ Success ({execution_time*1000:.1f}ms)")
                        print(f"    📄 Result: {str(result)[:200]}...")
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        error_msg = str(e)
                        
                        # Record failure
                        test_results.add_tool_result(
                            tool_name, test_case, False, None, error_msg, execution_time
                        )
                        
                        print(f"    ❌ Failed ({execution_time*1000:.1f}ms): {error_msg[:100]}")
            else:
                print(f"⚠️ Tool {tool_name} not found in registry")
        
        # Test prompts (if available)
        if hasattr(server, 'prompts') and server.prompts:
            print("\n\n📝 TESTING MCP PROMPTS")
            print("-" * 40)
            
            for prompt_name, test_cases in PROMPT_TEST_CASES.items():
                if prompt_name in server.prompts:
                    print(f"\n📝 Testing {prompt_name}")
                    
                    for i, test_case in enumerate(test_cases, 1):
                        print(f"  Test {i}: {json.dumps(test_case, ensure_ascii=False)[:100]}...")
                        
                        try:
                            # Get prompt function
                            prompt_func = server.prompts[prompt_name]
                            
                            # Execute prompt
                            if asyncio.iscoroutinefunction(prompt_func):
                                result = await prompt_func(**test_case)
                            else:
                                result = prompt_func(**test_case)
                            
                            # Record success
                            test_results.add_prompt_result(
                                prompt_name, test_case, True, result
                            )
                            
                            print(f"    ✅ Success")
                            print(f"    📄 Prompt: {str(result)[:200]}...")
                            
                        except Exception as e:
                            error_msg = str(e)
                            
                            # Record failure
                            test_results.add_prompt_result(
                                prompt_name, test_case, False, None, error_msg
                            )
                            
                            print(f"    ❌ Failed: {error_msg[:100]}")
                else:
                    print(f"⚠️ Prompt {prompt_name} not found")
        else:
            print("\n📝 No prompts available for testing")
        
    except Exception as e:
        print(f"❌ Failed to initialize enhanced server: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Finalize results
    test_results.results["summary"]["end_time"] = datetime.now().isoformat()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    summary = test_results.get_summary()
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Tools Tested: {summary['tools_tested']}")
    print(f"Prompts Tested: {summary['prompts_tested']}")
    
    return test_results

def generate_test_report(test_results: MCPTestResults, output_file: str):
    """Generate comprehensive test report"""
    
    if not test_results:
        print("❌ No test results to generate report from")
        return
    
    summary = test_results.get_summary()
    
    report_content = f"""# Comprehensive MCP Tools & Prompts Test Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version**: 0.7.8+  
**Target**: Local Enhanced Server  

## Executive Summary

- **Total Tests**: {summary['total_tests']}
- **Success Rate**: {summary['success_rate']}% ({summary['passed_tests']}/{summary['total_tests']})
- **Tools Tested**: {summary['tools_tested']}
- **Prompts Tested**: {summary['prompts_tested']}

## Tool Test Results

"""
    
    # Add tool results
    for tool_name, results in test_results.results["tools"].items():
        report_content += f"### {tool_name}\n\n"
        
        for i, result in enumerate(results, 1):
            status = "✅" if result["success"] else "❌"
            report_content += f"**Test {i}**: {status} ({result['execution_time_ms']}ms)\n\n"
            report_content += f"**Input**:\n```json\n{json.dumps(result['test_case'], indent=2, ensure_ascii=False)}\n```\n\n"
            
            if result["success"]:
                result_str = str(result["result"])
                if len(result_str) > 1000:
                    result_str = result_str[:1000] + "..."
                report_content += f"**Output**:\n```\n{result_str}\n```\n\n"
            else:
                report_content += f"**Error**: {result['error']}\n\n"
            
            report_content += "---\n\n"
    
    # Add prompt results
    if test_results.results["prompts"]:
        report_content += "## Prompt Test Results\n\n"
        
        for prompt_name, results in test_results.results["prompts"].items():
            report_content += f"### {prompt_name}\n\n"
            
            for i, result in enumerate(results, 1):
                status = "✅" if result["success"] else "❌"
                report_content += f"**Test {i}**: {status}\n\n"
                report_content += f"**Input**:\n```json\n{json.dumps(result['test_case'], indent=2, ensure_ascii=False)}\n```\n\n"
                
                if result["success"]:
                    result_str = str(result["result"])
                    if len(result_str) > 1000:
                        result_str = result_str[:1000] + "..."
                    report_content += f"**Generated Prompt**:\n```\n{result_str}\n```\n\n"
                else:
                    report_content += f"**Error**: {result['error']}\n\n"
                
                report_content += "---\n\n"
    
    # Add test data summary
    report_content += f"""## Test Configuration

### Tool Test Cases
{len(TEST_CASES)} tools tested with {sum(len(cases) for cases in TEST_CASES.values())} test cases total.

### Prompt Test Cases  
{len(PROMPT_TEST_CASES)} prompts tested with {sum(len(cases) for cases in PROMPT_TEST_CASES.values())} test cases total.

## Recommendations

"""
    
    if summary['success_rate'] >= 90:
        report_content += "🎉 **Excellent**: All systems functioning properly.\n\n"
    elif summary['success_rate'] >= 75:
        report_content += "✅ **Good**: Most functionality working, minor issues to address.\n\n"
    else:
        report_content += "⚠️ **Issues Detected**: Significant problems need attention.\n\n"
    
    # Write report
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Test report saved to: {output_file}")

async def main():
    """Main test function"""
    
    # Run tests
    test_results = await test_enhanced_server()
    
    if test_results:
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"docs/test-reports/COMPREHENSIVE_MCP_TEST_REPORT_{timestamp}.md"
        generate_test_report(test_results, report_file)
        
        # Save raw results as JSON
        json_file = f"docs/test-reports/mcp_test_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results.results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Raw test data saved to: {json_file}")
        
        summary = test_results.get_summary()
        if summary['success_rate'] >= 75:
            print("🎉 Test suite completed successfully!")
        else:
            print("⚠️ Test suite completed with issues.")
            
        return summary['success_rate']
    else:
        print("❌ Test suite failed to run.")
        return 0

if __name__ == "__main__":
    success_rate = asyncio.run(main())