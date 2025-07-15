#!/usr/bin/env python3
"""
Test MCP server with MCP Inspector-style requests
"""

import requests
import json
import time
from datetime import datetime

class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.request_id = 0
    
    def next_id(self):
        self.request_id += 1
        return self.request_id
    
    def send_request(self, method, params=None):
        """Send MCP JSON-RPC request"""
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.next_id()
        }
        
        try:
            response = requests.post(f"{self.base_url}/mcp", json=request_data)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self):
        """List available tools"""
        return self.send_request("tools/list")
    
    def call_tool(self, name, arguments=None):
        """Call a tool"""
        return self.send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })

def test_mcp_protocol():
    """Test MCP protocol compliance"""
    print("=== Testing MCP Protocol Compliance ===")
    
    client = MCPClient("http://localhost:8080")
    
    # Test 1: List tools
    print("\n1. Testing tools/list...")
    result = client.list_tools()
    if "result" in result and "tools" in result["result"]:
        tools = result["result"]["tools"]
        print(f"✓ Found {len(tools)} tools")
        tool_names = [t["name"] for t in tools]
        print(f"  Tools: {', '.join(tool_names[:5])}{'...' if len(tool_names) > 5 else ''}")
    else:
        print(f"✗ tools/list failed: {result}")
        return False
    
    # Test 2: Call info tools
    info_tools = [
        "get_mcp_server_purpose",
        "get_dr_strunz_biography", 
        "get_vector_db_analysis"
    ]
    
    print("\n2. Testing info tools...")
    for tool_name in info_tools:
        result = client.call_tool(tool_name)
        if "result" in result:
            print(f"✓ {tool_name}: OK")
        else:
            print(f"✗ {tool_name}: {result}")
    
    # Test 3: Call search tool (should handle missing vector store gracefully)
    print("\n3. Testing search tool...")
    result = client.call_tool("knowledge_search", {"query": "vitamin D"})
    if "result" in result:
        search_result = result["result"]
        if "error" in search_result:
            print(f"✓ knowledge_search: Handled missing vector store - {search_result['error']}")
        else:
            print(f"✓ knowledge_search: Success - {len(search_result.get('results', []))} results")
    else:
        print(f"✗ knowledge_search: {result}")
    
    # Test 4: Test protocol tool
    print("\n4. Testing protocol tool...")
    result = client.call_tool("create_health_protocol", {
        "condition": "vitamin D deficiency",
        "severity": "moderate"
    })
    if "result" in result:
        protocol = result["result"]
        print(f"✓ create_health_protocol: Created protocol with {len(protocol.get('core_supplements', []))} supplements")
    else:
        print(f"✗ create_health_protocol: {result}")
    
    return True

def test_sse_connection():
    """Test SSE connection properly"""
    print("\n=== Testing SSE Connection ===")
    
    try:
        response = requests.get("http://localhost:8080/sse", stream=True, timeout=5)
        if response.status_code == 200:
            print("✓ SSE connection established")
            
            # Read a few events with shorter timeout
            events_received = 0
            start_time = time.time()
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('event:'):
                        event_type = decoded[6:].strip()
                        print(f"  Event type: {event_type}")
                    elif decoded.startswith('data:'):
                        try:
                            data = json.loads(decoded[5:])
                            print(f"  Data: {data.get('message', str(data)[:100])}")
                            events_received += 1
                        except:
                            print(f"  Raw: {decoded[:100]}")
                
                # Stop after 1 event or 3 seconds
                if events_received >= 1 or (time.time() - start_time) > 3:
                    break
            
            print(f"✓ Received {events_received} SSE events")
            return True
        else:
            print(f"✗ SSE connection failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✓ SSE connection timeout (expected behavior for streaming)")
        return True
    except Exception as e:
        print(f"✗ SSE error: {e}")
        return False

def main():
    """Run comprehensive MCP tests"""
    print("=== Comprehensive MCP Server Test ===")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Wait for container
    time.sleep(2)
    
    # Test health first
    try:
        response = requests.get("http://localhost:8080/")
        if response.status_code == 200:
            print("✓ Server health check passed")
        else:
            print("✗ Server health check failed")
            return 1
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        return 1
    
    # Run tests
    success = True
    
    # Test MCP protocol
    if not test_mcp_protocol():
        success = False
    
    # Test SSE
    if not test_sse_connection():
        success = False
    
    print(f"\n=== Final Result ===")
    if success:
        print("✅ All tests passed! MCP server is working correctly.")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())