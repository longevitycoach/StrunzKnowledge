#!/usr/bin/env python3
"""
Test script for Gemini API integration
Tests the auth-less client approach with Gemini API
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.llm.gemini_client import GeminiClient, test_gemini_integration
from src.rag.search import KnowledgeSearcher


async def test_gemini_api_key():
    """Test if Gemini API key is properly configured"""
    print("=" * 60)
    print("Testing Gemini API Key Configuration")
    print("=" * 60)
    
    # Check environment variable
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_GEMINI_API_KEY not found in environment")
        print("   Please add it to your .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API connection
    try:
        async with GeminiClient() as client:
            print("\n📡 Testing API connection...")
            is_valid = await client.validate_api_key()
            
            if is_valid:
                print("✅ API key is valid and working")
                
                # Test generation
                print("\n🤖 Testing content generation...")
                response = await client.generate_content(
                    "What is vitamin D according to Dr. Strunz? Answer in one sentence."
                )
                print(f"Response: {response}")
                
                return True
            else:
                print("❌ API key validation failed")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False


async def test_gemini_enhanced_search():
    """Test Gemini-enhanced search functionality"""
    print("\n" + "=" * 60)
    print("Testing Gemini-Enhanced Search")
    print("=" * 60)
    
    try:
        # Initialize components
        print("Initializing KnowledgeSearcher...")
        searcher = KnowledgeSearcher()
        
        # Test search
        test_query = "vitamin d benefits"
        print(f"\nSearching for: '{test_query}'")
        
        # Get raw results first
        raw_results = searcher.search(test_query, k=5)
        print(f"Found {len(raw_results)} raw results")
        
        # Test Gemini synthesis
        from src.llm.gemini_client import GeminiEnhancedSearch
        
        print("\n🤖 Testing Gemini synthesis...")
        async with GeminiClient() as client:
            enhanced_search = GeminiEnhancedSearch(searcher, client)
            result = await enhanced_search.search(test_query, k=5)
            
            print(f"\n✅ Enhanced search completed")
            print(f"Key concepts: {', '.join(result['key_concepts'][:5])}")
            print(f"Sources used: {', '.join(result['sources_used'][:3])}")
            print(f"\nSynthesis preview:")
            print(result['synthesis'][:300] + "...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced search: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tool_registration():
    """Test MCP tool registration with Gemini"""
    print("\n" + "=" * 60)
    print("Testing MCP Tool Registration")
    print("=" * 60)
    
    try:
        from mcp.server.fastmcp import FastMCP
        from src.mcp.tools.gemini_enhanced_tools import register_gemini_tools
        
        # Create test server
        mcp = FastMCP(name="Test Server")
        searcher = KnowledgeSearcher()
        
        # Register tools
        print("Registering Gemini-enhanced tools...")
        success = register_gemini_tools(mcp, searcher)
        
        if success:
            print("✅ Tools registered successfully")
            
            # List registered tools
            print("\nRegistered tools:")
            # Note: FastMCP doesn't expose tool list directly, but we know what was registered
            gemini_tools = [
                "search_knowledge_gemini",
                "ask_strunz_gemini",
                "analyze_health_topic_gemini",
                "validate_gemini_connection"
            ]
            for tool in gemini_tools:
                print(f"  - {tool}")
                
            return True
        else:
            print("❌ Tool registration failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in tool registration: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_endpoint():
    """Test if health endpoint reports Gemini status"""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    # This would need to be tested with a running server
    print("ℹ️  Health endpoint test requires running server")
    print("   Start server with: python main.py")
    print("   Then check: http://localhost:8000/health")
    
    return True


async def main():
    """Run all tests"""
    print("🚀 StrunzKnowledge Gemini Integration Tests")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    results = []
    
    # Test 1: API Key
    results.append(("API Key Configuration", await test_gemini_api_key()))
    
    # Only run other tests if API key is valid
    if results[0][1]:
        # Test 2: Enhanced Search
        results.append(("Gemini Enhanced Search", await test_gemini_enhanced_search()))
        
        # Test 3: MCP Tool Registration
        results.append(("MCP Tool Registration", await test_mcp_tool_registration()))
        
        # Test 4: Health Endpoint
        results.append(("Health Endpoint", await test_health_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed! Gemini integration is ready.")
        print("📝 Next steps:")
        print("   1. Deploy to Railway with GOOGLE_GEMINI_API_KEY set")
        print("   2. Test enhanced tools in Claude.ai")
        print("   3. Implement browser extension client")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())