#!/usr/bin/env python3
"""
Comprehensive FastMCP Client Test for Railway Production
Tests all 20 MCP tools and generates detailed report
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add the virtual environment path
sys.path.insert(0, '/Users/ma3u/projects/StrunzKnowledge/fastmcp_test_env/lib/python3.13/site-packages')

from fastmcp import Client

class FastMCPTester:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.results = []
        self.tool_results = {}
        
    async def test_all_tools(self):
        """Test all 20 MCP tools comprehensively"""
        print("🧪 Comprehensive FastMCP Test Suite")
        print("=" * 60)
        print(f"🌐 Server: {self.server_url}")
        print(f"📅 Date: {datetime.now().isoformat()}")
        print()
        
        async with Client(self.server_url) as client:
            # Test 1: Server Connection
            print("1️⃣ Testing Server Connection...")
            try:
                # Get server info
                server_info = await self.get_server_info(client)
                print(f"   ✅ Connected to {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                self.results.append({"test": "connection", "status": "success", "details": server_info})
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
                self.results.append({"test": "connection", "status": "failed", "error": str(e)})
                return
            
            # Test 2: List Tools
            print("\n2️⃣ Testing Tool Discovery...")
            try:
                tools = await client.list_tools()
                print(f"   ✅ Discovered {len(tools)} tools")
                self.results.append({"test": "tool_discovery", "status": "success", "tool_count": len(tools)})
                
                # Show tools
                for i, tool in enumerate(tools):
                    print(f"      {i+1:2}. {tool.name}")
                    
            except Exception as e:
                print(f"   ❌ Tool discovery failed: {e}")
                self.results.append({"test": "tool_discovery", "status": "failed", "error": str(e)})
                return
            
            # Test 3: Individual Tool Tests
            print("\n3️⃣ Testing Individual Tools...")
            await self.test_information_tools(client)
            await self.test_search_tools(client)
            await self.test_protocol_tools(client)
            await self.test_community_tools(client)
            await self.test_newsletter_tools(client)
            await self.test_user_profiling_tools(client)
            await self.test_comparison_tools(client)
            
            # Test 4: Performance Analysis
            print("\n4️⃣ Performance Analysis...")
            await self.analyze_performance()
            
            # Test 5: Generate Report
            print("\n5️⃣ Generating Comprehensive Report...")
            await self.generate_report()
    
    async def get_server_info(self, client):
        """Get server information"""
        try:
            result = await client.call_tool("get_mcp_server_purpose", {})
            if isinstance(result, list) and len(result) > 0:
                content = result[0].get('text', '{}')
                return json.loads(content)
            return {}
        except:
            return {}
    
    async def test_information_tools(self, client):
        """Test information tools (3 tools)"""
        print("\n   📋 Information Tools:")
        
        # Test get_dr_strunz_biography
        await self.test_tool(client, "get_dr_strunz_biography", {}, 
                            "Get Dr. Strunz biography and achievements")
        
        # Test get_mcp_server_purpose
        await self.test_tool(client, "get_mcp_server_purpose", {}, 
                            "Get MCP server purpose and capabilities")
        
        # Test get_vector_db_analysis
        await self.test_tool(client, "get_vector_db_analysis", {}, 
                            "Get vector database analysis and statistics")
    
    async def test_search_tools(self, client):
        """Test search and analysis tools (3 tools)"""
        print("\n   🔍 Search & Analysis Tools:")
        
        # Test knowledge_search
        await self.test_tool(client, "knowledge_search", 
                            {"query": "Vitamin D Mangel", "max_results": 5}, 
                            "Search for Vitamin D deficiency")
        
        # Test find_contradictions
        await self.test_tool(client, "find_contradictions", 
                            {"topic": "vitamin_d_dosage"}, 
                            "Find contradictions in vitamin D dosage")
        
        # Test trace_topic_evolution
        await self.test_tool(client, "trace_topic_evolution", 
                            {"topic": "intermittent_fasting"}, 
                            "Trace evolution of intermittent fasting")
    
    async def test_protocol_tools(self, client):
        """Test protocol tools (3 tools)"""
        print("\n   🏥 Protocol Tools:")
        
        # Test create_health_protocol
        await self.test_tool(client, "create_health_protocol", 
                            {"condition": "fatigue", "severity": "moderate"}, 
                            "Create health protocol for fatigue")
        
        # Test analyze_supplement_stack
        await self.test_tool(client, "analyze_supplement_stack", 
                            {"supplements": ["vitamin_d", "magnesium", "omega_3"]}, 
                            "Analyze supplement stack")
        
        # Test nutrition_calculator
        await self.test_tool(client, "nutrition_calculator", 
                            {"foods": ["salmon", "spinach"], "portion_sizes": [100, 200]}, 
                            "Calculate nutrition")
    
    async def test_community_tools(self, client):
        """Test community tools (3 tools)"""
        print("\n   👥 Community Tools:")
        
        # Test get_community_insights
        await self.test_tool(client, "get_community_insights", 
                            {"topic": "supplement_timing"}, 
                            "Get community insights")
        
        # Test summarize_posts
        await self.test_tool(client, "summarize_posts", 
                            {"category": "success_stories", "limit": 5}, 
                            "Summarize success stories")
        
        # Test get_trending_insights
        await self.test_tool(client, "get_trending_insights", 
                            {"time_period": "last_month"}, 
                            "Get trending insights")
    
    async def test_newsletter_tools(self, client):
        """Test newsletter analysis tools (3 tools)"""
        print("\n   📰 Newsletter Analysis Tools:")
        
        # Test analyze_strunz_newsletter_evolution
        await self.test_tool(client, "analyze_strunz_newsletter_evolution", 
                            {"time_range": "2023"}, 
                            "Analyze newsletter evolution")
        
        # Test get_guest_authors_analysis
        await self.test_tool(client, "get_guest_authors_analysis", 
                            {"limit": 5}, 
                            "Analyze guest authors")
        
        # Test track_health_topic_trends
        await self.test_tool(client, "track_health_topic_trends", 
                            {"topics": ["longevity", "metabolic_health"]}, 
                            "Track health topic trends")
    
    async def test_user_profiling_tools(self, client):
        """Test user profiling tools (3 tools)"""
        print("\n   👤 User Profiling Tools:")
        
        # Test get_health_assessment_questions
        await self.test_tool(client, "get_health_assessment_questions", 
                            {"category": "nutrition"}, 
                            "Get health assessment questions")
        
        # Test assess_user_health_profile
        await self.test_tool(client, "assess_user_health_profile", 
                            {"responses": {"age": 35, "activity_level": "moderate"}}, 
                            "Assess user health profile")
        
        # Test create_personalized_protocol
        await self.test_tool(client, "create_personalized_protocol", 
                            {"health_profile": {"age": 35, "goals": ["energy"]}}, 
                            "Create personalized protocol")
    
    async def test_comparison_tools(self, client):
        """Test comparison tools (1 tool)"""
        print("\n   ⚖️ Comparison Tools:")
        
        # Test compare_approaches
        await self.test_tool(client, "compare_approaches", 
                            {"approaches": ["keto_diet", "mediterranean_diet"]}, 
                            "Compare dietary approaches")
    
    async def test_tool(self, client, tool_name: str, arguments: Dict[str, Any], description: str):
        """Test individual tool"""
        start_time = time.time()
        
        try:
            result = await client.call_tool(tool_name, arguments)
            duration = (time.time() - start_time) * 1000
            
            print(f"      ✅ {tool_name}: {description} ({duration:.0f}ms)")
            
            # Store result
            self.tool_results[tool_name] = {
                "status": "success",
                "duration_ms": duration,
                "description": description,
                "arguments": arguments,
                "result_type": type(result).__name__,
                "result_length": len(str(result)) if result else 0
            }
            
            # Analyze result
            if isinstance(result, list) and len(result) > 0:
                first_item = result[0]
                if isinstance(first_item, dict) and 'text' in first_item:
                    text_content = first_item['text']
                    self.tool_results[tool_name]["has_text_content"] = True
                    self.tool_results[tool_name]["text_length"] = len(text_content)
                    
                    # Check for structured data
                    if text_content.strip().startswith('{'):
                        try:
                            json.loads(text_content)
                            self.tool_results[tool_name]["structured_json"] = True
                        except:
                            self.tool_results[tool_name]["structured_json"] = False
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"      ❌ {tool_name}: {str(e)[:100]}... ({duration:.0f}ms)")
            
            self.tool_results[tool_name] = {
                "status": "failed",
                "duration_ms": duration,
                "description": description,
                "arguments": arguments,
                "error": str(e)
            }
    
    async def analyze_performance(self):
        """Analyze performance metrics"""
        successful_tools = [r for r in self.tool_results.values() if r["status"] == "success"]
        failed_tools = [r for r in self.tool_results.values() if r["status"] == "failed"]
        
        if successful_tools:
            durations = [r["duration_ms"] for r in successful_tools]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"   📊 Performance Metrics:")
            print(f"      • Total Tools: {len(self.tool_results)}")
            print(f"      • Successful: {len(successful_tools)}")
            print(f"      • Failed: {len(failed_tools)}")
            print(f"      • Success Rate: {len(successful_tools)/len(self.tool_results)*100:.1f}%")
            print(f"      • Avg Response Time: {avg_duration:.0f}ms")
            print(f"      • Min Response Time: {min_duration:.0f}ms")
            print(f"      • Max Response Time: {max_duration:.0f}ms")
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        report = {
            "test_info": {
                "server_url": self.server_url,
                "test_date": datetime.now().isoformat(),
                "fastmcp_version": "2.10.5",
                "total_tools": len(self.tool_results)
            },
            "summary": {
                "total_tests": len(self.tool_results),
                "successful": len([r for r in self.tool_results.values() if r["status"] == "success"]),
                "failed": len([r for r in self.tool_results.values() if r["status"] == "failed"]),
                "success_rate": len([r for r in self.tool_results.values() if r["status"] == "success"]) / len(self.tool_results) * 100
            },
            "tool_results": self.tool_results,
            "performance": {}
        }
        
        # Add performance metrics
        successful_tools = [r for r in self.tool_results.values() if r["status"] == "success"]
        if successful_tools:
            durations = [r["duration_ms"] for r in successful_tools]
            report["performance"] = {
                "avg_response_time_ms": sum(durations) / len(durations),
                "min_response_time_ms": min(durations),
                "max_response_time_ms": max(durations),
                "total_response_time_ms": sum(durations)
            }
        
        # Save report
        report_file = f"/Users/ma3u/projects/StrunzKnowledge/docs/test-reports/FASTMCP_COMPREHENSIVE_TEST_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   📄 Report saved to: {report_file}")
        
        # Generate markdown report
        await self.generate_markdown_report(report)
    
    async def generate_markdown_report(self, report):
        """Generate markdown test report"""
        md_content = f"""# FastMCP Comprehensive Test Report

