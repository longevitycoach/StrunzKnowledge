#!/usr/bin/env python3
"""
Test the actual OAuth flow that Claude.ai is performing
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

def test_claude_oauth_flow():
    """Simulate the OAuth flow Claude.ai is performing"""
    base_url = "https://strunz.up.railway.app"
    
    print("Testing Claude.ai OAuth Flow")
    print("=" * 50)
    
    # Step 1: Check OAuth discovery
    print("\n1. Checking OAuth discovery endpoints...")
    
    # Check authorization server metadata
    try:
        response = requests.get(f"{base_url}/.well-known/oauth-authorization-server")
        print(f"   Authorization Server Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Authorization endpoint: {data.get('authorization_endpoint')}")
            print(f"   - Token endpoint: {data.get('token_endpoint')}")
            print(f"   - Registration endpoint: {data.get('registration_endpoint')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 2: Check MCP resource discovery
    print("\n2. Checking MCP resource discovery...")
    try:
        response = requests.get(f"{base_url}/.well-known/mcp/resource")
        print(f"   MCP Resource Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            if 'authentication' in data:
                print("   ⚠️  WARNING: Authentication is still present in response!")
            else:
                print("   ✅ Good: No authentication field")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 3: Test the authorization flow Claude is using
    print("\n3. Testing authorization flow...")
    auth_params = {
        "response_type": "code",
        "client_id": "client_1ddfa125400747d9",
        "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
        "code_challenge": "FDGCOpXvAka6a8lEdH_oLyDmjFYkhbjJQx6d6z8b7vg",
        "code_challenge_method": "S256",
        "state": "test-state",
        "scope": "read write",
        "resource": base_url
    }
    
    try:
        response = requests.get(
            f"{base_url}/oauth/authorize",
            params=auth_params,
            allow_redirects=False
        )
        print(f"   Authorization Status: {response.status_code}")
        if response.status_code in [302, 307]:
            location = response.headers.get('Location', '')
            print(f"   Redirect to: {location}")
            
            # Check if it's redirecting to Claude's callback
            if "claude.ai" in location and "code=" in location:
                print("   ✅ OAuth flow appears to be working")
            else:
                print("   ⚠️  Unexpected redirect")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Check what our custom endpoint returns
    print("\n4. Testing Claude.ai specific endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/organizations/test-org/mcp/start-auth/test-auth"
        )
        print(f"   Start Auth Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            if data.get("auth_not_required"):
                print("   ⚠️  This non-standard response might confuse Claude.ai")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_claude_oauth_flow()