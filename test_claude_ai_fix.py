#!/usr/bin/env python3
"""
Test script to verify Claude.ai MCP server fixes
"""

import requests
import json

def test_claude_ai_endpoints():
    """Test all Claude.ai specific endpoints"""
    base_url = "http://localhost:8080"
    
    print("Testing Claude.ai MCP Server Fixes")
    print("=" * 50)
    
    # Test 1: MCP Resource Discovery (should NOT show authentication)
    print("\n1. Testing /.well-known/mcp/resource...")
    try:
        response = requests.get(f"{base_url}/.well-known/mcp/resource")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Has authentication: {'authentication' in data}")
        if 'authentication' not in data:
            print("   ✅ PASS - No authentication required")
        else:
            print("   ❌ FAIL - Authentication still present")
        print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")
    
    # Test 2: Claude.ai Start Auth Endpoint
    print("\n2. Testing Claude.ai start-auth endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/organizations/test-org/mcp/start-auth/test-auth"
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        if data.get("auth_not_required") == True:
            print("   ✅ PASS - Authentication not required")
        else:
            print("   ❌ FAIL - Unexpected response")
        print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")
    
    # Test 3: Basic health check
    print("\n3. Testing basic health endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Server: {data.get('server')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Total tools: {data.get('tools_summary', {}).get('total')}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")
    
    # Test 4: SSE endpoint (just check it exists)
    print("\n4. Testing SSE endpoint exists...")
    try:
        response = requests.head(f"{base_url}/sse")
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 204]:
            print("   ✅ PASS - SSE endpoint available")
        else:
            print("   ❌ FAIL - SSE endpoint not available")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")

if __name__ == "__main__":
    print("Make sure the server is running locally on port 8080")
    print("Run with: CLAUDE_AI_SKIP_OAUTH=true python src/mcp/claude_compatible_server.py")
    input("\nPress Enter when server is ready...")
    
    test_claude_ai_endpoints()