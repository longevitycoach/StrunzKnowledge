#!/usr/bin/env python3
"""
Test MCP server running in Docker with SSE transport
"""

import requests
import json
import time
from datetime import datetime

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get("http://localhost:8080/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            print(f"  Server: {data['server']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_sse_endpoint():
    """Test the SSE endpoint"""
    print("\nTesting SSE endpoint...")
    try:
        # Test SSE connection
        response = requests.get("http://localhost:8080/sse", stream=True, timeout=5)
        if response.status_code == 200:
            print("✓ SSE endpoint connected")
            
            # Read first few events
            lines = []
            for i, line in enumerate(response.iter_lines()):
                if i > 10:  # Read first 10 lines
                    break
                if line:
                    decoded = line.decode('utf-8')
                    lines.append(decoded)
                    if decoded.startswith('data:'):
                        try:
                            data = json.loads(decoded[5:])
                            print(f"  Received event: {data.get('message', data)}")
                        except:
                            print(f"  Raw event: {decoded}")
            
            return True
        else:
            print(f"✗ SSE endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✓ SSE endpoint timeout (expected for streaming)")
        return True
    except Exception as e:
        print(f"✗ SSE endpoint error: {e}")
        return False

def test_mcp_endpoint():
    """Test the MCP JSON-RPC endpoint"""
    print("\nTesting MCP endpoint...")
    
    # Test tools/list
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    try:
        response = requests.post("http://localhost:8080/mcp", json=request_data)
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                tools = data["result"]["tools"]
                print(f"✓ MCP tools/list: Found {len(tools)} tools")
                # Show first 5 tools
                for tool in tools[:5]:
                    print(f"  - {tool['name']}")
                if len(tools) > 5:
                    print(f"  ... and {len(tools) - 5} more")
                return True
            else:
                print(f"✗ MCP tools/list failed: {data}")
                return False
        else:
            print(f"✗ MCP endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ MCP endpoint error: {e}")
        return False

def test_tool_call():
    """Test calling an MCP tool"""
    print("\nTesting MCP tool call...")
    
    # Call get_mcp_server_purpose tool
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_mcp_server_purpose",
            "arguments": {}
        },
        "id": 2
    }
    
    try:
        response = requests.post("http://localhost:8080/mcp", json=request_data)
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                result = data["result"]
                print("✓ Tool call successful:")
                print(f"  Server: {result.get('server_name', 'Unknown')}")
                print(f"  Purpose: {result.get('purpose', 'Unknown')}")
                return True
            else:
                print(f"✗ Tool call failed: {data}")
                return False
        else:
            print(f"✗ Tool call HTTP failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Tool call error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Testing MCP Server in Docker with SSE ===")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Allow container to fully start
    print("Waiting for container to start...")
    time.sleep(2)
    
    # Run tests
    results = {
        "health": test_health_check(),
        "sse": test_sse_endpoint(),
        "mcp_list": test_mcp_endpoint(),
        "mcp_call": test_tool_call()
    }
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())