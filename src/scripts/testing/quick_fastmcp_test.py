#!/usr/bin/env python3
"""
Quick FastMCP test to verify connection and basic functionality
"""
import asyncio
import json
import time
from datetime import datetime

# Add virtual environment to path
import sys
sys.path.insert(0, '/Users/ma3u/projects/StrunzKnowledge/fastmcp_test_env/lib/python3.13/site-packages')

from fastmcp import Client

async def quick_test():
    """Quick test of FastMCP connection"""
    server_url = "https://strunz.up.railway.app/sse"
    
    print("🧪 Quick FastMCP Connection Test")
    print(f"🌐 Server: {server_url}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        async with Client(server_url) as client:
            print("✅ FastMCP client connected successfully!")
            
            # Test 1: List tools
            print("\n📋 Testing tool discovery...")
            tools = await client.list_tools()
            print(f"✅ Found {len(tools)} tools")
            
            # Show first 10 tools
            for i, tool in enumerate(tools[:10]):
                print(f"   {i+1:2}. {tool.name}")
            if len(tools) > 10:
                print(f"   ... and {len(tools) - 10} more tools")
            
            # Test 2: Simple tool call
            print("\n🔧 Testing simple tool call...")
            start_time = time.time()
            result = await client.call_tool("get_mcp_server_purpose", {})
            duration = (time.time() - start_time) * 1000
            
            print(f"✅ Tool call successful ({duration:.0f}ms)")
            print(f"   Result type: {type(result)}")
            
            if isinstance(result, list) and len(result) > 0:
                first_item = result[0]
                if isinstance(first_item, dict) and 'text' in first_item:
                    text_content = first_item['text']
                    print(f"   Content length: {len(text_content)} characters")
                    
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(text_content)
                        print(f"   Server: {parsed.get('server_name', 'Unknown')}")
                        print(f"   Version: {parsed.get('version', 'Unknown')}")
                        print(f"   Tools: {parsed.get('capabilities', {}).get('tools_available', 'Unknown')}")
                    except:
                        print(f"   Content preview: {text_content[:100]}...")
            
            # Test 3: Knowledge search
            print("\n🔍 Testing knowledge search...")
            start_time = time.time()
            search_result = await client.call_tool("knowledge_search", {
                "query": "Vitamin D",
                "max_results": 3
            })
            duration = (time.time() - start_time) * 1000
            
            print(f"✅ Search successful ({duration:.0f}ms)")
            print(f"   Search result type: {type(search_result)}")
            
            if isinstance(search_result, list) and len(search_result) > 0:
                first_item = search_result[0]
                if isinstance(first_item, dict) and 'text' in first_item:
                    text_content = first_item['text']
                    print(f"   Search content length: {len(text_content)} characters")
                    
                    # Try to parse search results
                    try:
                        parsed = json.loads(text_content)
                        if 'results' in parsed:
                            results = parsed['results']
                            print(f"   Found {len(results)} search results")
                            for i, result in enumerate(results[:3]):
                                score = result.get('score', 0)
                                content = result.get('content', '')[:50]
                                print(f"      {i+1}. Score: {score:.3f} - {content}...")
                    except:
                        print(f"   Search preview: {text_content[:100]}...")
            
            print("\n🎉 Quick FastMCP test completed successfully!")
            
    except Exception as e:
        print(f"❌ FastMCP test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())