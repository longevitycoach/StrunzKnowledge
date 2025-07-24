#!/usr/bin/env python3
"""
Direct test of MCP SDK clean server functionality
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.mcp.mcp_sdk_clean import StrunzKnowledgeServer

async def test_direct():
    """Test the server directly without MCP protocol"""
    print("=== Direct MCP SDK Server Test ===\n")
    
    # Create server
    server = StrunzKnowledgeServer()
    await server._init_vector_store()
    
    print("✓ Server initialized\n")
    
    # Test results
    passed = 0
    failed = 0
    
    # Test 1: List tools
    print("### Testing Tool Discovery ###")
    try:
        # Call the decorated function directly
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} tools")
        print(f"   Tools: {', '.join([t.name for t in tools[:5]])}...")
        passed += 1
    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        failed += 1
    
    # Test 2: Call a simple tool
    print("\n### Testing Simple Tool Call ###")
    try:
        result = await server.call_tool("get_mcp_server_purpose", {})
        if result and len(result) > 0:
            print(f"✅ get_mcp_server_purpose: Success")
            print(f"   Response length: {len(result[0].text)} chars")
            passed += 1
        else:
            print(f"❌ get_mcp_server_purpose: Empty response")
            failed += 1
    except Exception as e:
        print(f"❌ get_mcp_server_purpose failed: {e}")
        failed += 1
    
    # Test 3: Call tool with parameters
    print("\n### Testing Tool with Parameters ###")
    try:
        result = await server.call_tool("knowledge_search", {"query": "vitamin d optimal levels"})
        if result and len(result) > 0:
            print(f"✅ knowledge_search: Success")
            print(f"   Response contains: {'vitamin' in result[0].text.lower()}")
            passed += 1
        else:
            print(f"❌ knowledge_search: Empty response")
            failed += 1
    except Exception as e:
        print(f"❌ knowledge_search failed: {e}")
        failed += 1
    
    # Test 4: Test all tools quickly
    print("\n### Testing All Tools ###")
    test_params = {
        "knowledge_search": {"query": "test"},
        "find_contradictions": {"topic": "test"},
        "trace_topic_evolution": {"topic": "test"},
        "create_health_protocol": {"condition": "test", "age": 40, "gender": "male"},
        "analyze_supplement_stack": {"supplements": ["test"]},
        "nutrition_calculator": {"weight": 70, "goal": "test"},
        "get_community_insights": {"topic": "test"},
        "summarize_posts": {"category": "test"},
        "get_trending_insights": {},
        "analyze_strunz_newsletter_evolution": {},
        "get_guest_authors_analysis": {},
        "track_health_topic_trends": {"topic": "test"},
        "get_health_assessment_questions": {},
        "get_dr_strunz_biography": {},
        "get_mcp_server_purpose": {},
        "get_vector_db_analysis": {},
        "compare_approaches": {"health_issue": "test", "alternative_approaches": ["test"]},
        "get_optimal_diagnostic_values": {"age": 40, "gender": "male"},
        "assess_user_health_profile": {"responses": {}},
        "create_personalized_protocol": {"user_profile": {}},
        "get_dr_strunz_info": {}
    }
    
    for tool_name, params in test_params.items():
        try:
            result = await server.call_tool(tool_name, params)
            if result and len(result) > 0:
                print(f"✅ {tool_name}")
                passed += 1
            else:
                print(f"❌ {tool_name}: Empty response")
                failed += 1
        except Exception as e:
            print(f"❌ {tool_name}: {str(e)[:50]}...")
            failed += 1
    
    # Test 5: Test prompts
    print("\n### Testing Prompts ###")
    try:
        prompts = await server.list_prompts()
        print(f"✅ Found {len(prompts)} prompts")
        passed += 1
        
        # Test getting a prompt
        prompt_result = await server.get_prompt("health_assessment", {})
        if prompt_result:
            print(f"✅ Retrieved health_assessment prompt")
            passed += 1
        else:
            print(f"❌ Failed to retrieve prompt")
            failed += 1
    except Exception as e:
        print(f"❌ Prompt testing failed: {e}")
        failed += 1
    
    # Summary
    total = passed + failed
    print(f"\n=== Summary ===")
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed}")
    
    # Generate report
    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed/total*100:.1f}%"
    }
    
    report_path = f"src/tests/reports/mcp_sdk_direct_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = asyncio.run(test_direct())
    sys.exit(0 if failed == 0 else 1)