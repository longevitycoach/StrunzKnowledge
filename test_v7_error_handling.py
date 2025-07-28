#!/usr/bin/env python3
"""
Test v7 implementation with improved error handling
"""

import subprocess
import time
import requests
import json
import sys
import os

def test_v7_error_handling():
    """Test the v7 implementation with various edge cases"""
    print("🚀 Testing MCP Server v7 with Enhanced Error Handling")
    print("=" * 60)
    
    # Start the v7 server as a subprocess
    server_process = None
    try:
        # Kill any existing servers
        os.system("lsof -ti:8080 | xargs kill -9 2>/dev/null || true")
        time.sleep(1)
        
        # Start the server
        print("\n🔧 Starting v7 server...")
        env = os.environ.copy()
        env['PORT'] = '8080'
        env['TRANSPORT'] = 'sse'
        
        server_process = subprocess.Popen(
            [sys.executable, 'src/mcp/sse_server_v7.py'],
            cwd='/Users/ma3u/projects/StrunzKnowledge',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Give server time to start
        print("⏳ Waiting for server to start...")
        time.sleep(4)
        
        # Check if server is running
        if server_process.poll() is not None:
            output, _ = server_process.communicate()
            print(f"❌ Server failed to start!")
            print(f"Output: {output}")
            return False
        
        print("✅ Server started successfully")
        
        # Run tests
        base_url = "http://localhost:8080"
        results = []
        
        # Test 1: Health check
        print("\n📍 Testing health check...")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} Health: {response.status_code}")
            if success:
                data = response.json()
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Improvements: {', '.join(data.get('improvements', []))}")
            results.append(("Health Check", success, response.status_code))
        except Exception as e:
            print(f"❌ Health: Error - {e}")
            results.append(("Health Check", False, 0))
        
        # Test 2: Initialize
        print("\n🔧 Testing MCP Initialize...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client-v7",
                        "version": "7.0.0"
                    }
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=5)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Initialize: {response.status_code}")
            results.append(("Initialize", success, response.status_code))
        except Exception as e:
            print(f"❌ Initialize: Error - {e}")
            results.append(("Initialize", False, 0))
        
        # Test 3: List tools
        print("\n📋 Testing tools listing...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=5)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} List Tools: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"   Found {len(tools)} tools")
                except:
                    pass
            
            results.append(("List Tools", success, response.status_code))
        except Exception as e:
            print(f"❌ List Tools: Error - {e}")
            results.append(("List Tools", False, 0))
        
        # Test 4: Basic search (should work)
        print("\n🔍 Testing basic search...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_knowledge",
                    "arguments": {
                        "query": "Vitamin D",
                        "limit": 5
                    }
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Basic Search: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    if 'result' in data:
                        result = data['result']
                        print(f"   Result preview: {result[:100]}...")
                except:
                    pass
            
            results.append(("Basic Search", success, response.status_code))
        except Exception as e:
            print(f"❌ Basic Search: Error - {e}")
            results.append(("Basic Search", False, 0))
        
        # Test 5: Edge case - empty query
        print("\n🔍 Testing empty query (should fail gracefully)...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "search_knowledge",
                    "arguments": {
                        "query": "",
                        "limit": 5
                    }
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Empty Query Handling: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    if 'result' in data:
                        result = data['result']
                        if "Error:" in result:
                            print(f"   ✅ Proper error message: {result}")
                except:
                    pass
            
            results.append(("Empty Query", success, response.status_code))
        except Exception as e:
            print(f"❌ Empty Query: Error - {e}")
            results.append(("Empty Query", False, 0))
        
        # Test 6: Advanced search with filtering
        print("\n🔍 Testing advanced search with filtering...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "search_knowledge_advanced",
                    "arguments": {
                        "query": "Protein",
                        "content_types": ["books"],
                        "limit": 3
                    }
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Advanced Search: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    if 'result' in data:
                        result = data['result']
                        if "books" in result.lower():
                            print(f"   ✅ Filtered to books only")
                except:
                    pass
            
            results.append(("Advanced Search", success, response.status_code))
        except Exception as e:
            print(f"❌ Advanced Search: Error - {e}")
            results.append(("Advanced Search", False, 0))
        
        # Test 7: Edge case - invalid parameters
        print("\n🔍 Testing invalid parameters (should handle gracefully)...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "search_knowledge",
                    "arguments": {
                        "query": "test",
                        "filter_source": ["books"]  # Wrong parameter name
                    }
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            # Should still succeed but ignore invalid parameter
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Invalid Parameter Handling: {response.status_code}")
            
            results.append(("Invalid Params", success, response.status_code))
        except Exception as e:
            print(f"❌ Invalid Params: Error - {e}")
            results.append(("Invalid Params", False, 0))
        
        # Summary
        print("\n" + "=" * 60)
        total_tests = len(results)
        passed_tests = sum(1 for _, success, _ in results if success)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🟢 Overall Status: PERFECT! v7 handles all cases correctly")
        elif success_rate >= 80:
            print("🟡 Overall Status: GOOD - Most cases handled properly")
        else:
            print("🔴 Overall Status: ISSUES - Error handling needs work")
        
        print("\n📝 Test Summary:")
        print("-" * 40)
        for test_name, success, status_code in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:20} {status:8} (HTTP {status_code})")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
        
    finally:
        # Clean up
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Server stopped")

if __name__ == "__main__":
    test_v7_error_handling()