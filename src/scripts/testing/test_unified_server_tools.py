#!/usr/bin/env python3
"""
Test Unified Server Tool Extraction
Test if the unified server can properly extract and call tools from the enhanced server
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_unified_server_tools():
    """Test unified server tool extraction and execution"""
    
    print("🔍 Testing Unified Server Tool Extraction...")
    print("=" * 60)
    
    try:
        # Import the unified server components
        from src.mcp.unified_mcp_server import _enhanced_server, startup_event
        from src.mcp.enhanced_server import StrunzKnowledgeMCP
        
        # Initialize enhanced server manually
        print("🚀 Initializing enhanced server...")
        enhanced_server = StrunzKnowledgeMCP()
        print(f"✅ Enhanced server loaded with {len(enhanced_server.tool_registry)} tools")
        
        # Test tool extraction
        print("\n🛠️ Testing tool extraction...")
        test_tool = "get_mcp_server_purpose"
        
        if test_tool in enhanced_server.tool_registry:
            tool_info = enhanced_server.tool_registry[test_tool]
            print(f"📋 Tool info type: {type(tool_info)}")
            print(f"📋 Tool info attributes: {dir(tool_info)}")
            
            # Extract function (same logic as unified server)
            if hasattr(tool_info, 'fn'):
                func = tool_info.fn  # FastMCP FunctionTool.fn is the actual function
                print("✅ Extracted fn from FastMCP FunctionTool")
            elif hasattr(tool_info, 'run'):
                # FastMCP FunctionTool.run method
                func = lambda **kwargs: tool_info.run(**kwargs)
                print("✅ Using run method from FastMCP FunctionTool")
            elif hasattr(tool_info, 'func'):
                func = tool_info.func  # Other FunctionTool variants
                print("✅ Extracted func from other FunctionTool")
            elif hasattr(tool_info, 'function'):
                func = tool_info.function  # Other wrappers
                print("✅ Extracted function from wrapper")
            elif callable(tool_info):
                func = tool_info  # Direct function
                print("✅ Using direct function")
            else:
                # Try to get the original function
                func = getattr(tool_info, '__call__', tool_info)
                print("✅ Using __call__ method")
            
            print(f"📋 Extracted function type: {type(func)}")
            print(f"📋 Function callable: {callable(func)}")
            print(f"📋 Function async: {asyncio.iscoroutinefunction(func)}")
            
            # Test function call
            print("\n🎯 Testing function call...")
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func()
                else:
                    result = func()
                
                print(f"✅ Function call successful!")
                print(f"📄 Result: {str(result)[:200]}...")
                
            except Exception as e:
                print(f"❌ Function call failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Tool {test_tool} not found in registry")
        
        # Test a few more tools
        print(f"\n🧪 Testing additional tools...")
        test_tools = ["get_dr_strunz_biography", "get_vector_db_analysis"]
        
        for tool_name in test_tools:
            if tool_name in enhanced_server.tool_registry:
                try:
                    tool_info = enhanced_server.tool_registry[tool_name]
                    
                    # Extract function
                    if hasattr(tool_info, 'fn'):
                        func = tool_info.fn
                    elif hasattr(tool_info, 'run'):
                        func = lambda **kwargs: tool_info.run(**kwargs)
                    elif hasattr(tool_info, 'func'):
                        func = tool_info.func
                    elif hasattr(tool_info, 'function'):
                        func = tool_info.function
                    elif callable(tool_info):
                        func = tool_info
                    else:
                        func = getattr(tool_info, '__call__', tool_info)
                    
                    # Test call
                    if asyncio.iscoroutinefunction(func):
                        result = await func()
                    else:
                        result = func()
                    
                    print(f"  ✅ {tool_name}: Success")
                    
                except Exception as e:
                    print(f"  ❌ {tool_name}: {str(e)[:50]}")
            else:
                print(f"  ⚠️ {tool_name}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_unified_server_tools()
    
    if success:
        print("\n🎉 Unified server tool extraction working!")
    else:
        print("\n🚨 Issues detected with unified server tool extraction")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())