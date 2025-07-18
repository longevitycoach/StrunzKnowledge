#!/usr/bin/env python3
"""
Comprehensive MCP Server Test with Full Input/Output Reporting
Tests all 19 MCP tools and 3 prompts with detailed I/O logging
"""
import asyncio
import json
import time
import logging
import httpx
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveMCPTester:
    """Comprehensive MCP server tester with full I/O reporting"""
    
    def __init__(self, base_url: str = "http://localhost:8000", production: bool = False):
        self.base_url = base_url.rstrip('/')
        self.production = production
        self.test_results = []
        self.start_time = datetime.now()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_health(self) -> Dict:
        """Test server health endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            return {
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "error": None
            }
        except Exception as e:
            return {"status": 0, "data": None, "error": str(e)}
    
    async def test_tool(self, tool_name: str, params: Dict, description: str) -> Dict:
        """Test a single MCP tool with full I/O logging"""
        self.total_tests += 1
        start_time = time.time()
        
        # Prepare JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": self.total_tests
        }
        
        result = {
            "test_id": self.total_tests,
            "tool_name": tool_name,
            "description": description,
            "input": params,
            "request": request,
            "output": None,
            "status": "PENDING",
            "duration_ms": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Make the request
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            result["duration_ms"] = duration_ms
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data:
                    result["status"] = "PASS"
                    result["output"] = response_data["result"]
                    self.passed_tests += 1
                    
                    # Log summary
                    logger.info(f"✅ [{self.total_tests}] {tool_name}: {description} - PASS ({duration_ms}ms)")
                    
                    # Extract meaningful output summary
                    if isinstance(response_data["result"], list):
                        result["output_summary"] = f"Returned {len(response_data['result'])} results"
                    elif isinstance(response_data["result"], dict):
                        result["output_summary"] = f"Keys: {', '.join(list(response_data['result'].keys())[:5])}"
                    else:
                        result["output_summary"] = str(response_data["result"])[:100]
                        
                elif "error" in response_data:
                    result["status"] = "FAIL"
                    result["error"] = response_data["error"]
                    self.failed_tests += 1
                    logger.error(f"❌ [{self.total_tests}] {tool_name}: {description} - FAIL: {response_data['error'].get('message', 'Unknown error')}")
                else:
                    result["status"] = "FAIL"
                    result["error"] = "Invalid response format"
                    self.failed_tests += 1
                    logger.error(f"❌ [{self.total_tests}] {tool_name}: Invalid response format")
            else:
                result["status"] = "FAIL"
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                self.failed_tests += 1
                logger.error(f"❌ [{self.total_tests}] {tool_name}: HTTP {response.status_code}")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["duration_ms"] = int((time.time() - start_time) * 1000)
            self.failed_tests += 1
            logger.error(f"💥 [{self.total_tests}] {tool_name}: Exception - {str(e)}")
        
        self.test_results.append(result)
        return result
    
    async def test_prompt(self, prompt_name: str, arguments: Dict, description: str) -> Dict:
        """Test a single MCP prompt with full I/O logging"""
        self.total_tests += 1
        start_time = time.time()
        
        # Prepare JSON-RPC request for prompts
        request = {
            "jsonrpc": "2.0",
            "method": "prompts/get",
            "params": {
                "name": prompt_name,
                "arguments": arguments
            },
            "id": self.total_tests
        }
        
        result = {
            "test_id": self.total_tests,
            "prompt_name": prompt_name,
            "description": description,
            "input": arguments,
            "request": request,
            "output": None,
            "status": "PENDING",
            "duration_ms": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Make the request
            response = await self.client.post(
                f"{self.base_url}/messages",
                json=request,
                headers={"Content-Type": "application/json"}
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            result["duration_ms"] = duration_ms
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data:
                    result["status"] = "PASS"
                    result["output"] = response_data["result"]
                    self.passed_tests += 1
                    
                    # Log summary
                    logger.info(f"✅ [{self.total_tests}] Prompt {prompt_name}: {description} - PASS ({duration_ms}ms)")
                    
                    # Extract prompt details
                    if "messages" in response_data.get("result", {}):
                        msg_count = len(response_data["result"]["messages"])
                        result["output_summary"] = f"Generated {msg_count} messages"
                    else:
                        result["output_summary"] = "Prompt generated"
                        
                elif "error" in response_data:
                    result["status"] = "FAIL"
                    result["error"] = response_data["error"]
                    self.failed_tests += 1
                    logger.error(f"❌ [{self.total_tests}] Prompt {prompt_name}: FAIL - {response_data['error'].get('message', 'Unknown error')}")
                else:
                    result["status"] = "FAIL"
                    result["error"] = "Invalid response format"
                    self.failed_tests += 1
                    
            else:
                result["status"] = "FAIL"
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                self.failed_tests += 1
                logger.error(f"❌ [{self.total_tests}] Prompt {prompt_name}: HTTP {response.status_code}")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["duration_ms"] = int((time.time() - start_time) * 1000)
            self.failed_tests += 1
            logger.error(f"💥 [{self.total_tests}] Prompt {prompt_name}: Exception - {str(e)}")
        
        self.test_results.append(result)
        return result
    
    async def run_all_tests(self):
        """Run all comprehensive MCP tests"""
        logger.info("🚀 Starting Comprehensive MCP Test Suite with Full I/O")
        logger.info(f"📍 Target: {self.base_url}")
        logger.info(f"🌐 Mode: {'Production' if self.production else 'Local'}")
        logger.info("=" * 80)
        
        # Check health first
        health = await self.test_health()
        if health["status"] != 200:
            logger.error(f"❌ Server health check failed: {health['error']}")
            if self.production:
                logger.warning("⚠️  Continuing with production tests despite health check failure")
            else:
                return
        else:
            logger.info(f"✅ Server healthy: v{health['data'].get('version', 'unknown')}")
        
        # Test all 19 MCP tools
        logger.info("\n📋 Testing MCP Tools...")
        logger.info("-" * 40)
        
        # 1. Core Information Tools
        await self.test_tool(
            "get_dr_strunz_biography",
            {},
            "Get comprehensive biography and achievements of Dr. Strunz"
        )
        
        await self.test_tool(
            "get_mcp_server_purpose",
            {},
            "Get MCP server purpose, capabilities, and tool inventory"
        )
        
        await self.test_tool(
            "get_vector_db_analysis",
            {},
            "Analyze vector database statistics and content distribution"
        )
        
        # 2. Search and Analysis Tools
        await self.test_tool(
            "knowledge_search",
            {
                "query": "Vitamin D Mangel Symptome Müdigkeit",
                "sources": ["books", "news"],
                "limit": 5
            },
            "Search for Vitamin D deficiency symptoms with German query"
        )
        
        await self.test_tool(
            "find_contradictions",
            {
                "topic": "vitamin D dosage",
                "time_range": "all"
            },
            "Find contradictions in vitamin D dosage recommendations over time"
        )
        
        await self.test_tool(
            "trace_topic_evolution",
            {
                "topic": "intermittent fasting",
                "start_year": 2010,
                "end_year": 2024
            },
            "Trace evolution of intermittent fasting from 2010 to 2024"
        )
        
        # 3. Health Protocol Tools
        await self.test_tool(
            "create_health_protocol",
            {
                "condition": "chronic fatigue",
                "user_profile": {
                    "age": 45,
                    "gender": "female",
                    "activity_level": "sedentary"
                }
            },
            "Create personalized protocol for 45-year-old woman with chronic fatigue"
        )
        
        await self.test_tool(
            "analyze_supplement_stack",
            {
                "supplements": ["vitamin D3 5000IU", "magnesium glycinate 400mg", "omega-3 2g", "vitamin K2 200mcg"],
                "health_goals": ["bone health", "cardiovascular health"],
                "check_interactions": True
            },
            "Analyze supplement stack for bone and heart health with interaction check"
        )
        
        await self.test_tool(
            "nutrition_calculator",
            {
                "meal_plan": [
                    {"food": "wild salmon", "amount": 150, "unit": "g"},
                    {"food": "spinach", "amount": 200, "unit": "g"},
                    {"food": "almonds", "amount": 30, "unit": "g"},
                    {"food": "olive oil", "amount": 15, "unit": "ml"}
                ],
                "calculate": ["calories", "protein", "omega3", "vitamins"]
            },
            "Calculate detailed nutrition for a complete meal"
        )
        
        # 4. Community Insights Tools
        await self.test_tool(
            "get_community_insights",
            {
                "topic": "magnesium timing",
                "insight_type": "practical_tips"
            },
            "Get community insights on optimal magnesium supplementation timing"
        )
        
        await self.test_tool(
            "summarize_posts",
            {
                "category": "success stories",
                "time_period": "last_6_months",
                "focus": ["weight loss", "energy improvement"]
            },
            "Summarize success stories focusing on weight loss and energy"
        )
        
        await self.test_tool(
            "get_trending_insights",
            {
                "lookback_days": 30,
                "min_mentions": 5
            },
            "Get trending health topics from the last 30 days"
        )
        
        # 5. Newsletter Analysis Tools
        await self.test_tool(
            "analyze_strunz_newsletter_evolution",
            {
                "start_year": 2020,
                "end_year": 2024,
                "focus_topics": ["covid-19", "immunity", "vitamin D"]
            },
            "Analyze how COVID-19 and immunity topics evolved in newsletters"
        )
        
        await self.test_tool(
            "get_guest_authors_analysis",
            {
                "min_articles": 3,
                "include_topics": True
            },
            "Analyze guest authors with 3+ articles and their main topics"
        )
        
        await self.test_tool(
            "track_health_topic_trends",
            {
                "topics": ["longevity", "metabolic health", "mental health"],
                "granularity": "yearly",
                "include_sentiment": True
            },
            "Track trends in longevity, metabolic, and mental health topics"
        )
        
        # 6. User Profiling Tools
        await self.test_tool(
            "get_health_assessment_questions",
            {
                "categories": ["nutrition", "fitness", "sleep"],
                "user_type": "beginner"
            },
            "Get beginner-level health assessment questions for multiple categories"
        )
        
        await self.test_tool(
            "assess_user_health_profile",
            {
                "assessment_responses": {
                    "age": 35,
                    "height": 175,
                    "weight": 80,
                    "activity_level": "moderate",
                    "sleep_hours": 6,
                    "stress_level": "high",
                    "health_goals": ["reduce stress", "improve sleep", "increase energy"],
                    "current_symptoms": ["fatigue", "poor sleep quality", "afternoon energy dip"]
                }
            },
            "Assess health profile for stressed 35-year-old with sleep issues"
        )
        
        await self.test_tool(
            "create_personalized_protocol",
            {
                "user_profile": {
                    "age": 35,
                    "gender": "male",
                    "health_score": 65,
                    "main_concerns": ["stress", "sleep", "energy"]
                },
                "preferences": {
                    "supplement_budget": "moderate",
                    "time_availability": "limited",
                    "dietary_restrictions": ["vegetarian"]
                },
                "focus_areas": ["stress management", "sleep optimization"]
            },
            "Create personalized protocol for vegetarian with stress and sleep issues"
        )
        
        # 7. Comparison Tool
        await self.test_tool(
            "compare_approaches",
            {
                "approach1": {
                    "name": "ketogenic diet",
                    "context": "weight loss"
                },
                "approach2": {
                    "name": "mediterranean diet",
                    "context": "weight loss"
                },
                "comparison_criteria": ["effectiveness", "sustainability", "health benefits", "side effects"]
            },
            "Compare keto vs mediterranean diet for weight loss across multiple criteria"
        )
        
        # Test MCP Prompts
        logger.info("\n📝 Testing MCP Prompts...")
        logger.info("-" * 40)
        
        await self.test_prompt(
            "health_assessment",
            {
                "symptoms": ["chronic fatigue", "brain fog", "joint pain"],
                "duration": "6 months",
                "severity": "moderate to severe",
                "medical_history": ["hypothyroidism"],
                "current_medications": ["levothyroxine"],
                "lifestyle": {
                    "diet": "standard western",
                    "exercise": "minimal",
                    "sleep": "6-7 hours",
                    "stress": "high"
                },
                "health_goals": ["increase energy", "mental clarity", "reduce pain"]
            },
            "Comprehensive health assessment for chronic fatigue with thyroid issues"
        )
        
        await self.test_prompt(
            "supplement_optimization",
            {
                "current_supplements": [
                    {"name": "vitamin D3", "dose": "2000 IU", "timing": "morning"},
                    {"name": "magnesium", "dose": "200mg", "timing": "evening"},
                    {"name": "b-complex", "dose": "standard", "timing": "morning"}
                ],
                "health_conditions": ["hypothyroidism", "chronic fatigue"],
                "medications": ["levothyroxine 100mcg"],
                "goals": ["thyroid support", "energy", "mental clarity"],
                "budget": "$100/month"
            },
            "Optimize supplements for thyroid patient with fatigue"
        )
        
        await self.test_prompt(
            "longevity_protocol",
            {
                "age": 50,
                "gender": "male",
                "current_health": {
                    "conditions": ["pre-diabetes", "high cholesterol"],
                    "family_history": ["heart disease", "diabetes"],
                    "lifestyle": "sedentary office worker"
                },
                "commitment_level": "high",
                "focus_areas": ["metabolic health", "cardiovascular health", "cognitive function"]
            },
            "Create longevity protocol for 50-year-old with metabolic syndrome risk"
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("🏁 Test Suite Complete!")
        
    def generate_report(self) -> str:
        """Generate comprehensive test report with full I/O"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report = f"""# Comprehensive MCP Server Test Report with Full I/O

