#!/usr/bin/env python3
"""
Test Enhanced Server Initialization
Diagnose why enhanced server is not initializing properly
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_server_init():
    """Test enhanced server initialization step by step"""
    print("🔍 Testing Enhanced Server Initialization...")
    
    try:
        # Test import
        print("📦 Testing import...")
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        print("✅ Import successful")
        
        # Test initialization
        print("🚀 Testing initialization...")
        server = StrunzKnowledgeMCP()
        print(f"✅ Server initialized successfully")
        print(f"📊 Tools registered: {len(server.tool_registry)}")
        
        # List all tools
        print("\n🛠️ Available tools:")
        for i, (name, tool) in enumerate(server.tool_registry.items(), 1):
            print(f"  {i:2d}. {name}")
        
        # Test vector store
        print(f"\n🗂️ Vector store available: {server.HAS_VECTOR_STORE}")
        if server.searcher:
            print("✅ Vector store searcher initialized")
        else:
            print("❌ Vector store searcher not available")
        
        # Test user profiling
        print(f"👤 User profiling available: {server.profiling is not None}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastmcp_availability():
    """Test FastMCP availability"""
    print("\n📦 Testing FastMCP availability...")
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP is available")
        return True
    except ImportError as e:
        print(f"❌ FastMCP not available: {e}")
        return False

def test_vector_store():
    """Test vector store availability"""
    print("\n🗂️ Testing Vector Store...")
    try:
        from src.rag.search import KnowledgeSearcher
        searcher = KnowledgeSearcher()
        print("✅ Vector store searcher available")
        return True
    except Exception as e:
        print(f"❌ Vector store not available: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ENHANCED SERVER INITIALIZATION TEST")
    print("=" * 60)
    
    # Test components
    fastmcp_ok = test_fastmcp_availability()
    vector_ok = test_vector_store()
    server_ok = test_enhanced_server_init()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"FastMCP Available: {'✅' if fastmcp_ok else '❌'}")
    print(f"Vector Store Available: {'✅' if vector_ok else '❌'}")  
    print(f"Enhanced Server Init: {'✅' if server_ok else '❌'}")
    
    if server_ok:
        print("\n🎉 Enhanced server should work properly in production!")
    else:
        print("\n🚨 Enhanced server initialization issues detected!")
    
    return server_ok

if __name__ == "__main__":
    main()