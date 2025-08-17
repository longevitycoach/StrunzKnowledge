#!/usr/bin/env python3
"""
Test v6 hybrid implementation using FastMCP sse_app with uvicorn
"""

import subprocess
import time
import requests
import json
import signal
import sys
import os

def test_v6_hybrid():
    """Test the v6 hybrid implementation"""
    print("🚀 Testing MCP Server v6 with Hybrid Approach")
    print("=" * 60)
    
    # Start the v6 server as a subprocess
    server_process = None
    try:
        # Start the server directly using v6
        print("\n🔧 Starting v6 server...")
        env = os.environ.copy()
        env['PORT'] = '8080'
        env['TRANSPORT'] = 'sse'
        
        server_process = subprocess.Popen(
            [sys.executable, 'src/mcp/sse_server_v6.py'],
            cwd='/Users/ma3u/projects/StrunzKnowledge',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give server time to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start!")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        print("✅ Server started successfully")
        
        # Run tests
        base_url = "http://localhost:8080"
        results = []
        
        # Test 1: Root endpoint with SSE
        print("\n📍 Testing root endpoint with SSE...")
        try:
            headers = {'Accept': 'text/event-stream'}
            response = requests.get(f"{base_url}/", headers=headers, timeout=5, stream=True)
            success = response.status_code == 200
            print(f"{'✅' if success else '❌'} Root SSE: {response.status_code}")
            
            if success:
                # Try to read first event
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        print(f"   First event: {decoded[:100]}...")
                        break
            
            results.append(("Root SSE", success, response.status_code))
            response.close()
        except Exception as e:
            print(f"❌ Root SSE: Error - {e}")
            results.append(("Root SSE", False, 0))
        
        # Test 2: MCP Initialize
        print("\n🔧 Testing MCP protocol...")
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
                        "name": "test-client-v6",
                        "version": "6.0.0"
                    }
                }
            }
            
            # Connect with SSE
            response = requests.post(f"{base_url}/", 
                                   json=payload, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=5)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} MCP Initialize: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response (raw): {response.text[:200]}...")
            
            results.append(("MCP Initialize", success, response.status_code))
                    
        except Exception as e:
            print(f"❌ MCP Initialize: Error - {e}")
            results.append(("MCP Initialize", False, 0))
        
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
                        print(f"   Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"   - {tool['name']}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            
            results.append(("List Tools", success, response.status_code))
                    
        except Exception as e:
            print(f"❌ List Tools: Error - {e}")
            results.append(("List Tools", False, 0))
        
        # Test 4: Call a tool
        print("\n🔨 Testing tool execution...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_health_stats",
                    "arguments": {}
                }
            }
            
            response = requests.post(f"{base_url}/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            success = response.status_code in [200, 202]
            print(f"{'✅' if success else '❌'} Tool Call: {response.status_code}")
            
            if success and response.text:
                try:
                    data = json.loads(response.text)
                    if 'result' in data:
                        result = data['result']
                        print(f"   Tool result preview: {str(result)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            
            results.append(("Tool Call", success, response.status_code))
                    
        except Exception as e:
            print(f"❌ Tool Call: Error - {e}")
            results.append(("Tool Call", False, 0))
        
        # Summary
        print("\n" + "=" * 60)
        total_tests = len(results)
        passed_tests = sum(1 for _, success, _ in results if success)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🟢 Overall Status: PERFECT! v6 implementation is working correctly")
            print("✨ All routing issues have been resolved!")
        elif success_rate >= 80:
            print("🟡 Overall Status: GOOD - Minor issues remaining")
        else:
            print("🔴 Overall Status: ISSUES - v6 needs more work")
        
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
    test_v6_hybrid()