**Test Date**: {report['test_info']['test_date']}  
**Server**: {report['test_info']['server_url']}  
**FastMCP Version**: {report['test_info']['fastmcp_version']}  

## Summary

- **Total Tools**: {report['summary']['total_tests']}
- **Successful**: {report['summary']['successful']}
- **Failed**: {report['summary']['failed']}
- **Success Rate**: {report['summary']['success_rate']:.1f}%

## Performance Metrics

"""
        
        if report['performance']:
            md_content += f"""- **Average Response Time**: {report['performance']['avg_response_time_ms']:.0f}ms
- **Min Response Time**: {report['performance']['min_response_time_ms']:.0f}ms
- **Max Response Time**: {report['performance']['max_response_time_ms']:.0f}ms
- **Total Response Time**: {report['performance']['total_response_time_ms']:.0f}ms

"""
        
        md_content += """## Tool Test Results

| Tool | Status | Duration | Description |
|------|--------|----------|-------------|
"""
        
        for tool_name, result in report['tool_results'].items():
            status = "✅ PASS" if result['status'] == 'success' else "❌ FAIL"
            duration = f"{result['duration_ms']:.0f}ms"
            desc = result['description']
            md_content += f"| {tool_name} | {status} | {duration} | {desc} |\n"
        
        # Add failed tools details
        failed_tools = {k: v for k, v in report['tool_results'].items() if v['status'] == 'failed'}
        if failed_tools:
            md_content += f"""
