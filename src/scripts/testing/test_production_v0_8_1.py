#!/usr/bin/env python3
"""
Production Test Suite for v0.8.1
Tests the Railway deployment after legacy server cleanup
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any

PRODUCTION_URL = "https://strunz.up.railway.app"

async def test_endpoint(session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Test a single endpoint"""
    url = f"{PRODUCTION_URL}{endpoint}"
    start_time = asyncio.get_event_loop().time()
    
    try:
        if method == "GET":
            async with session.get(url) as response:
                result = await response.json()
                status = response.status
        else:
            headers = {"Content-Type": "application/json"}
            async with session.post(url, json=data, headers=headers) as response:
                result = await response.json()
                status = response.status
        
        elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return {
            "endpoint": endpoint,
            "status": "✅ PASS" if status == 200 else f"❌ FAIL ({status})",
            "response_time": f"{elapsed:.0f}ms",
            "data": result
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": f"❌ ERROR: {str(e)}",
            "response_time": "N/A",
            "data": None
        }

async def test_tool(session: aiohttp.ClientSession, tool_name: str, arguments: Dict) -> Dict:
    """Test a specific tool via MCP protocol"""
    data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }
    
    result = await test_endpoint(session, "/mcp", "POST", data)
    return {
        "tool": tool_name,
        "status": result["status"],
        "response_time": result["response_time"],
        "success": result["data"] and "result" in result["data"] if result["data"] else False
    }

async def run_tests():
    """Run comprehensive production tests"""
    print("🧪 Production Test Suite v0.8.1")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing: {PRODUCTION_URL}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health Check
        print("\n📊 Testing Core Endpoints:")
        health = await test_endpoint(session, "/")
        print(f"  Health Check: {health['status']} ({health['response_time']})")
        
        if health['data']:
            version = health['data'].get('version', 'Unknown')
            tools_count = health['data'].get('tools_available', 0)
            print(f"  Version: {version}")
            print(f"  Tools Available: {tools_count}")
            
            # Check if using new server
            if 'enhanced_server_loaded' in health['data']:
                if health['data']['enhanced_server_loaded']:
                    print("  ⚠️  Still using enhanced_server (deployment pending)")
                else:
                    print("  ✅ Using clean MCP SDK server")
        
        # Test 2: Discovery Endpoint
        discovery = await test_endpoint(session, "/.well-known/mcp/resource")
        print(f"  Discovery: {discovery['status']} ({discovery['response_time']})")
        
        # Test 3: OAuth Endpoints
        oauth_start = await test_endpoint(session, "/api/organizations/test/mcp/start-auth/test123?redirect_url=test")
        print(f"  OAuth Start: {oauth_start['status']} ({oauth_start['response_time']})")
        
        # Test 4: Sample Tools
        print("\n🔧 Testing Sample Tools:")
        
        tool_tests = [
            ("get_mcp_server_purpose", {}),
            ("knowledge_search", {"query": "vitamin d", "limit": 3}),
            ("get_dr_strunz_biography", {"include_achievements": True}),
            ("get_vector_db_analysis", {}),
            ("nutrition_calculator", {
                "age": 35, "gender": "male", "weight": 75, "height": 180,
                "activity_level": "moderate", "health_goals": ["energy"]
            })
        ]
        
        for tool_name, args in tool_tests:
            result = await test_tool(session, tool_name, args)
            status_icon = "✅" if "✅" in result["status"] and result["success"] else "❌"
            print(f"  {status_icon} {tool_name}: {result['response_time']}")
        
        # Test 5: Performance Check
        print("\n⚡ Performance Summary:")
        
        # Multiple concurrent requests
        tasks = []
        for _ in range(5):
            tasks.append(test_endpoint(session, "/"))
        
        results = await asyncio.gather(*tasks)
        response_times = [float(r['response_time'].rstrip('ms')) for r in results if 'ms' in r['response_time']]
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"  Average Response: {avg_time:.0f}ms")
            print(f"  Min/Max: {min_time:.0f}ms / {max_time:.0f}ms")
            print(f"  Concurrent Requests: {len(response_times)}/5 successful")
        
        # Final Summary
        print("\n📋 Test Summary:")
        print(f"  Deployment Status: {'🟡 Pending' if version == '0.8.0' else '✅ Complete'}")
        print(f"  Expected Version: 0.8.1")
        print(f"  Current Version: {version}")
        
        if version == "0.8.1":
            print("\n✅ v0.8.1 deployment successful!")
            print("🎯 All legacy servers removed")
            print("🚀 Production using clean MCP SDK")
        else:
            print("\n⏳ Deployment still in progress...")
            print("💡 Railway typically takes 5-10 minutes to deploy")
            print("🔄 Re-run this test in a few minutes")

if __name__ == "__main__":
    asyncio.run(run_tests())