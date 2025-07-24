#!/usr/bin/env python3
"""
OAuth Test Fix - Properly test OAuth endpoints with required parameters
"""

import requests
import json

def test_oauth_endpoints():
    """Test OAuth endpoints with proper parameters"""
    base_url = "https://strunz.up.railway.app"
    
    print("Testing OAuth Endpoints with Proper Parameters")
    print("=" * 50)
    
    # Test 1: OAuth Authorize with required parameters
    print("\n1. Testing /oauth/authorize with required params...")
    authorize_url = f"{base_url}/oauth/authorize"
    params = {
        "client_id": "test-client",
        "redirect_uri": "https://example.com/callback",
        "scope": "read",
        "response_type": "code",
        "state": "test-state"
    }
    
    try:
        response = requests.get(authorize_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ PASS - OAuth authorize endpoint working correctly")
        else:
            print(f"   ❌ FAIL - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")
    
    # Test 2: OAuth Token endpoint (POST)
    print("\n2. Testing /oauth/token endpoint...")
    token_url = f"{base_url}/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": "test-code",
        "redirect_uri": "https://example.com/callback",
        "client_id": "test-client"
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        print(f"   Status: {response.status_code}")
        # 400 is expected for invalid code
        if response.status_code in [400, 401]:
            print("   ✅ PASS - OAuth token endpoint responding correctly")
        else:
            print(f"   ❌ FAIL - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")
    
    # Test 3: OAuth Discovery
    print("\n3. Testing OAuth discovery endpoint...")
    discovery_url = f"{base_url}/.well-known/oauth-authorization-server"
    
    try:
        response = requests.get(discovery_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ PASS - Discovery endpoint working")
            print(f"   - Issuer: {data.get('issuer')}")
            print(f"   - Authorization endpoint: {data.get('authorization_endpoint')}")
            print(f"   - Token endpoint: {data.get('token_endpoint')}")
        else:
            print(f"   ❌ FAIL - Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL - Error: {e}")

if __name__ == "__main__":
    test_oauth_endpoints()