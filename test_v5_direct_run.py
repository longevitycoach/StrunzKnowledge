#!/usr/bin/env python3
"""
Test v5 implementation using FastMCP's run() method directly
"""

import subprocess
import time
import requests
import json
import signal
import sys
import os

def test_v5_direct_run():
    """Test the v5 implementation with direct FastMCP run"""
    print("🚀 Testing MCP Server v5 with Direct FastMCP Run")
    print("=" * 60)
    
    # Start the v5 server as a subprocess
    server_process = None
    try:
        # Update main.py to use v5
        print("📝 Updating main.py to use v5 implementation...")
        main_path = "/Users/ma3u/projects/StrunzKnowledge/main.py"
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Replace v4 with v5
        updated_content = content.replace(
            'from src.mcp.sse_server_v4 import app',
            'from src.mcp.sse_server_v5 import run_server'
        ).replace(
            'from src.mcp.sse_server_v4 import app\n        import uvicorn\n        \n        port = int(os.environ.get("PORT", 8000))\n        print(f"🌐 Starting SSE server on port {port}")\n        \n        config = uvicorn.Config(\n            app, \n            host="0.0.0.0", \n            port=port, \n            log_level="info"\n        )\n        server = uvicorn.Server(config)\n        await server.serve()',
            'from src.mcp.sse_server_v5 import run_server\n        await run_server()'
        )
        
        with open(main_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated main.py to use v5")
        
        # Start the server directly using v5's run method
        print("\n🔧 Starting v5 server directly...")
        env = os.environ.copy()
        env['PORT'] = '8080'
        env['TRANSPORT'] = 'sse'
        
        server_process = subprocess.Popen(
            [sys.executable, 'src/mcp/sse_server_v5.py'],
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
                        "name": "test-client-v5",
                        "version": "5.0.0"
                    }
                }
            }
            
            # Connect with SSE
            with requests.post(f"{base_url}/", 
                             json=payload, 
                             headers={'Content-Type': 'application/json'},
                             stream=True) as response:
                
                if response.status_code == 200:
                    print("✅ MCP Initialize: Connected")
                    
                    # Read SSE response
                    for line in response.iter_lines():
                        if line:
                            decoded = line.decode('utf-8')
                            if decoded.startswith('data: '):
                                data = json.loads(decoded[6:])
                                print(f"   Response: {data.get('method', data.get('result', 'Unknown'))}")
                                break
                    
                    results.append(("MCP Initialize", True, 200))
                else:
                    print(f"❌ MCP Initialize: {response.status_code}")
                    results.append(("MCP Initialize", False, response.status_code))
                    
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
            
            with requests.post(f"{base_url}/", 
                             json=payload,
                             headers={'Content-Type': 'application/json'},
                             stream=True) as response:
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            decoded = line.decode('utf-8')
                            if decoded.startswith('data: '):
                                data = json.loads(decoded[6:])
                                if 'result' in data and 'tools' in data['result']:
                                    tools = data['result']['tools']
                                    print(f"✅ List Tools: Found {len(tools)} tools")
                                    for tool in tools:
                                        print(f"   - {tool['name']}")
                                    results.append(("List Tools", True, 200))
                                    break
                else:
                    print(f"❌ List Tools: {response.status_code}")
                    results.append(("List Tools", False, response.status_code))
                    
        except Exception as e:
            print(f"❌ List Tools: Error - {e}")
            results.append(("List Tools", False, 0))
        
        # Summary
        print("\n" + "=" * 60)
        total_tests = len(results)
        passed_tests = sum(1 for _, success, _ in results if success)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🟢 Overall Status: PERFECT! v5 implementation is working correctly")
        elif success_rate >= 80:
            print("🟡 Overall Status: GOOD - Minor issues remaining")
        else:
            print("🔴 Overall Status: ISSUES - v5 needs more work")
        
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
        
        # Restore main.py to v4
        print("📝 Restoring main.py to v4...")
        try:
            with open(main_path, 'r') as f:
                content = f.read()
            
            restored_content = content.replace(
                'from src.mcp.sse_server_v5 import run_server',
                'from src.mcp.sse_server_v4 import app'
            ).replace(
                'from src.mcp.sse_server_v5 import run_server\n        await run_server()',
                'from src.mcp.sse_server_v4 import app\n        import uvicorn\n        \n        port = int(os.environ.get("PORT", 8000))\n        print(f"🌐 Starting SSE server on port {port}")\n        \n        config = uvicorn.Config(\n            app, \n            host="0.0.0.0", \n            port=port, \n            log_level="info"\n        )\n        server = uvicorn.Server(config)\n        await server.serve()'
            )
            
            with open(main_path, 'w') as f:
                f.write(restored_content)
            
            print("✅ Restored main.py")
        except Exception as e:
            print(f"⚠️  Warning: Could not restore main.py: {e}")

if __name__ == "__main__":
    test_v5_direct_run()