#!/usr/bin/env python3
"""
Comprehensive Tool Test Suite for StrunzKnowledge v0.9.0
Tests all 24 tools with real inputs and captures outputs
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class ComprehensiveToolTester:
    def __init__(self):
        self.base_url = "https://strunz.up.railway.app"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.9.0",
            "tool_tests": [],
            "prompt_tests": [],
            "summary": {
                "total_tools": 24,
                "total_tested": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a specific tool and return the result"""
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": f"test-{tool_name}-{int(time.time())}"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/messages",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    # Extract the actual content
                    content = data["result"].get("content", [])
                    if content and isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get("text", "")
                        try:
                            # Try to parse as JSON if possible
                            parsed_content = json.loads(text_content)
                            return {
                                "success": True,
                                "output": parsed_content,
                                "response_time": response_time,
                                "raw_response": data
                            }
                        except:
                            # Return as text if not JSON
                            return {
                                "success": True,
                                "output": text_content,
                                "response_time": response_time,
                                "raw_response": data
                            }
                    else:
                        return {
                            "success": True,
                            "output": data["result"],
                            "response_time": response_time,
                            "raw_response": data
                        }
                else:
                    return {
                        "success": False,
                        "error": data.get("error", {}).get("message", "Unknown error"),
                        "response_time": response_time,
                        "raw_response": data
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def test_tool(self, tool_name: str, test_cases: List[Dict]):
        """Test a tool with multiple test cases"""
        tool_result = {
            "tool_name": tool_name,
            "is_prompt": tool_name.endswith("_prompt"),
            "test_cases": [],
            "overall_success": True
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"\n  Test case {i+1}: {test_case.get('description', 'No description')}")
            print(f"  Input: {json.dumps(test_case['input'], indent=2)}")
            
            result = self.call_tool(tool_name, test_case['input'])
            
            test_result = {
                "description": test_case.get('description', ''),
                "input": test_case['input'],
                "expected_type": test_case.get('expected_type', 'any'),
                "success": result['success'],
                "response_time": result.get('response_time', 0)
            }
            
            if result['success']:
                test_result['output'] = result['output']
                print(f"  ✅ Success ({result['response_time']:.2f}s)")
                
                # Truncate output for display if it's too long
                output_str = str(result['output'])
                if isinstance(result['output'], dict):
                    output_str = json.dumps(result['output'], indent=2)
                
                if len(output_str) > 500:
                    print(f"  Output (truncated): {output_str[:500]}...")
                else:
                    print(f"  Output: {output_str}")
            else:
                test_result['error'] = result['error']
                tool_result['overall_success'] = False
                print(f"  ❌ Failed: {result['error']}")
            
            tool_result['test_cases'].append(test_result)
        
        return tool_result
    
    def run_all_tool_tests(self):
        """Run tests for all 24 tools"""
        
        # Define test cases for each tool
        tool_test_definitions = {
            # Knowledge and Search Tools
            "knowledge_search": [
                {
                    "description": "Search for vitamin D information",
                    "input": {"query": "vitamin D deficiency symptoms", "max_results": 3},
                    "expected_type": "search_results"
                },
                {
                    "description": "Search for magnesium benefits",
                    "input": {"query": "magnesium benefits sleep", "max_results": 2},
                    "expected_type": "search_results"
                }
            ],
            
            "find_contradictions": [
                {
                    "description": "Find contradictions about vitamin C dosage",
                    "input": {"topic": "vitamin C dosage"},
                    "expected_type": "contradictions"
                }
            ],
            
            "trace_topic_evolution": [
                {
                    "description": "Trace evolution of intermittent fasting",
                    "input": {"topic": "intermittent fasting", "start_year": 2010, "end_year": 2025},
                    "expected_type": "evolution"
                }
            ],
            
            # Health Protocol Tools
            "create_health_protocol": [
                {
                    "description": "Create protocol for energy optimization",
                    "input": {"condition": "chronic fatigue", "approach": "comprehensive"},
                    "expected_type": "protocol"
                }
            ],
            
            "create_personalized_protocol": [
                {
                    "description": "Create personalized protocol for 40-year-old male",
                    "input": {
                        "health_profile": {
                            "age": 40,
                            "gender": "male",
                            "symptoms": ["low energy", "brain fog"],
                            "goals": ["energy", "mental clarity"]
                        }
                    },
                    "expected_type": "personalized_protocol"
                }
            ],
            
            # Analysis Tools
            "compare_approaches": [
                {
                    "description": "Compare vitamin D supplementation approaches",
                    "input": {
                        "topic": "vitamin D supplementation",
                        "approaches": ["daily low dose", "weekly high dose"]
                    },
                    "expected_type": "comparison"
                }
            ],
            
            "analyze_supplement_stack": [
                {
                    "description": "Analyze common supplement stack",
                    "input": {
                        "supplements": ["vitamin D", "magnesium", "omega-3", "vitamin K2"],
                        "user_profile": {"age": 35, "gender": "female"}
                    },
                    "expected_type": "analysis"
                }
            ],
            
            "nutrition_calculator": [
                {
                    "description": "Calculate nutrition needs for active adult",
                    "input": {
                        "age": 30,
                        "weight": 70,
                        "height": 175,
                        "gender": "male",
                        "activity_level": "moderate",
                        "goal": "maintenance"
                    },
                    "expected_type": "nutrition_plan"
                }
            ],
            
            # Community and Newsletter Tools
            "get_community_insights": [
                {
                    "description": "Get insights about fasting",
                    "input": {"topic": "fasting"},
                    "expected_type": "insights"
                }
            ],
            
            "summarize_posts": [
                {
                    "description": "Summarize posts about supplements",
                    "input": {"category": "supplements", "limit": 5},
                    "expected_type": "summary"
                }
            ],
            
            "get_trending_insights": [
                {
                    "description": "Get current trending topics",
                    "input": {"timeframe": "recent"},
                    "expected_type": "trends"
                }
            ],
            
            "analyze_strunz_newsletter_evolution": [
                {
                    "description": "Analyze newsletter evolution 2020-2025",
                    "input": {"start_year": 2020, "end_year": 2025},
                    "expected_type": "evolution_analysis"
                }
            ],
            
            "get_guest_authors_analysis": [
                {
                    "description": "Analyze guest author contributions",
                    "input": {},
                    "expected_type": "author_analysis"
                }
            ],
            
            "track_health_topic_trends": [
                {
                    "description": "Track vitamin D trends",
                    "input": {"topic": "vitamin D", "timeframe": "5_years"},
                    "expected_type": "trend_analysis"
                }
            ],
            
            # Assessment and Profile Tools
            "get_health_assessment_questions": [
                {
                    "description": "Get cardiovascular assessment questions",
                    "input": {"category": "cardiovascular"},
                    "expected_type": "questions"
                }
            ],
            
            "assess_user_health_profile": [
                {
                    "description": "Assess health profile for middle-aged woman",
                    "input": {
                        "age": 45,
                        "gender": "female",
                        "symptoms": ["fatigue", "weight gain"],
                        "medical_history": ["hypothyroidism"],
                        "lifestyle": {"exercise": "low", "stress": "high"}
                    },
                    "expected_type": "assessment"
                }
            ],
            
            # Information Tools
            "get_dr_strunz_biography": [
                {
                    "description": "Get Dr. Strunz biography",
                    "input": {},
                    "expected_type": "biography"
                }
            ],
            
            "get_dr_strunz_info": [
                {
                    "description": "Get Dr. Strunz information",
                    "input": {},
                    "expected_type": "info"
                }
            ],
            
            "get_mcp_server_purpose": [
                {
                    "description": "Get server purpose and capabilities",
                    "input": {},
                    "expected_type": "server_info"
                }
            ],
            
            "get_vector_db_analysis": [
                {
                    "description": "Analyze vector database for longevity content",
                    "input": {"topic": "longevity"},
                    "expected_type": "db_analysis"
                }
            ],
            
            "get_optimal_diagnostic_values": [
                {
                    "description": "Get optimal values for vitamin D",
                    "input": {"biomarker": "vitamin D"},
                    "expected_type": "diagnostic_values"
                }
            ],
            
            # Prompt Tools (Special Handling)
            "health_assessment_prompt": [
                {
                    "description": "Generate health assessment prompt",
                    "input": {"focus": "comprehensive"},
                    "expected_type": "prompt"
                }
            ],
            
            "longevity_protocol_prompt": [
                {
                    "description": "Generate longevity protocol prompt",
                    "input": {"age_group": "40-50"},
                    "expected_type": "prompt"
                }
            ],
            
            "supplement_optimization_prompt": [
                {
                    "description": "Generate supplement optimization prompt",
                    "input": {"goal": "cognitive_enhancement"},
                    "expected_type": "prompt"
                }
            ]
        }
        
        print("\n" + "="*80)
        print("COMPREHENSIVE TOOL TEST REPORT - StrunzKnowledge v0.9.0")
        print("="*80)
        print(f"Testing all 24 tools with real inputs and outputs")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Separate tools and prompts
        regular_tools = [t for t in tool_test_definitions.keys() if not t.endswith("_prompt")]
        prompt_tools = [t for t in tool_test_definitions.keys() if t.endswith("_prompt")]
        
        # Test regular tools
        print("\n\nTESTING REGULAR TOOLS (21)")
        print("-"*80)
        
        for i, tool_name in enumerate(regular_tools, 1):
            print(f"\n{i}. Testing: {tool_name}")
            print("-"*40)
            
            test_cases = tool_test_definitions[tool_name]
            result = self.test_tool(tool_name, test_cases)
            
            if result['overall_success']:
                self.results['summary']['passed'] += 1
                print(f"\n✅ {tool_name}: ALL TESTS PASSED")
            else:
                self.results['summary']['failed'] += 1
                print(f"\n❌ {tool_name}: SOME TESTS FAILED")
            
            self.results['tool_tests'].append(result)
            self.results['summary']['total_tested'] += 1
        
        # Test prompt tools
        print("\n\nTESTING PROMPT TOOLS (3)")
        print("-"*80)
        
        for i, tool_name in enumerate(prompt_tools, 1):
            print(f"\n{i}. Testing: {tool_name}")
            print("-"*40)
            
            test_cases = tool_test_definitions[tool_name]
            result = self.test_tool(tool_name, test_cases)
            
            if result['overall_success']:
                self.results['summary']['passed'] += 1
                print(f"\n✅ {tool_name}: ALL TESTS PASSED")
            else:
                self.results['summary']['failed'] += 1
                print(f"\n❌ {tool_name}: SOME TESTS FAILED")
            
            self.results['prompt_tests'].append(result)
            self.results['summary']['total_tested'] += 1
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate and save the summary report"""
        print("\n\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = self.results['summary']['total_tested']
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        
        print(f"Total Tools Tested: {total}/24")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        # Performance summary
        total_time = 0
        tool_times = []
        
        for tool_result in self.results['tool_tests'] + self.results['prompt_tests']:
            for test_case in tool_result['test_cases']:
                if test_case['success']:
                    response_time = test_case['response_time']
                    total_time += response_time
                    tool_times.append((tool_result['tool_name'], response_time))
        
        print(f"\nTotal Test Time: {total_time:.2f} seconds")
        print(f"Average Response Time: {total_time/len(tool_times):.2f} seconds")
        
        # Slowest tools
        tool_times.sort(key=lambda x: x[1], reverse=True)
        print("\nSlowest Tools:")
        for tool, time in tool_times[:5]:
            print(f"  - {tool}: {time:.2f}s")
        
        # Save detailed report
        report_file = f"test_reports/comprehensive_tool_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        # Generate markdown report
        self.generate_markdown_report()
    
    def generate_markdown_report(self):
        """Generate a markdown report with all inputs and outputs"""
        report = f"""# Comprehensive Tool Test Report - StrunzKnowledge v0.9.0

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Environment**: Production (https://strunz.up.railway.app)  
**Total Tools**: 24  
**Tools Tested**: {self.results['summary']['total_tested']}  
**Pass Rate**: {self.results['summary']['passed']/self.results['summary']['total_tested']*100:.1f}%

## Summary

- ✅ Passed: {self.results['summary']['passed']}
- ❌ Failed: {self.results['summary']['failed']}

## Regular Tools (21)

"""
        
        for i, tool_result in enumerate(self.results['tool_tests'], 1):
            report += f"### {i}. {tool_result['tool_name']}\n\n"
            
            for j, test_case in enumerate(tool_result['test_cases'], 1):
                report += f"**Test Case {j}**: {test_case['description']}\n\n"
                report += f"**Input**:\n```json\n{json.dumps(test_case['input'], indent=2)}\n```\n\n"
                
                if test_case['success']:
                    report += f"**Status**: ✅ Success ({test_case['response_time']:.2f}s)\n\n"
                    
                    output = test_case['output']
                    if isinstance(output, str) and len(output) > 1000:
                        output = output[:1000] + "... (truncated)"
                    elif isinstance(output, dict) or isinstance(output, list):
                        output_str = json.dumps(output, indent=2)
                        if len(output_str) > 1000:
                            output = output_str[:1000] + "... (truncated)"
                        else:
                            output = output_str
                    
                    report += f"**Output**:\n```json\n{output}\n```\n\n"
                else:
                    report += f"**Status**: ❌ Failed\n"
                    report += f"**Error**: {test_case.get('error', 'Unknown error')}\n\n"
        
        report += "## Prompt Tools (3)\n\n"
        
        for i, tool_result in enumerate(self.results['prompt_tests'], 1):
            report += f"### {i}. {tool_result['tool_name']}\n\n"
            
            for j, test_case in enumerate(tool_result['test_cases'], 1):
                report += f"**Test Case {j}**: {test_case['description']}\n\n"
                report += f"**Input**:\n```json\n{json.dumps(test_case['input'], indent=2)}\n```\n\n"
                
                if test_case['success']:
                    report += f"**Status**: ✅ Success ({test_case['response_time']:.2f}s)\n\n"
                    
                    output = test_case['output']
                    if isinstance(output, str) and len(output) > 1000:
                        output = output[:1000] + "... (truncated)"
                    
                    report += f"**Output**:\n```\n{output}\n```\n\n"
                else:
                    report += f"**Status**: ❌ Failed\n"
                    report += f"**Error**: {test_case.get('error', 'Unknown error')}\n\n"
        
        # Save markdown report
        md_file = f"test_reports/comprehensive_tool_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(md_file, "w") as f:
            f.write(report)
        
        print(f"Markdown report saved to: {md_file}")

if __name__ == "__main__":
    tester = ComprehensiveToolTester()
    tester.run_all_tool_tests()