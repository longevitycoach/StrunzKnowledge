#!/usr/bin/env python3
"""
Test OAuth flow for Claude MCP integration
"""

import requests
import json
import secrets
import time
from urllib.parse import urlencode, urlparse, parse_qs

# Test configuration
BASE_URL = "https://strunz.up.railway.app"
# BASE_URL = "http://localhost:8000"  # For local testing

def test_oauth_discovery():
    """Test OAuth metadata discovery"""
    print("=== Testing OAuth Discovery ===")
    
    # Get OAuth metadata
    response = requests.get(f"{BASE_URL}/.well-known/oauth-authorization-server")
    if response.status_code == 200:
        metadata = response.json()
        print("✓ OAuth metadata discovered:")
        print(f"  Issuer: {metadata['issuer']}")
        print(f"  Authorization endpoint: {metadata['authorization_endpoint']}")
        print(f"  Token endpoint: {metadata['token_endpoint']}")
        print(f"  Registration endpoint: {metadata['registration_endpoint']}")
        print(f"  Supported scopes: {', '.join(metadata['scopes_supported'])}")
        return metadata
    else:
        print(f"✗ Failed to discover OAuth metadata: {response.status_code}")
        return None

def test_dynamic_client_registration():
    """Test Dynamic Client Registration"""
    print("\n=== Testing Dynamic Client Registration ===")
    
    # Register a new client
    registration_data = {
        "client_name": "Claude AI Test Client",
        "redirect_uris": ["https://claude.ai/oauth/callback"],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": "read write",
        "token_endpoint_auth_method": "client_secret_basic"
    }
    
    response = requests.post(
        f"{BASE_URL}/oauth/register",
        json=registration_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        client = response.json()
        print("✓ Client registered successfully:")
        print(f"  Client ID: {client['client_id']}")
        print(f"  Client Name: {client['client_name']}")
        print(f"  Client Secret: {client['client_secret'][:8]}...")
        return client
    else:
        print(f"✗ Failed to register client: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_authorization_flow(client):
    """Test authorization code flow"""
    print("\n=== Testing Authorization Flow ===")
    
    # Generate PKCE challenge
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = code_verifier  # For plain method, use S256 in production
    
    # Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": client["client_id"],
        "redirect_uri": client["redirect_uris"][0],
        "scope": "read write",
        "state": secrets.token_urlsafe(16),
        "code_challenge": code_challenge,
        "code_challenge_method": "plain"
    }
    
    auth_url = f"{BASE_URL}/oauth/authorize?{urlencode(auth_params)}"
    print(f"Authorization URL: {auth_url}")
    
    # Simulate authorization (in real flow, user would visit this URL)
    response = requests.get(auth_url, allow_redirects=False)
    
    if response.status_code == 302:
        # Parse redirect URL
        redirect_url = response.headers.get("Location")
        parsed = urlparse(redirect_url)
        query_params = parse_qs(parsed.query)
        
        auth_code = query_params.get("code", [None])[0]
        state = query_params.get("state", [None])[0]
        
        if auth_code:
            print(f"✓ Authorization code received: {auth_code[:10]}...")
            print(f"  State matches: {state == auth_params['state']}")
            return auth_code, code_verifier
        else:
            print("✗ No authorization code in redirect")
            return None, None
    else:
        print(f"✗ Authorization failed: {response.status_code}")
        return None, None

def test_token_exchange(client, auth_code, code_verifier):
    """Test token exchange"""
    print("\n=== Testing Token Exchange ===")
    
    # Exchange authorization code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": client["redirect_uris"][0],
        "code_verifier": code_verifier
    }
    
    # Use client credentials
    import base64
    auth_header = base64.b64encode(
        f"{client['client_id']}:{client['client_secret']}".encode()
    ).decode()
    
    response = requests.post(
        f"{BASE_URL}/oauth/token",
        data=token_data,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("✓ Tokens received:")
        print(f"  Access token: {tokens['access_token'][:20]}...")
        print(f"  Token type: {tokens['token_type']}")
        print(f"  Expires in: {tokens['expires_in']} seconds")
        print(f"  Refresh token: {tokens['refresh_token'][:20]}...")
        return tokens
    else:
        print(f"✗ Token exchange failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_authenticated_request(access_token):
    """Test authenticated API request"""
    print("\n=== Testing Authenticated Request ===")
    
    # Test SSE endpoint
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test health endpoint (should work without auth)
    response = requests.get(f"{BASE_URL}/", headers=headers)
    if response.status_code == 200:
        print("✓ Health check passed")
    
    # Test SSE endpoint (requires auth)
    response = requests.get(
        f"{BASE_URL}/sse",
        headers=headers,
        stream=True,
        timeout=5
    )
    
    if response.status_code == 200:
        print("✓ SSE endpoint accessible with token")
        # Read first event
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data:'):
                    data = json.loads(decoded[5:])
                    print(f"  Connected as user: {data.get('user')}")
                    print(f"  Scope: {data.get('scope')}")
                    break
        return True
    else:
        print(f"✗ SSE request failed: {response.status_code}")
        return False

def test_refresh_token(client, refresh_token):
    """Test refresh token grant"""
    print("\n=== Testing Refresh Token ===")
    
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    import base64
    auth_header = base64.b64encode(
        f"{client['client_id']}:{client['client_secret']}".encode()
    ).decode()
    
    response = requests.post(
        f"{BASE_URL}/oauth/token",
        data=token_data,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("✓ New access token received")
        return tokens
    else:
        print(f"✗ Refresh failed: {response.status_code}")
        return None

def main():
    """Run OAuth flow tests"""
    print("=== OAuth 2.1 Flow Test for Claude MCP ===")
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Test discovery
    metadata = test_oauth_discovery()
    if not metadata:
        return 1
    
    # Test client registration
    client = test_dynamic_client_registration()
    if not client:
        return 1
    
    # Test authorization flow
    auth_code, code_verifier = test_authorization_flow(client)
    if not auth_code:
        return 1
    
    # Test token exchange
    tokens = test_token_exchange(client, auth_code, code_verifier)
    if not tokens:
        return 1
    
    # Test authenticated request
    if not test_authenticated_request(tokens["access_token"]):
        return 1
    
    # Test refresh token
    new_tokens = test_refresh_token(client, tokens["refresh_token"])
    if not new_tokens:
        return 1
    
    print("\n✅ All OAuth tests passed!")
    print("The OAuth implementation is ready for Claude.ai integration.")
    
    # Print integration instructions
    print("\n=== Claude.ai Integration ===")
    print("1. Claude.ai will discover OAuth endpoints via /.well-known/oauth-authorization-server")
    print("2. Claude will register a client dynamically")
    print("3. Users will be redirected to authorize access")
    print("4. Claude will exchange the code for tokens")
    print("5. All MCP requests will include the Bearer token")
    
    return 0

if __name__ == "__main__":
    exit(main())