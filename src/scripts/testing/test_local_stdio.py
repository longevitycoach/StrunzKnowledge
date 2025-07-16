#!/usr/bin/env python3
"""
Test local MCP server with stdio transport
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def test_stdio_server():
    """Test the MCP server with stdio transport"""
    print("=== Testing MCP Server with stdio transport ===")
    
    # Start the server
    print("Starting MCP server...")
    try:
        # Run the enhanced server in stdio mode
        process = subprocess.Popen(
            [sys.executable, "-c", "from src.mcp.enhanced_server import main; main()"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        
        # Send tools/list request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        print("Sending tools/list request...")
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    tools = response["result"]["tools"]
                    print(f"✓ Found {len(tools)} tools via stdio")
                    return True
                else:
                    print(f"✗ No result in response: {response}")
                    return False
            else:
                print("✗ No response received")
                return False
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error reading response: {e}")
            return False
        
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return False
    finally:
        # Clean up
        if 'process' in locals():
            process.terminate()
            process.wait()

def main():
    """Run stdio test"""
    print("Testing MCP server in local stdio mode...")
    
    # Set up environment for local mode
    import os
    os.environ.pop('RAILWAY_ENVIRONMENT', None)
    
    success = test_stdio_server()
    
    if success:
        print("\n✅ Local stdio test passed!")
        return 0
    else:
        print("\n❌ Local stdio test failed!")
        return 1

if __name__ == "__main__":
    exit(main())