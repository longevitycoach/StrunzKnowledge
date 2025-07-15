#!/usr/bin/env python3
"""
Simple test for MCP server without external dependencies
"""

import urllib.request
import json
import sys

def test_endpoint(url, description):
    """Test a single endpoint"""
    print(f"🔍 Testing {description}...")
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                try:
                    json_data = json.loads(data)
                    print(f"✅ {description}: PASSED")
                    return True, json_data
                except json.JSONDecodeError:
                    print(f"✅ {description}: PASSED (non-JSON response)")
                    return True, data
            else:
                print(f"❌ {description}: FAILED - HTTP {response.status}")
                return False, None
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False, str(e)

def test_post_endpoint(url, data, description):
    """Test a POST endpoint"""
    print(f"🔍 Testing {description}...")
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=json_data, 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                resp_data = response.read().decode('utf-8')
                try:
                    json_resp = json.loads(resp_data)
                    print(f"✅ {description}: PASSED")
                    return True, json_resp
                except json.JSONDecodeError:
                    print(f"✅ {description}: PASSED (non-JSON response)")
                    return True, resp_data
            else:
                print(f"❌ {description}: FAILED - HTTP {response.status}")
                return False, None
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False, str(e)

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🧪 Testing MCP Server at: {base_url}")
    print("=" * 50)
    
    tests = []
    
    # Test health check
    success, result = test_endpoint(f"{base_url}/", "Health Check")
    tests.append(("health_check", success))
    if success and isinstance(result, dict):
        print(f"   Server: {result.get('server', 'Unknown')}")
        print(f"   Version: {result.get('version', 'Unknown')}")
        print(f"   Protocol: {result.get('protocol_version', 'Unknown')}")
    
    # Test OAuth discovery endpoints
    success, result = test_endpoint(f"{base_url}/.well-known/oauth-authorization-server", "OAuth Server Discovery")
    tests.append(("oauth_server_discovery", success))
    
    success, result = test_endpoint(f"{base_url}/.well-known/oauth-protected-resource", "OAuth Resource Discovery")
    tests.append(("oauth_resource_discovery", success))
    
    # Test MCP discovery
    success, result = test_endpoint(f"{base_url}/.well-known/mcp/resource", "MCP Resource Discovery")
    tests.append(("mcp_discovery", success))
    
    # Test OAuth client registration
    registration_data = {
        "client_name": "Test Client",
        "redirect_uris": ["http://localhost:3000/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"]
    }
    success, result = test_post_endpoint(f"{base_url}/oauth/register", registration_data, "OAuth Client Registration")
    tests.append(("oauth_registration", success))
    
    # Test MCP initialize
    init_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "Test Client", "version": "1.0.0"}
        }
    }
    success, result = test_post_endpoint(f"{base_url}/messages", init_data, "MCP Initialize")
    tests.append(("mcp_initialize", success))
    
    # Test tools list
    tools_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    success, result = test_post_endpoint(f"{base_url}/messages", tools_data, "MCP Tools List")
    tests.append(("tools_list", success))
    if success and isinstance(result, dict) and "result" in result:
        tools_count = len(result["result"].get("tools", []))
        print(f"   Tools found: {tools_count}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())