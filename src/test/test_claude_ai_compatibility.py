#!/usr/bin/env python3
"""
Test Claude.ai compatibility for Batch 1 migration
Checks SSE endpoint and tool exposure
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Enable Batch 1 migration
os.environ['ENABLE_BATCH1_MIGRATION'] = 'true'


def test_claude_ai_requirements():
    """Test requirements for Claude.ai connection"""
    print("=== Claude.ai Compatibility Test ===\n")
    
    results = {"compatible": [], "incompatible": [], "warnings": []}
    
    # Test 1: Check SSE server implementation
    print("1. Checking SSE server implementation...")
    try:
        from src.mcp.sse_server_v8 import mcp_server, app
        
        # Check if server is using FastMCP (current) or Official SDK (needed)
        if hasattr(mcp_server, '__class__'):
            server_type = mcp_server.__class__.__name__
            if 'FastMCP' in server_type:
                print(f"⚠️ SSE server still using FastMCP: {server_type}")
                results["warnings"].append("SSE server needs migration to Official MCP SDK")
            else:
                print(f"✅ SSE server using: {server_type}")
                results["compatible"].append("SSE server implementation")
        
        # Check for Claude.ai specific endpoints
        print("\n2. Checking Claude.ai specific endpoints...")
        
        # Check for OAuth endpoints
        routes = []
        if hasattr(app, 'routes'):
            for route in app.routes:
                routes.append(f"{route.methods} {route.path}")
        
        required_endpoints = [
            "/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
            "/api/mcp/auth_callback",
            "/.well-known/mcp/resource"
        ]
        
        for endpoint in required_endpoints:
            found = any(endpoint in str(route) for route in routes)
            if found:
                print(f"✅ Found: {endpoint}")
                results["compatible"].append(f"Endpoint: {endpoint}")
            else:
                print(f"❌ Missing: {endpoint}")
                results["incompatible"].append(f"Missing endpoint: {endpoint}")
        
    except Exception as e:
        print(f"❌ SSE server check failed: {e}")
        results["incompatible"].append(f"SSE server error: {str(e)}")
    
    # Test 2: Check if Batch 1 tools would be exposed
    print("\n3. Checking Batch 1 tool exposure in SSE...")
    
    # The current SSE server uses FastMCP, so Batch 1 tools won't be exposed
    # until we migrate the SSE server to use Official MCP SDK
    print("⚠️ Batch 1 tools are implemented in mcp_sdk_clean.py")
    print("⚠️ SSE server (sse_server_v8.py) still uses FastMCP")
    print("⚠️ Tools won't be visible to Claude.ai until SSE migration")
    results["warnings"].append("SSE server needs to use mcp_sdk_clean.py tools")
    
    # Test 3: Check main.py transport handling
    print("\n4. Checking transport configuration...")
    try:
        with open(os.path.join(project_root, "main.py"), 'r') as f:
            main_content = f.read()
        
        if 'sse_server_v8' in main_content:
            print("✅ main.py configured to use SSE server for web")
            results["compatible"].append("Transport configuration")
        
        if 'mcp_sdk_clean' in main_content:
            print("⚠️ main.py may need update to use mcp_sdk_clean for SSE")
            results["warnings"].append("main.py SSE integration needs update")
    except Exception as e:
        print(f"❌ main.py check failed: {e}")
        results["incompatible"].append(f"main.py error: {str(e)}")
    
    # Test 4: Check for OAuth configuration
    print("\n5. Checking OAuth configuration...")
    oauth_vars = [
        "CLAUDE_AI_SKIP_OAUTH",
        "OAUTH_CLIENT_ID",
        "OAUTH_CLIENT_SECRET"
    ]
    
    for var in oauth_vars:
        if os.environ.get(var):
            print(f"✅ {var} is configured")
            results["compatible"].append(f"OAuth: {var}")
        else:
            print(f"ℹ️ {var} not set (may be optional)")
    
    # Summary
    print("\n=== Claude.ai Compatibility Summary ===\n")
    
    print(f"Compatible features: {len(results['compatible'])}")
    for item in results['compatible']:
        print(f"  ✅ {item}")
    
    print(f"\nIncompatible features: {len(results['incompatible'])}")
    for item in results['incompatible']:
        print(f"  ❌ {item}")
    
    print(f"\nWarnings: {len(results['warnings'])}")
    for item in results['warnings']:
        print(f"  ⚠️ {item}")
    
    # Overall assessment
    print("\n=== Overall Assessment ===")
    
    if len(results['incompatible']) == 0 and len(results['warnings']) == 0:
        print("✅ FULLY COMPATIBLE - Claude.ai should maintain connection")
        return True
    elif len(results['incompatible']) == 0:
        print("⚠️ PARTIALLY COMPATIBLE - Claude.ai may connect but with limitations")
        print("\nIMPORTANT: Batch 1 tools won't be visible to Claude.ai until:")
        print("1. SSE server (sse_server_v8.py) is migrated to use Official MCP SDK")
        print("2. SSE server imports and uses tools from mcp_sdk_clean.py")
        print("3. Both servers (stdio and SSE) share the same tool implementations")
        return True
    else:
        print("❌ NOT COMPATIBLE - Claude.ai connection will likely fail")
        return False


def generate_migration_plan():
    """Generate a plan for full Claude.ai compatibility"""
    print("\n\n=== Migration Plan for Claude.ai Compatibility ===\n")
    
    print("To ensure Claude.ai maintains 'Connected' status with Batch 1 tools:\n")
    
    print("1. **Current State**:")
    print("   - Batch 1 tools implemented in mcp_sdk_clean.py ✅")
    print("   - Tools work with stdio transport (Claude Desktop) ✅")
    print("   - SSE server still uses FastMCP ⚠️")
    print("   - Tools not exposed to Claude.ai ❌")
    
    print("\n2. **Required Changes**:")
    print("   a) Migrate sse_server_v8.py to use Official MCP SDK")
    print("   b) Import StrunzKnowledgeServer from mcp_sdk_clean.py")
    print("   c) Expose the same tools in SSE transport")
    print("   d) Maintain OAuth and Claude.ai specific endpoints")
    
    print("\n3. **Deployment Strategy**:")
    print("   a) Test SSE migration locally")
    print("   b) Deploy to staging with both transports")
    print("   c) Verify Claude.ai sees all tools")
    print("   d) Monitor for 24 hours")
    print("   e) Deploy to production")
    
    print("\n4. **Risk Mitigation**:")
    print("   - Keep FastMCP version as backup")
    print("   - Use feature flags for SSE migration too")
    print("   - Test thoroughly before production")


if __name__ == "__main__":
    print("Claude.ai Compatibility Test for Batch 1 Migration")
    print("=" * 50)
    print()
    
    # Run compatibility test
    compatible = test_claude_ai_requirements()
    
    # Generate migration plan
    generate_migration_plan()
    
    print("\n" + "=" * 50)
    print("Test completed:", datetime.now().isoformat())