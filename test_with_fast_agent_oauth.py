#!/usr/bin/env python3
"""
Test OAuth endpoints using Fast Agent style testing
"""

import subprocess
import json
import time
import urllib.request
import urllib.parse


def run_test(description, command):
    """Run a test command and return results"""
    print(f"\n🔍 Testing: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return True, result.stdout
        else:
            print(f"❌ Failed: {description}")
            print(f"   Error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout: {description}")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Error: {description} - {e}")
        return False, str(e)


def test_oauth_with_curl(base_url):
    """Test OAuth endpoints using curl commands"""
    print(f"\n🧪 Testing OAuth Endpoints with Fast Agent Style")
    print(f"🌐 Base URL: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health Check
    success, _ = run_test(
        "Health Check",
        f"curl -s {base_url}/ | jq ."
    )
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 2: OAuth Discovery
    success, output = run_test(
        "OAuth Authorization Server Discovery",
        f"curl -s {base_url}/.well-known/oauth-authorization-server | jq ."
    )
    if success:
        tests_passed += 1
        # Extract endpoints from discovery
        try:
            discovery = json.loads(output)
            print(f"   📍 Authorization: {discovery.get('authorization_endpoint', 'N/A')}")
            print(f"   📍 Token: {discovery.get('token_endpoint', 'N/A')}")
        except:
            pass
    else:
        tests_failed += 1
    
    # Test 3: OAuth Protected Resource
    success, _ = run_test(
        "OAuth Protected Resource Discovery",
        f"curl -s {base_url}/.well-known/oauth-protected-resource | jq ."
    )
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 4: MCP Resource Discovery
    success, _ = run_test(
        "MCP Resource Discovery",
        f"curl -s {base_url}/.well-known/mcp/resource | jq ."
    )
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Client Registration
    registration_data = {
        "client_name": "Fast Agent Test Client",
        "redirect_uris": ["http://localhost:3000/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"]
    }
    
    success, output = run_test(
        "OAuth Client Registration",
        f'''curl -s -X POST {base_url}/oauth/register \
        -H "Content-Type: application/json" \
        -d '{json.dumps(registration_data)}' | jq .'''
    )
    
    client_id = None
    if success:
        tests_passed += 1
        try:
            client_data = json.loads(output)
            client_id = client_data.get("client_id")
            print(f"   📝 Client ID: {client_id}")
        except:
            pass
    else:
        tests_failed += 1
    
    # Test 6: Authorization Flow (if client_id available)
    if client_id:
        auth_params = {
            "client_id": client_id,
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "scope": "read",
            "state": "test123"
        }
        auth_url = f"{base_url}/oauth/authorize?{urllib.parse.urlencode(auth_params)}"
        
        success, output = run_test(
            "OAuth Authorization Endpoint",
            f'curl -s -i "{auth_url}" | head -20'
        )
        
        if success and ("302" in output or "303" in output or "200" in output):
            tests_passed += 1
            if "code=" in output:
                print("   🔓 Authorization code received")
        else:
            tests_failed += 1
    
    # Test 7: MCP Initialize without auth
    mcp_init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "Fast Agent", "version": "1.0.0"}
        }
    }
    
    success, _ = run_test(
        "MCP Initialize (without auth)",
        f'''curl -s -X POST {base_url}/messages \
        -H "Content-Type: application/json" \
        -d '{json.dumps(mcp_init)}' | jq .'''
    )
    if success:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 8: Tools List
    tools_list = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    success, output = run_test(
        "MCP Tools List",
        f'''curl -s -X POST {base_url}/messages \
        -H "Content-Type: application/json" \
        -d '{json.dumps(tools_list)}' | jq .'''
    )
    if success:
        tests_passed += 1
        try:
            result = json.loads(output)
            if "result" in result and "tools" in result["result"]:
                print(f"   🛠️ Tools available: {len(result['result']['tools'])}")
        except:
            pass
    else:
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Fast Agent Test Results")
    print("=" * 60)
    total = tests_passed + tests_failed
    print(f"✅ Passed: {tests_passed}/{total}")
    print(f"❌ Failed: {tests_failed}/{total}")
    print(f"📈 Success Rate: {(tests_passed/total)*100:.1f}%")
    
    return tests_passed, tests_failed


def test_mcp_inspector_config():
    """Test MCP Inspector configuration"""
    print("\n🔍 Testing MCP Inspector Configuration")
    print("=" * 60)
    
    # Check if MCP Inspector config exists
    configs = [
        "mcp-inspector-config.json",
        "mcp-inspector-sse-config.json",
        "mcp-inspector-fastmcp-config.json"
    ]
    
    for config_file in configs:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"✅ Found {config_file}")
                transport = config.get("transport", {}).get("type", "unknown")
                print(f"   Transport: {transport}")
                if transport == "sse":
                    url = config.get("transport", {}).get("config", {}).get("url", "N/A")
                    print(f"   URL: {url}")
        except FileNotFoundError:
            print(f"❌ Missing {config_file}")
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")


def main():
    """Main test runner"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("🚀 Fast Agent OAuth Testing Suite")
    print("📋 Testing OAuth 2.1 + MCP Integration")
    
    # Run OAuth tests
    passed, failed = test_oauth_with_curl(base_url)
    
    # Test MCP Inspector configs
    test_mcp_inspector_config()
    
    # Exit code based on results
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()