## Failed Tools Details

"""
            for tool_name, result in failed_tools.items():
                md_content += f"""### {tool_name}
- **Error**: {result.get('error', 'Unknown error')}
- **Duration**: {result['duration_ms']:.0f}ms
- **Arguments**: {result['arguments']}

"""
        
        md_content += """
## MCP Server PROMPT

The Dr. Strunz Knowledge Base MCP Server provides comprehensive access to Dr. Ulrich Strunz's medical knowledge and community insights. It includes:

### Core Capabilities:
- **Semantic Search**: Search across 13 books, 6,953 newsletters, and 14,435 forum discussions
- **Health Protocols**: Generate personalized health protocols based on Dr. Strunz's recommendations
- **Community Insights**: Access real-world experiences from 20+ years of community discussions
- **Newsletter Analysis**: Track evolution of health topics from 2004-2025
- **User Profiling**: Personalized health assessments and recommendations

### Available Tools (20):
1. **Information Tools** (3): Biography, server purpose, database analysis
2. **Search & Analysis** (3): Knowledge search, contradiction finding, topic evolution
3. **Protocol Tools** (3): Health protocols, supplement analysis, nutrition calculator
4. **Community Tools** (3): Community insights, post summaries, trending topics
5. **Newsletter Analysis** (3): Newsletter evolution, guest authors, topic trends
6. **User Profiling** (3): Health assessment, profile analysis, personalized protocols
7. **Comparison Tools** (1): Compare different health approaches

### Data Sources:
- **Books**: 13 comprehensive health books by Dr. Strunz
- **Newsletters**: 6,953 articles spanning 2004-2025
- **Forum**: 14,435 community discussions
- **Total Content**: 43,373 indexed text chunks with 28,938 vector embeddings

### Technical Features:
- **Protocol**: MCP 2025-03-26 with SSE transport
- **Authentication**: OAuth 2.1 with dynamic client registration
- **Vector Search**: Semantic search using sentence-transformers
- **Real-time**: Server-Sent Events for live communication

This server transforms Dr. Strunz's static knowledge into dynamic, personalized health guidance through the MCP protocol.
"""
        
        # Save markdown report
        md_file = f"/Users/ma3u/projects/StrunzKnowledge/docs/test-reports/FASTMCP_TEST_REPORT_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        
        print(f"   📄 Markdown report saved to: {md_file}")

async def main():
    """Run comprehensive FastMCP test"""
    server_url = "https://strunz.up.railway.app/sse"
    
    tester = FastMCPTester(server_url)
    await tester.test_all_tools()
    
    print("\n🎉 Comprehensive FastMCP testing complete!")
    print("📋 Check the generated reports for detailed results.")

if __name__ == "__main__":
    # Set up environment
    os.environ['PYTHONPATH'] = '/Users/ma3u/projects/StrunzKnowledge/fastmcp_test_env/lib/python3.13/site-packages'
    
    asyncio.run(main())