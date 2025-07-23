#!/usr/bin/env python3
"""
Cleanup Validation Test - Issue #19 Day 2
Validates that all remaining MCP servers and utilities import correctly after cleanup.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_import(module_path, description):
    """Test if a module can be imported successfully."""
    try:
        exec(f"import {module_path}")
        print(f"✅ {description}: {module_path}")
        return True
    except Exception as e:
        print(f"❌ {description}: {module_path} - ERROR: {e}")
        return False

def main():
    """Run all import validation tests."""
    print("🧪 Cleanup Validation Test Suite - Issue #19")
    print("=" * 50)
    
    tests = [
        # Primary MCP Servers
        ("src.mcp.mcp_sdk_clean", "Primary MCP SDK Server"),
        ("src.mcp.enhanced_server", "Enhanced Server (FastMCP)"),
        ("src.mcp.claude_compatible_server", "Claude Compatible Server"),
        ("src.mcp.unified_mcp_server", "Unified MCP Server (Production)"),
        
        # Utility Modules
        ("src.mcp.claude_ai_oauth_handler", "Claude.ai OAuth Handler"),
        ("src.mcp.oauth_provider", "OAuth Provider"),
        ("src.mcp.user_profiling", "User Profiling System"),
        ("src.mcp.lightweight_embeddings", "Lightweight Embeddings"),
        ("src.mcp.mcp_input_parser", "MCP Input Parser"),
        
        # Core RAG Components
        ("src.rag.search", "RAG Search Engine"),
        ("src.rag.vector_store", "Vector Store"),
        
        # Main Entry Points
        ("main", "Main Entry Point"),
    ]
    
    passed = 0
    failed = 0
    
    for module_path, description in tests:
        if test_import(module_path, description):
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All imports successful! Cleanup validation PASSED")
        return 0
    else:
        print("⚠️ Some imports failed! Manual review needed")
        return 1

if __name__ == "__main__":
    exit(main())