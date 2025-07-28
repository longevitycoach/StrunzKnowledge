#!/usr/bin/env python3
"""
Test the complete SSE flow manually
"""

import asyncio
import aiohttp
import json

async def test_sse_flow():
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. Connect to SSE endpoint
        print("1. Connecting to SSE endpoint...")
        async with session.get(f"{base_url}/sse") as resp:
            print(f"   Status: {resp.status}")
            print(f"   Content-Type: {resp.headers.get('Content-Type')}")
            
            # Read the first event
            async for line in resp.content:
                text = line.decode('utf-8').strip()
                if text:
                    print(f"   Received: {text}")
                    
                    # Parse SSE event
                    if text.startswith("event:"):
                        event_type = text[6:].strip()
                        print(f"   Event type: {event_type}")
                    elif text.startswith("data:"):
                        data = text[5:].strip()
                        print(f"   Data: {data}")
                        
                        # Extract session endpoint
                        if "session_id=" in data:
                            # Parse the endpoint and session_id
                            parts = data.split("?session_id=")
                            if len(parts) == 2:
                                endpoint = parts[0]
                                session_id = parts[1]
                                print(f"\n2. Got session endpoint: {endpoint}")
                                print(f"   Session ID: {session_id}")
                                
                                # Now test the messages endpoint with session_id
                                messages_url = f"{base_url}{endpoint}?session_id={session_id}"
                                
                                # Send initialize request
                                print("\n3. Sending initialize request...")
                                init_request = {
                                    "jsonrpc": "2.0",
                                    "method": "initialize",
                                    "params": {
                                        "protocolVersion": "2025-11-05",
                                        "capabilities": {},
                                        "clientInfo": {
                                            "name": "sse-test",
                                            "version": "1.0.0"
                                        }
                                    },
                                    "id": "1"
                                }
                                
                                async with session.post(messages_url, json=init_request) as msg_resp:
                                    print(f"   Status: {msg_resp.status}")
                                    if msg_resp.status == 200:
                                        result = await msg_resp.json()
                                        print(f"   Result: {json.dumps(result, indent=2)}")
                                        
                                        # Test tools/list
                                        print("\n4. Testing tools/list...")
                                        tools_request = {
                                            "jsonrpc": "2.0",
                                            "method": "tools/list",
                                            "id": "2"
                                        }
                                        
                                        async with session.post(messages_url, json=tools_request) as tools_resp:
                                            print(f"   Status: {tools_resp.status}")
                                            if tools_resp.status == 200:
                                                tools_result = await tools_resp.json()
                                                tools = tools_result.get("result", {}).get("tools", [])
                                                print(f"   Found {len(tools)} tools")
                                
                                break
                
                # Only read first few lines
                if text.startswith("data:") and "session_id=" in text:
                    break

if __name__ == "__main__":
    asyncio.run(test_sse_flow())