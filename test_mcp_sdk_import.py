#!/usr/bin/env python3
"""
Test script to verify all MCP SDK dependencies
"""

import sys
import os

print("Testing MCP SDK Server Dependencies")
print("=" * 40)

# Add project to path
sys.path.insert(0, '.')

def test_import(module_name, description=""):
    try:
        __import__(module_name)
        print(f"✅ {module_name} {description}")
        return True
    except Exception as e:
        print(f"❌ {module_name} {description}: {e}")
        return False

# Test core dependencies
success = 0
total = 0

modules = [
    ("mcp", "- MCP SDK core"),
    ("mcp.types", "- MCP types"),
    ("mcp.server", "- MCP server"),
    ("mcp.server.stdio", "- Stdio transport"),
    ("mcp.server.sse", "- SSE transport"),
    ("fastapi", "- FastAPI framework"),
    ("uvicorn", "- ASGI server"),
    ("pydantic", "- Data validation"),
]

for module, desc in modules:
    total += 1
    if test_import(module, desc):
        success += 1

print(f"\nResult: {success}/{total} imports successful")

if success == total:
    print("\n🎉 All dependencies available - testing server import...")
    
    try:
        from src.mcp.mcp_sdk_server import server, main
        print("✅ MCP SDK server imports successfully")
        print(f"✅ Server name: {server.name}")
        
        # Test in Railway mode
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        print("✅ Ready for Railway deployment")
        
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ Missing {total - success} dependencies")
    print("Install with: pip install fastapi uvicorn mcp")