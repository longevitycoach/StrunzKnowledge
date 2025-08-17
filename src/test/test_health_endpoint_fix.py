#!/usr/bin/env python3
"""
Test script to verify health endpoint fix
Tests both local and production endpoints
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class HealthEndpointTester:
    def __init__(self):
        self.results = []
        
    async def test_endpoint(self, url, endpoint_name):
        """Test a single endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                print(f"\n📍 Testing {endpoint_name}: {url}")
                
                # Test health endpoint
                health_url = f"{url}/health"
                async with session.get(health_url) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"   Status: {status}")
                    print(f"   Content-Type: {content_type}")
                    
                    if status == 200:
                        if 'application/json' in content_type:
                            data = await response.json()
                            print(f"   ✅ Valid JSON response")
                            print(f"   Version: {data.get('version', 'unknown')}")
                            print(f"   MCP Implementation: {data.get('mcp_implementation', 'unknown')}")
                            print(f"   SSE Endpoint: {data.get('endpoints', {}).get('sse', 'unknown')}")
                            self.results.append((endpoint_name, "PASS", "Health endpoint working correctly"))
                        else:
                            text = await response.text()
                            print(f"   ❌ Non-JSON response: {text[:100]}...")
                            self.results.append((endpoint_name, "FAIL", f"Non-JSON response: {content_type}"))
                    else:
                        text = await response.text()
                        print(f"   ❌ Error {status}: {text[:100]}...")
                        self.results.append((endpoint_name, "FAIL", f"HTTP {status}: {text[:50]}"))
                
                # Test SSE endpoint availability
                sse_url = f"{url}/sse"
                async with session.get(sse_url, headers={'Accept': 'text/event-stream'}) as response:
                    if response.status == 200:
                        print(f"   ✅ SSE endpoint available at /sse")
                    else:
                        print(f"   ⚠️  SSE endpoint returned {response.status}")
                        
            except aiohttp.ClientError as e:
                print(f"   ❌ Connection error: {e}")
                self.results.append((endpoint_name, "FAIL", f"Connection error: {str(e)}"))
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing error: {e}")
                self.results.append((endpoint_name, "FAIL", f"JSON parsing error: {str(e)}"))
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                self.results.append((endpoint_name, "FAIL", f"Unexpected error: {str(e)}"))
    
    async def run_tests(self):
        """Run all tests"""
        print("🧪 Dr. Strunz Knowledge Health Endpoint Test")
        print("=" * 50)
        
        # Test local server
        await self.test_endpoint("http://localhost:8000", "Local Server")
        
        # Test Railway production
        await self.test_endpoint("https://strunz.up.railway.app", "Railway Production")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print("-" * 50)
        
        passed = sum(1 for _, status, _ in self.results if status == "PASS")
        total = len(self.results)
        
        for name, status, message in self.results:
            emoji = "✅" if status == "PASS" else "❌"
            print(f"{emoji} {name}: {message}")
        
        print("-" * 50)
        print(f"Total: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
        return passed == total

async def main():
    """Main test function"""
    tester = HealthEndpointTester()
    success = await tester.run_tests()
    
    if not success:
        print("\n⚠️  Some tests failed. Please check the server configuration.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())