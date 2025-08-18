#!/usr/bin/env python3
"""
Test streaming implementation locally
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_streaming():
    """Test the streaming analyzer implementation"""
    
    print("🔬 Testing Streaming Implementation")
    print("=" * 60)
    
    # Initialize the tools
    from src.rag.search import KnowledgeSearcher
    from src.mcp.streaming_analyzer import StreamingAnalyzer
    
    print("Initializing knowledge searcher...")
    search_tool = KnowledgeSearcher()
    
    print("Creating streaming analyzer...")
    analyzer = StreamingAnalyzer(search_tool)
    
    # Test streaming with comprehensive analysis
    topic = "Magnesium"
    depth = "comprehensive"
    
    print(f"\n📊 Testing: {topic} (depth: {depth})")
    print("-" * 40)
    
    start_time = time.time()
    chunk_count = 0
    final_result = None
    
    try:
        async for chunk in analyzer.analyze_health_topic_streaming(topic, depth):
            chunk_count += 1
            elapsed = time.time() - start_time
            
            chunk_type = chunk.get("type", "unknown")
            status = chunk.get("status", "unknown")
            progress = chunk.get("progress", 0)
            message = chunk.get("message", "")
            
            print(f"[{elapsed:.2f}s] Chunk {chunk_count}: {chunk_type}/{status} - {progress}% - {message}")
            
            if chunk_type == "complete":
                final_result = chunk.get("data", {}).get("result", "No result")
                print(f"\n✅ Streaming complete in {elapsed:.2f} seconds")
                print(f"Total chunks received: {chunk_count}")
                
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Error after {elapsed:.2f}s: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Display final result summary
    if final_result:
        print("\n📋 Final Result Preview:")
        print("-" * 40)
        print(final_result[:500] + "..." if len(final_result) > 500 else final_result)
    
    print("\n" + "=" * 60)
    print("✅ Test Complete")
    
    # Test timing requirements
    total_time = time.time() - start_time
    if total_time < 10:
        print(f"✅ PASS: Completed in {total_time:.2f}s (under 10s limit)")
    else:
        print(f"❌ FAIL: Took {total_time:.2f}s (exceeds 10s limit)")

async def test_regular_vs_streaming():
    """Compare regular vs streaming implementation"""
    
    print("\n🔄 Comparing Regular vs Streaming")
    print("=" * 60)
    
    from src.rag.search import KnowledgeSearcher
    from src.mcp.batch2_health_tools import HealthAssessmentTools
    
    search_tool = KnowledgeSearcher()
    health_tools = HealthAssessmentTools(search_tool)
    
    # Test different depths
    for depth in ["basic", "moderate", "comprehensive"]:
        print(f"\n📊 Testing depth: {depth}")
        print("-" * 40)
        
        start_time = time.time()
        try:
            result = await health_tools.analyze_health_topic("Vitamin D", depth)
            elapsed = time.time() - start_time
            
            print(f"✅ {depth}: {elapsed:.2f}s - Result length: {len(result)} chars")
            
            if elapsed > 10 and depth == "comprehensive":
                print("  ⚠️ Warning: Exceeds 10s timeout limit")
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ {depth}: Failed after {elapsed:.2f}s - {str(e)}")

async def main():
    """Run all tests"""
    print("\n🚀 Streaming Implementation Test Suite")
    print("=" * 60)
    
    # Test 1: Streaming functionality
    await test_streaming()
    
    # Test 2: Compare implementations
    await test_regular_vs_streaming()
    
    print("\n" + "=" * 60)
    print("🎯 All tests completed")

if __name__ == "__main__":
    asyncio.run(main())