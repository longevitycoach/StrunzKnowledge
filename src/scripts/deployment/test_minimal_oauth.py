#!/usr/bin/env python3
"""
Test minimal OAuth implementation for Claude.ai
This implements just enough OAuth to satisfy Claude.ai without actual authentication
"""

import requests

def test_minimal_oauth():
    """Test minimal OAuth flow"""
    base_url = "https://strunz.up.railway.app"
    
    print("Testing Minimal OAuth Flow")
    print("=" * 50)
    
    # Test parameters from Claude.ai
    params = {
        "response_type": "code",
        "client_id": "client_1ddfa125400747d9",
        "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
        "code_challenge": "4c1qNYwEQgkON6kjf6uS9kO82lo8KodsWS8YeiXNZqM",
        "code_challenge_method": "S256",
        "state": "M3WbzdnOnH_23LvqWcF2jDelfSeHGdn4KHxg_qc1zq4",
        "scope": "claudeai"
    }
    
    # Step 1: Test authorize endpoint
    print("\n1. Testing /authorize endpoint...")
    response = requests.get(f"{base_url}/authorize", params=params, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text if response.status_code != 302 else 'Redirect'}")
    if response.status_code == 302:
        print(f"   Location: {response.headers.get('Location', 'No location')}")
    
    # Step 2: Test OAuth authorize endpoint
    print("\n2. Testing /oauth/authorize endpoint...")
    response = requests.get(f"{base_url}/oauth/authorize", params=params, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text if response.status_code != 302 else 'Redirect'}")
    
    # Step 3: Test what Claude.ai expects
    print("\n3. What would a working OAuth flow return?")
    print("   Expected: 302 redirect to callback with authorization code")
    print("   Example: https://claude.ai/api/mcp/auth_callback?code=AUTH_CODE&state=STATE")

if __name__ == "__main__":
    test_minimal_oauth()