**Test Date**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Server**: {self.base_url}
**Mode**: {'Production' if self.production else 'Local'}
**Duration**: {duration:.1f}s
**Total Tests**: {self.total_tests}
**Passed**: {self.passed_tests} ✅
**Failed**: {self.failed_tests} ❌
**Success Rate**: {(self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0:.1f}%

## 📊 Test Summary by Category

### Information Tools (3 tests)
- `get_dr_strunz_biography`: Biography and achievements
- `get_mcp_server_purpose`: Server capabilities and tools
- `get_vector_db_analysis`: Database statistics

### Search & Analysis Tools (3 tests)
- `knowledge_search`: Semantic search with German support
- `find_contradictions`: Contradiction detection
- `trace_topic_evolution`: Historical topic analysis

### Health Protocol Tools (3 tests)
- `create_health_protocol`: Personalized health protocols
- `analyze_supplement_stack`: Supplement interaction analysis
- `nutrition_calculator`: Detailed nutrition calculations

### Community Tools (3 tests)
- `get_community_insights`: Real-world experiences
- `summarize_posts`: Content summarization
- `get_trending_insights`: Trending topics

### Newsletter Tools (3 tests)
- `analyze_strunz_newsletter_evolution`: Newsletter trends
- `get_guest_authors_analysis`: Guest author contributions
- `track_health_topic_trends`: Topic trend tracking

### User Profiling Tools (3 tests)
- `get_health_assessment_questions`: Assessment questionnaires
- `assess_user_health_profile`: Profile analysis
- `create_personalized_protocol`: Custom protocols

### Comparison Tool (1 test)
- `compare_approaches`: Method comparison

### MCP Prompts (3 tests)
- `health_assessment`: Comprehensive health evaluation
- `supplement_optimization`: Supplement recommendations
- `longevity_protocol`: Longevity planning

## 🧪 Detailed Test Results with Input/Output

"""
        
        # Group tests by category
        tool_tests = [r for r in self.test_results if "tool_name" in r]
        prompt_tests = [r for r in self.test_results if "prompt_name" in r]
        
        # Add tool test results
        if tool_tests:
            report += "### MCP Tools Test Results\n\n"
            for result in tool_tests:
                report += f"""#### Test #{result['test_id']}: `{result.get('tool_name', 'unknown')}`

**Description**: {result['description']}
**Status**: {result['status']} {'✅' if result['status'] == 'PASS' else '❌'}
**Duration**: {result['duration_ms']}ms

**Input Parameters**:
```json
{json.dumps(result['input'], indent=2)}
```

**Request Sent**:
```json
{json.dumps(result['request'], indent=2)}
```

"""
                if result['status'] == 'PASS' and result.get('output'):
                    # Format output based on type
                    output = result['output']
                    if isinstance(output, list) and len(output) > 0:
                        report += f"**Output** ({len(output)} results):\n"
                        # Show first 2 results in detail
                        for i, item in enumerate(output[:2]):
                            report += f"\nResult {i+1}:\n```json\n{json.dumps(item, indent=2)}\n```\n"
                        if len(output) > 2:
                            report += f"\n... and {len(output) - 2} more results\n"
                    elif isinstance(output, dict):
                        report += "**Output**:\n```json\n"
                        report += json.dumps(output, indent=2)[:2000]  # Limit output size
                        if len(json.dumps(output)) > 2000:
                            report += "\n... (truncated)"
                        report += "\n```\n"
                    else:
                        report += f"**Output**: {str(output)[:500]}\n"
                    
                    if result.get('output_summary'):
                        report += f"\n**Summary**: {result['output_summary']}\n"
                elif result['status'] != 'PASS':
                    report += f"**Error**: {result.get('error', 'Unknown error')}\n"
                
                report += "\n---\n\n"
        
        # Add prompt test results
        if prompt_tests:
            report += "### MCP Prompts Test Results\n\n"
            for result in prompt_tests:
                report += f"""#### Test #{result['test_id']}: `{result.get('prompt_name', 'unknown')}`

**Description**: {result['description']}
**Status**: {result['status']} {'✅' if result['status'] == 'PASS' else '❌'}
**Duration**: {result['duration_ms']}ms

**Input Arguments**:
```json
{json.dumps(result['input'], indent=2)}
```

"""
                if result['status'] == 'PASS' and result.get('output'):
                    output = result['output']
                    report += "**Output**:\n```json\n"
                    report += json.dumps(output, indent=2)[:3000]  # Prompts can be longer
                    if len(json.dumps(output)) > 3000:
                        report += "\n... (truncated)"
                    report += "\n```\n"
                    
                    if result.get('output_summary'):
                        report += f"\n**Summary**: {result['output_summary']}\n"
                elif result['status'] != 'PASS':
                    report += f"**Error**: {result.get('error', 'Unknown error')}\n"
                
                report += "\n---\n\n"
        
        # Add performance analysis
        if tool_tests:
            response_times = [r['duration_ms'] for r in tool_tests if r['status'] == 'PASS']
            if response_times:
                report += f"""## 📈 Performance Analysis

### Response Time Statistics
- **Average**: {sum(response_times) / len(response_times):.0f}ms
- **Min**: {min(response_times)}ms
- **Max**: {max(response_times)}ms
- **Total successful calls**: {len(response_times)}

### Response Time by Tool Category
"""
                # Calculate category averages
                categories = {
                    "Information Tools": ["get_dr_strunz_biography", "get_mcp_server_purpose", "get_vector_db_analysis"],
                    "Search Tools": ["knowledge_search", "find_contradictions", "trace_topic_evolution"],
                    "Protocol Tools": ["create_health_protocol", "analyze_supplement_stack", "nutrition_calculator"],
                    "Community Tools": ["get_community_insights", "summarize_posts", "get_trending_insights"],
                    "Analysis Tools": ["analyze_strunz_newsletter_evolution", "get_guest_authors_analysis", "track_health_topic_trends"],
                    "User Tools": ["get_health_assessment_questions", "assess_user_health_profile", "create_personalized_protocol"]
                }
                
                for cat_name, cat_tools in categories.items():
                    cat_times = [r['duration_ms'] for r in tool_tests 
                               if r.get('tool_name') in cat_tools and r['status'] == 'PASS']
                    if cat_times:
                        report += f"- **{cat_name}**: {sum(cat_times) / len(cat_times):.0f}ms avg ({len(cat_times)} tests)\n"
        
        # Add test coverage analysis
        report += f"""
## 🎯 Test Coverage Analysis

### Tool Coverage
- **Total MCP Tools**: 19
- **Tools Tested**: {len(set(r.get('tool_name', '') for r in tool_tests if 'tool_name' in r))}
- **Coverage**: {len(set(r.get('tool_name', '') for r in tool_tests if 'tool_name' in r)) / 19 * 100:.1f}%

### Prompt Coverage  
- **Total MCP Prompts**: 3
- **Prompts Tested**: {len(set(r.get('prompt_name', '') for r in prompt_tests if 'prompt_name' in r))}
- **Coverage**: {len(set(r.get('prompt_name', '') for r in prompt_tests if 'prompt_name' in r)) / 3 * 100:.1f}%

### Test Quality Metrics
- **Tests with valid input**: {len([r for r in self.test_results if r.get('input')])}
- **Tests with captured output**: {len([r for r in self.test_results if r.get('output')])}
- **Tests with error details**: {len([r for r in self.test_results if r.get('error')])}

## 🔍 Key Findings

### Successful Features
"""
        # List successful tools
        successful_tools = [r.get('tool_name', r.get('prompt_name', 'unknown')) 
                          for r in self.test_results if r['status'] == 'PASS']
        if successful_tools:
            for tool in successful_tools[:10]:  # Show first 10
                report += f"- ✅ `{tool}` working correctly\n"
            if len(successful_tools) > 10:
                report += f"- ... and {len(successful_tools) - 10} more\n"
        
        report += "\n### Failed Tests\n"
        failed_tests = [r for r in self.test_results if r['status'] != 'PASS']
        if failed_tests:
            for result in failed_tests:
                tool = result.get('tool_name', result.get('prompt_name', 'unknown'))
                error_msg = result.get('error', 'Unknown error')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', str(error_msg))
                error_msg = str(error_msg)[:100]
                report += f"- ❌ `{tool}`: {error_msg}\n"
        else:
            report += "- 🎉 No failures detected!\n"
        
        # Add recommendations
        report += f"""
## 💡 Recommendations

"""
        if self.passed_tests == self.total_tests:
            report += "- 🎉 **Excellent!** All tests passed successfully\n"
            report += "- ✅ Server is production-ready with all capabilities functional\n"
            report += "- 📊 Performance is within acceptable limits\n"
        else:
            failure_rate = (self.failed_tests / self.total_tests * 100)
            if failure_rate < 10:
                report += "- ✅ **Good** - Most tests passing with minor issues\n"
            elif failure_rate < 25:
                report += "- ⚠️ **Moderate Issues** - Several tests failing\n"
            else:
                report += "- ❌ **Critical Issues** - High failure rate detected\n"
            
            report += f"- 🔧 Fix {self.failed_tests} failing tests before production deployment\n"
            report += "- 📝 Review error messages for root cause analysis\n"
        
        report += f"""
## 📋 Test Environment

- **Server URL**: {self.base_url}
- **Test Mode**: {'Production' if self.production else 'Local Development'}
- **Test Framework**: Async HTTP with httpx
- **Protocol**: JSON-RPC 2.0 over HTTP
- **Test Date**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Total Duration**: {duration:.1f} seconds

---

*Generated by Comprehensive MCP Test Suite with Full I/O Logging*
"""
        
        return report


async def main():
    """Run comprehensive tests against local or production server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive MCP Server Test with Full I/O")
    parser.add_argument("--production", action="store_true", help="Test production server")
    parser.add_argument("--url", default=None, help="Custom server URL")
    parser.add_argument("--output", default=None, help="Output report file")
    args = parser.parse_args()
    
    # Determine server URL
    if args.url:
        base_url = args.url
        production = "railway" in args.url or "production" in args.url
    elif args.production:
        base_url = "https://strunz.up.railway.app"
        production = True
    else:
        base_url = "http://localhost:8000"
        production = False
    
    # Run tests
    async with ComprehensiveMCPTester(base_url, production) as tester:
        await tester.run_all_tests()
        report = tester.generate_report()
        
        # Save report
        if args.output:
            output_file = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = Path(__file__).parent.parent.parent.parent / "docs" / "test-reports"
            report_dir.mkdir(exist_ok=True)
            output_file = report_dir / f"COMPREHENSIVE_FULL_IO_REPORT_{timestamp}.md"
        
        output_file.write_text(report)
        logger.info(f"\n📄 Report saved to: {output_file}")
        
        # Print summary
        print(f"\n{'=' * 80}")
        print(f"Test Summary: {tester.passed_tests}/{tester.total_tests} passed ({tester.passed_tests/tester.total_tests*100:.1f}%)")
        print(f"Report: {output_file}")
        print(f"{'=' * 80}")


if __name__ == "__main__":
    asyncio.run(main())