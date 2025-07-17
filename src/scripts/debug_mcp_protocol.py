#!/usr/bin/env python3
"""
Debug MCP Protocol Communication

This script tests MCP server communication using the stdio transport,
simulating what Claude Code/Desktop does.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class MCPDebugger:
    def __init__(self, server_command):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        
    def start_server(self):
        """Start the MCP server process"""
        print(f"Starting MCP server: {' '.join(self.server_command)}")
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            cwd=project_root
        )
        time.sleep(2)  # Give server time to start
        
    def send_request(self, method, params=None):
        """Send a JSON-RPC request to the server"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id
        }
        if params:
            request["params"] = params
            
        request_str = json.dumps(request)
        print(f"\n→ Sending: {request_str}")
        
        self.process.stdin.write(request_str + "\n")
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"← Response: {json.dumps(response, indent=2)}")
            return response
        else:
            print("← No response received")
            return None
            
    def check_stderr(self):
        """Check for any error output"""
        try:
            # Non-blocking read of stderr
            import select
            if select.select([self.process.stderr], [], [], 0.1)[0]:
                errors = self.process.stderr.read()
                if errors:
                    print(f"⚠️  Server errors: {errors}")
        except:
            pass
            
    def debug_session(self):
        """Run a full debug session"""
        print("=== MCP Protocol Debugging Session ===\n")
        
        # Test 1: Initialize
        print("Test 1: Initialize")
        response = self.send_request("initialize", {
            "protocolVersion": "2025-03-26",
            "clientInfo": {
                "name": "MCP Debugger",
                "version": "1.0"
            }
        })
        
        if response and "result" in response:
            capabilities = response["result"].get("capabilities", {})
            print(f"✓ Server capabilities: {list(capabilities.keys())}")
            
            # Check for prompts capability
            if "prompts" in capabilities:
                print("✓ Prompts capability is present")
            else:
                print("✗ Prompts capability is MISSING!")
                
        # Test 2: List tools
        print("\nTest 2: List tools")
        response = self.send_request("tools/list")
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✓ Found {len(tools)} tools")
            for tool in tools[:3]:  # Show first 3
                print(f"  - {tool['name']}")
                
        # Test 3: List prompts
        print("\nTest 3: List prompts")
        response = self.send_request("prompts/list")
        if response:
            if "error" in response:
                print(f"✗ Error: {response['error']['message']}")
            elif "result" in response:
                prompts = response["result"].get("prompts", [])
                print(f"✓ Found {len(prompts)} prompts")
                
        # Test 4: Call a tool
        print("\nTest 4: Call a tool")
        response = self.send_request("tools/call", {
            "name": "get_dr_strunz_biography",
            "arguments": {}
        })
        if response and "result" in response:
            print("✓ Tool call successful")
            
        # Check for errors
        self.check_stderr()
        
    def stop_server(self):
        """Stop the server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("\nServer stopped")


def main():
    """Main debug function"""
    print("MCP Protocol Debugger")
    print("====================\n")
    
    # Test 1: Local enhanced server
    print("Testing Local Enhanced Server (stdio)...")
    debugger = MCPDebugger([
        sys.executable, "-m", "src.mcp.enhanced_server"
    ])
    
    try:
        debugger.start_server()
        debugger.debug_session()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        debugger.stop_server()
        
    print("\n" + "="*50 + "\n")
    
    # Test 2: Check if FastMCP is the issue
    print("Checking FastMCP compatibility...")
    try:
        from src.mcp.enhanced_server import server
        print(f"Server type: {type(server)}")
        print(f"Server name: {getattr(server, 'name', 'Unknown')}")
        
        # Check for prompts attribute
        if hasattr(server, 'prompts'):
            print("✓ Server has prompts attribute")
        else:
            print("✗ Server missing prompts attribute")
            
        # Check registered prompts
        if hasattr(server, '_prompts'):
            print(f"✓ Registered prompts: {len(getattr(server, '_prompts', []))}")
        else:
            print("✗ No _prompts registry found")
            
    except Exception as e:
        print(f"Error checking server: {e}")


if __name__ == "__main__":
    main()