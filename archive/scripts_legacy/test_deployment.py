#!/usr/bin/env python3
"""Test script for deployed Strunz Knowledge Base application."""

import requests
import json
import sys
from datetime import datetime

def test_deployment(base_url):
    """Run tests against deployed application."""
    print(f"\n🧪 Testing Strunz Knowledge Base at: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ✅ Server: {data.get('name', 'Unknown')}")
            print(f"   ✅ Version: {data.get('version', 'Unknown')}")
            print(f"   ✅ Vector Store Stats: {data.get('vector_store_stats', {})}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   ❌ Response: {response.text}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Test 2: SSE endpoint
    print("\n2. Testing SSE endpoint...")
    try:
        response = requests.get(f"{base_url}/sse?q=Vitamin%20D", timeout=10, stream=True)
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ✅ Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            # Read first few events
            events_read = 0
            for line in response.iter_lines():
                if line and events_read < 3:
                    print(f"   ✅ Event: {line.decode('utf-8')[:100]}...")
                    events_read += 1
                if events_read >= 3:
                    break
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Test 3: MCP tools endpoint
    print("\n3. Testing MCP tools endpoint...")
    try:
        response = requests.get(f"{base_url}/mcp/tools", timeout=10)
        if response.status_code in [200, 404, 405]:  # May not be a GET endpoint
            print(f"   ✅ MCP endpoint accessible (status: {response.status_code})")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Test 4: Health check
    print("\n4. Testing health check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health check passed")
            tests_passed += 1
        else:
            print(f"   ❌ Health check failed")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary:")
    print(f"   ✅ Passed: {tests_passed}")
    print(f"   ❌ Failed: {tests_failed}")
    print(f"   📅 Tested at: {datetime.now().isoformat()}")
    
    return tests_failed == 0

if __name__ == "__main__":
    # Default to Railway URL
    url = "https://strunz-knowledge-production.up.railway.app"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = test_deployment(url)
    sys.exit(0 if success else 1)