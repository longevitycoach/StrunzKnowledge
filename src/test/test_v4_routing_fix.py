#!/usr/bin/env python3
"""
Quick test to verify v4 routing fixes
"""

import requests
import json
import time
import uuid
from datetime import datetime

def test_routing_fixes():
    """Test the routing fixes in v4"""
    base_url = "http://localhost:8080"
    session_id = str(uuid.uuid4())
    
    print("🔧 Testing MCP Server v4 Routing Fixes")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        success = response.status_code == 200
        print(f"✅ Health: {response.status_code}" if success else f"❌ Health: {response.status_code}")
        results.append(("Health", success, response.status_code))
        
        if success:
            data = response.json()
            print(f"   Version: {data.get('version', 'unknown')}")
    except Exception as e:
        print(f"❌ Health: Error - {e}")
        results.append(("Health", False, 0))
    
    # Test 2: SSE endpoint (root mount)
    try:
        headers = {'Accept': 'text/event-stream'}
        response = requests.get(f"{base_url}/sse", headers=headers, timeout=5, stream=True)
        success = response.status_code == 200
        print(f"✅ SSE GET /sse: {response.status_code}" if success else f"❌ SSE GET /sse: {response.status_code}")
        results.append(("SSE GET /sse", success, response.status_code))
        response.close()
    except Exception as e:
        print(f"❌ SSE GET /sse: Error - {e}")
        results.append(("SSE GET /sse", False, 0))
    
    # Test 3: Root endpoint (should be SSE)
    try:
        headers = {'Accept': 'text/event-stream'}
        response = requests.get(f"{base_url}/", headers=headers, timeout=5, stream=True)
        success = response.status_code == 200
        print(f"✅ SSE GET /: {response.status_code}" if success else f"❌ SSE GET /: {response.status_code}")
        results.append(("SSE GET /", success, response.status_code))
        response.close()
    except Exception as e:
        print(f"❌ SSE GET /: Error - {e}")
        results.append(("SSE GET /", False, 0))
    
    # Test 4: MCP protocol test - Initialize
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client-v4",
                    "version": "4.0.0"
                }
            }
        }
        
        # Try posting to SSE endpoint with session
        response = requests.post(f"{base_url}/sse?session_id={session_id}", 
                               json=payload, headers=headers, timeout=5)
        success = response.status_code in [200, 202]
        print(f"✅ Initialize: {response.status_code}" if success else f"❌ Initialize: {response.status_code}")
        results.append(("Initialize", success, response.status_code))
    except Exception as e:
        print(f"❌ Initialize: Error - {e}")
        results.append(("Initialize", False, 0))
    
    # Test 5: List tools
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(f"{base_url}/sse?session_id={session_id}", 
                               json=payload, headers=headers, timeout=5)
        success = response.status_code in [200, 202]
        print(f"✅ List Tools: {response.status_code}" if success else f"❌ List Tools: {response.status_code}")
        results.append(("List Tools", success, response.status_code))
        
        if success and response.text:
            try:
                data = response.json()
                print(f"   Tools available: {len(data.get('result', {}).get('tools', []))}")
            except:
                pass
    except Exception as e:
        print(f"❌ List Tools: Error - {e}")
        results.append(("List Tools", False, 0))
    
    # Summary
    print("\n" + "=" * 60)
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🟢 Overall Status: ROUTING FIXED! - v4 is working properly")
    elif success_rate >= 60:
        print("🟡 Overall Status: PARTIAL FIX - Some routing issues remain")
    else:
        print("🔴 Overall Status: ROUTING ISSUES - More work needed")
    
    print("\n📝 Test Report Summary:")
    print("-" * 40)
    for test_name, success, status_code in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status:8} (HTTP {status_code})")
    
    return success_rate >= 80

if __name__ == "__main__":
    test_routing_fixes()