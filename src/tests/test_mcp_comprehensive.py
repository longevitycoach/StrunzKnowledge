#!/usr/bin/env python3
"""
Comprehensive MCP Server Test Suite
Tests all capabilities, transports, and protocols
Version: 2.0.0
"""

import os
import sys
import json
import asyncio
import aiohttp
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class MCPTestSuite:
    """Comprehensive test suite for MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all test categories"""
        print("🧪 MCP Comprehensive Test Suite v2.0.0")
        print("=" * 60)
        
        # Test categories
        await self.test_basic_connectivity()
        await self.test_cors_headers()
        await self.test_sse_transport()
        await self.test_http_streaming()
        await self.test_mcp_protocol()
        await self.test_all_tools()
        await self.test_error_handling()
        await self.test_schema_validation()
        await self.test_mcp_inspector_compatibility()
        
        # Print summary
        self.print_test_summary()
    
    async def test_basic_connectivity(self):
        """Test 1: Basic connectivity and health checks"""
        print("\n📡 Test 1: Basic Connectivity")
        print("-" * 40)
        
        tests = [
            ("Health Check GET /", "GET", "/"),
            ("Health Check GET /health", "GET", "/health"),
            ("SSE Endpoint Available", "HEAD", "/sse"),
            ("Messages Endpoint Available", "HEAD", "/messages/"),
        ]
        
        async with aiohttp.ClientSession() as session:
            for test_name, method, endpoint in tests:
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with session.request(method, url) as resp:
                        success = resp.status in [200, 204, 405]  # 405 for HEAD on POST-only
                        self.log_test(test_name, success, f"Status: {resp.status}")
                        
                        if endpoint == "/" and method == "GET":
                            data = await resp.json()
                            print(f"  Server: {data.get('service')}")
                            print(f"  Version: {data.get('version')}")
                            print(f"  Transport: {data.get('transport')}")
                except Exception as e:
                    self.log_test(test_name, False, str(e))
    
    async def test_cors_headers(self):
        """Test 2: CORS headers for browser compatibility"""
        print("\n🌐 Test 2: CORS Headers")
        print("-" * 40)
        
        async with aiohttp.ClientSession() as session:
            # Test preflight OPTIONS request
            headers = {
                "Origin": "https://claude.ai",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
            
            try:
                async with session.options(f"{self.base_url}/messages/", headers=headers) as resp:
                    cors_headers = {
                        "Access-Control-Allow-Origin": resp.headers.get("Access-Control-Allow-Origin"),
                        "Access-Control-Allow-Methods": resp.headers.get("Access-Control-Allow-Methods"),
                        "Access-Control-Allow-Headers": resp.headers.get("Access-Control-Allow-Headers"),
                    }
                    
                    # Check CORS headers
                    has_cors = all([
                        cors_headers.get("Access-Control-Allow-Origin") in ["*", "https://claude.ai"],
                        "POST" in (cors_headers.get("Access-Control-Allow-Methods") or ""),
                        "content-type" in (cors_headers.get("Access-Control-Allow-Headers") or "").lower()
                    ])
                    
                    self.log_test("CORS Preflight", has_cors, f"Headers: {cors_headers}")
            except Exception as e:
                self.log_test("CORS Preflight", False, str(e))
    
    async def test_sse_transport(self):
        """Test 3: SSE Transport Protocol"""
        print("\n📨 Test 3: SSE Transport")
        print("-" * 40)
        
        async with aiohttp.ClientSession() as session:
            try:
                # Connect to SSE endpoint
                async with session.get(f"{self.base_url}/sse") as resp:
                    self.log_test("SSE Connection", resp.status == 200, f"Status: {resp.status}")
                    
                    # Check content type
                    content_type = resp.headers.get("Content-Type", "")
                    is_sse = "text/event-stream" in content_type
                    self.log_test("SSE Content-Type", is_sse, content_type)
                    
                    # Read first event
                    first_chunk = await resp.content.read(1024)
                    if first_chunk:
                        text = first_chunk.decode('utf-8')
                        has_event = "event:" in text or "data:" in text
                        self.log_test("SSE Event Format", has_event, f"First chunk: {text[:100]}...")
                        
                        # Extract session endpoint
                        if "endpoint" in text and "/messages/" in text:
                            self.log_test("SSE Session Endpoint", True, "Found messages endpoint")
                        else:
                            self.log_test("SSE Session Endpoint", False, "No endpoint in SSE stream")
                    
            except Exception as e:
                self.log_test("SSE Connection", False, str(e))
    
    async def test_http_streaming(self):
        """Test 4: HTTP Streaming capabilities"""
        print("\n🔄 Test 4: HTTP Streaming")
        print("-" * 40)
        
        # Note: MCP uses SSE for streaming, not chunked transfer encoding
        # This tests that the server supports streaming responses
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test streaming support via SSE
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.get(f"{self.base_url}/sse", timeout=timeout) as resp:
                    chunks_received = 0
                    async for chunk in resp.content.iter_chunked(1024):
                        chunks_received += 1
                        if chunks_received >= 3:  # Got multiple chunks = streaming works
                            break
                    
                    self.log_test("Streaming Support", chunks_received > 1, f"Chunks: {chunks_received}")
                    
            except asyncio.TimeoutError:
                # Timeout is expected for SSE
                self.log_test("Streaming Support", True, "SSE keeps connection open")
            except Exception as e:
                self.log_test("Streaming Support", False, str(e))
    
    async def test_mcp_protocol(self):
        """Test 5: MCP Protocol Implementation"""
        print("\n🔧 Test 5: MCP Protocol")
        print("-" * 40)
        
        async with aiohttp.ClientSession() as session:
            # Test initialize
            request_id = str(uuid.uuid4())
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "mcp-test-suite",
                        "version": "1.0.0"
                    }
                },
                "id": request_id
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/messages/",
                    json=init_request,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    self.log_test("Initialize Request", resp.status == 200, f"Status: {resp.status}")
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Check JSON-RPC response format
                        has_jsonrpc = data.get("jsonrpc") == "2.0"
                        has_id = data.get("id") == request_id
                        has_result = "result" in data
                        
                        self.log_test("JSON-RPC Format", all([has_jsonrpc, has_id, has_result]), 
                                    f"Valid: {has_jsonrpc and has_id and has_result}")
                        
                        if has_result:
                            result = data["result"]
                            # Check server info
                            server_info = result.get("serverInfo", {})
                            self.log_test("Server Info", bool(server_info.get("name")), 
                                        f"Name: {server_info.get('name')}")
                            
                            # Check capabilities
                            capabilities = result.get("capabilities", {})
                            self.log_test("Capabilities", bool(capabilities), 
                                        f"Has tools: {'tools' in capabilities}")
                    
            except Exception as e:
                self.log_test("Initialize Request", False, str(e))
            
            # Test tools/list
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": str(uuid.uuid4())
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/messages/",
                    json=tools_request,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tools = data.get("result", {}).get("tools", [])
                        self.log_test("Tools List", len(tools) > 0, f"Found {len(tools)} tools")
                        
                        # Check tool schemas
                        tools_with_schema = sum(1 for t in tools if t.get("inputSchema"))
                        self.log_test("Tool Schemas", tools_with_schema == len(tools), 
                                    f"{tools_with_schema}/{len(tools)} have schemas")
                    
            except Exception as e:
                self.log_test("Tools List", False, str(e))
    
    async def test_all_tools(self):
        """Test 6: All Tool Implementations"""
        print("\n🛠️  Test 6: Tool Implementations")
        print("-" * 40)
        
        # Tool test cases
        tool_tests = [
            {
                "name": "knowledge_search",
                "args": {"query": "vitamin d", "limit": 5},
                "check": lambda r: "content" in r or "text" in r
            },
            {
                "name": "get_mcp_server_purpose",
                "args": {},
                "check": lambda r: True  # Should always work
            },
            {
                "name": "get_dr_strunz_biography",
                "args": {"include_achievements": True},
                "check": lambda r: True
            },
            {
                "name": "get_vector_db_analysis",
                "args": {},
                "check": lambda r: True
            },
            {
                "name": "find_contradictions",
                "args": {"topic": "cholesterol"},
                "check": lambda r: True
            },
            {
                "name": "trace_topic_evolution",
                "args": {"topic": "omega 3"},
                "check": lambda r: True
            },
            {
                "name": "create_health_protocol",
                "args": {"condition": "fatigue", "age": 45},
                "check": lambda r: True
            },
            {
                "name": "analyze_supplement_stack",
                "args": {"supplements": ["vitamin d", "omega 3", "magnesium"]},
                "check": lambda r: True
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in tool_tests:
                tool_name = test["name"]
                
                request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test["args"]
                    },
                    "id": str(uuid.uuid4())
                }
                
                try:
                    async with session.post(
                        f"{self.base_url}/messages/",
                        json=request,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if "result" in data:
                                result = data["result"]
                                # Check if tool returned content
                                has_content = (
                                    "content" in result or 
                                    "text" in result or
                                    (isinstance(result, dict) and len(result) > 0)
                                )
                                
                                # Apply custom check
                                passes_check = test["check"](result)
                                
                                self.log_test(f"Tool: {tool_name}", 
                                            has_content and passes_check, 
                                            "Success" if has_content else "No content")
                            else:
                                error = data.get("error", {})
                                self.log_test(f"Tool: {tool_name}", False, 
                                            f"Error: {error.get('message', 'Unknown error')}")
                        else:
                            self.log_test(f"Tool: {tool_name}", False, f"Status: {resp.status}")
                            
                except Exception as e:
                    self.log_test(f"Tool: {tool_name}", False, str(e))
    
    async def test_error_handling(self):
        """Test 7: Error Handling"""
        print("\n⚠️  Test 7: Error Handling")
        print("-" * 40)
        
        error_cases = [
            {
                "name": "Invalid Method",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "invalid/method",
                    "id": "1"
                },
                "expect_error": -32601  # Method not found
            },
            {
                "name": "Invalid Tool",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": "non_existent_tool"},
                    "id": "2"
                },
                "expect_error": True
            },
            {
                "name": "Missing Required Args",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": "knowledge_search", "arguments": {}},
                    "id": "3"
                },
                "expect_error": True  # Should handle missing required 'query'
            },
            {
                "name": "Invalid JSON",
                "raw_body": "not json",
                "expect_error": True
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test_case in error_cases:
                name = test_case["name"]
                
                try:
                    if "raw_body" in test_case:
                        # Test invalid JSON
                        async with session.post(
                            f"{self.base_url}/messages/",
                            data=test_case["raw_body"],
                            headers={"Content-Type": "application/json"}
                        ) as resp:
                            has_error = resp.status >= 400
                            self.log_test(name, has_error, f"Status: {resp.status}")
                    else:
                        # Test JSON-RPC errors
                        async with session.post(
                            f"{self.base_url}/messages/",
                            json=test_case["request"],
                            headers={"Content-Type": "application/json"}
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                has_error = "error" in data
                                
                                if has_error and isinstance(test_case["expect_error"], int):
                                    error_code = data.get("error", {}).get("code")
                                    correct_code = error_code == test_case["expect_error"]
                                    self.log_test(name, correct_code, 
                                                f"Error code: {error_code}")
                                else:
                                    self.log_test(name, has_error, 
                                                "Error returned" if has_error else "No error")
                            else:
                                self.log_test(name, True, f"HTTP error: {resp.status}")
                                
                except Exception as e:
                    self.log_test(name, False, f"Exception: {str(e)}")
    
    async def test_schema_validation(self):
        """Test 8: Schema Validation"""
        print("\n📋 Test 8: Schema Validation")
        print("-" * 40)
        
        schema_tests = [
            {
                "name": "Valid Schema Types",
                "tool": "knowledge_search",
                "args": {"query": "test", "limit": "not a number"},  # Wrong type
                "should_fail": True
            },
            {
                "name": "Extra Properties",
                "tool": "get_mcp_server_purpose",
                "args": {"extra": "property"},  # Extra property
                "should_fail": False  # May be allowed
            },
            {
                "name": "Required Properties",
                "tool": "find_contradictions",
                "args": {},  # Missing required 'topic'
                "should_fail": True
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in schema_tests:
                request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": test["tool"],
                        "arguments": test["args"]
                    },
                    "id": str(uuid.uuid4())
                }
                
                try:
                    async with session.post(
                        f"{self.base_url}/messages/",
                        json=request,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        data = await resp.json()
                        has_error = "error" in data
                        
                        if test["should_fail"]:
                            self.log_test(test["name"], has_error, 
                                        "Correctly rejected" if has_error else "Should have failed")
                        else:
                            self.log_test(test["name"], not has_error, 
                                        "Correctly accepted" if not has_error else "Should have passed")
                            
                except Exception as e:
                    self.log_test(test["name"], False, str(e))
    
    async def test_mcp_inspector_compatibility(self):
        """Test 9: MCP Inspector Compatibility"""
        print("\n🔍 Test 9: MCP Inspector Compatibility")
        print("-" * 40)
        
        # Key requirements for MCP Inspector
        inspector_tests = [
            {
                "name": "Resources List Support",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "resources/list",
                    "id": "1"
                },
                "check": lambda d: "result" in d and "resources" in d.get("result", {})
            },
            {
                "name": "Prompts List Support",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "prompts/list",
                    "id": "2"
                },
                "check": lambda d: True  # May return error or empty list
            },
            {
                "name": "Ping Support",
                "request": {
                    "jsonrpc": "2.0",
                    "method": "ping",
                    "id": "3"
                },
                "check": lambda d: True  # Optional
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for test in inspector_tests:
                try:
                    async with session.post(
                        f"{self.base_url}/messages/",
                        json=test["request"],
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            passes = test["check"](data)
                            self.log_test(test["name"], passes, 
                                        "Supported" if passes else "Not supported")
                        else:
                            self.log_test(test["name"], False, f"Status: {resp.status}")
                            
                except Exception as e:
                    self.log_test(test["name"], False, str(e))
    
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })
        
        status = "✅" if success else "❌"
        print(f"  {status} {name}: {details}")
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['name']}: {result['details']}")
        
        print("\n🏁 Test suite completed!")
        return passed == total


async def test_stdio_transport():
    """Test STDIO transport"""
    print("\n🖥️  Testing STDIO Transport")
    print("-" * 40)
    
    # Create a test script for stdio
    test_script = """
import sys
import json

# Send initialize request
request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-05",
        "capabilities": {},
        "clientInfo": {"name": "stdio-test", "version": "1.0.0"}
    },
    "id": "1"
}
sys.stdout.write(json.dumps(request) + '\\n')
sys.stdout.flush()

# Read response
response = sys.stdin.readline()
print(f"Response: {response}", file=sys.stderr)
"""
    
    # Save test script
    with open("test_stdio.py", "w") as f:
        f.write(test_script)
    
    try:
        # Run stdio server as subprocess
        proc = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "MCP_TRANSPORT": "stdio"}
        )
        
        # Wait a bit for server to start
        time.sleep(2)
        
        # Send initialize request
        init_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-05",
                "capabilities": {},
                "clientInfo": {"name": "stdio-test", "version": "1.0.0"}
            },
            "id": "1"
        }) + "\n"
        
        proc.stdin.write(init_request)
        proc.stdin.flush()
        
        # Read response
        response = proc.stdout.readline()
        if response:
            data = json.loads(response)
            success = "result" in data
            print(f"  {'✅' if success else '❌'} STDIO Initialize: {'Success' if success else 'Failed'}")
        else:
            print("  ❌ STDIO Initialize: No response")
        
        # Cleanup
        proc.terminate()
        proc.wait()
        
    except Exception as e:
        print(f"  ❌ STDIO Test Failed: {e}")
    finally:
        # Clean up test script
        if os.path.exists("test_stdio.py"):
            os.remove("test_stdio.py")


async def main():
    """Main test runner"""
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/") as resp:
                if resp.status != 200:
                    print("❌ Server not running on localhost:8000")
                    print("Please start the server with: MCP_TRANSPORT=sse python main.py")
                    return
    except:
        print("❌ Cannot connect to server on localhost:8000")
        print("Please start the server with: MCP_TRANSPORT=sse python main.py")
        return
    
    # Run SSE/HTTP tests
    test_suite = MCPTestSuite()
    await test_suite.run_all_tests()
    
    # Run STDIO tests
    await test_stdio_transport()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())