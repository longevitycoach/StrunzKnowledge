#!/usr/bin/env python3
"""
Test our MCP server using the official Anthropic MCP client
This will help us understand what Claude.ai expects
"""

import asyncio
import json
import logging
from typing import Dict, Any
import httpx

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OfficialMCPClientTester:
    """Test MCP server using official client patterns"""
    
    def __init__(self, server_url: str = "https://strunz.up.railway.app"):
        self.server_url = server_url
        self.client = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_discovery(self):
        """Test MCP resource discovery"""
        logger.info("Testing MCP resource discovery...")
        
        # Test .well-known/mcp/resource
        response = await self.client.get(f"{self.server_url}/.well-known/mcp/resource")
        logger.info(f"MCP Resource Discovery: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"MCP Version: {data.get('mcpVersion')}")
            logger.info(f"Transport: {data.get('transport')}")
            logger.info(f"Authentication: {data.get('authentication', {}).get('type')}")
            return data
        return None
    
    async def test_oauth_flow(self):
        """Test OAuth2 flow"""
        logger.info("\nTesting OAuth2 flow...")
        
        # Step 1: Get OAuth metadata
        response = await self.client.get(f"{self.server_url}/.well-known/oauth-authorization-server")
        if response.status_code == 200:
            oauth_meta = response.json()
            logger.info(f"OAuth Issuer: {oauth_meta.get('issuer')}")
            logger.info(f"Authorization Endpoint: {oauth_meta.get('authorization_endpoint')}")
            logger.info(f"Token Endpoint: {oauth_meta.get('token_endpoint')}")
        
        # Step 2: Register client
        register_data = {
            "client_name": "Official MCP Test Client",
            "redirect_uris": ["https://claude.ai/api/callback"],
            "grant_types": ["authorization_code"],
            "response_types": ["code"]
        }
        
        response = await self.client.post(
            f"{self.server_url}/oauth/register",
            json=register_data
        )
        
        if response.status_code == 200:
            client_data = response.json()
            logger.info(f"Client Registration Success: {client_data.get('client_id')}")
            return client_data
        else:
            logger.error(f"Client Registration Failed: {response.status_code}")
            return None
    
    async def test_claude_ai_endpoints(self):
        """Test Claude.ai specific endpoints"""
        logger.info("\nTesting Claude.ai specific endpoints...")
        
        # Test the endpoint Claude.ai is looking for
        test_endpoints = [
            "/api/organizations/test-org/mcp/start-auth/test-auth",
            "/api/mcp/start-auth",
            "/mcp/start-auth",
            "/.well-known/mcp-server"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = await self.client.get(f"{self.server_url}{endpoint}")
                logger.info(f"{endpoint}: {response.status_code}")
            except Exception as e:
                logger.error(f"{endpoint}: Error - {e}")
    
    async def test_mcp_initialize(self):
        """Test MCP initialization"""
        logger.info("\nTesting MCP initialization...")
        
        # Standard MCP initialize
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "Official MCP Test",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = await self.client.post(
            f"{self.server_url}/messages",
            json=request
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Initialize Response: {json.dumps(data, indent=2)}")
            return data
        else:
            logger.error(f"Initialize Failed: {response.status_code}")
            return None
    
    async def test_sse_connection(self):
        """Test SSE connection"""
        logger.info("\nTesting SSE connection...")
        
        # Try to connect to SSE endpoint
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        
        try:
            response = await self.client.get(
                f"{self.server_url}/sse",
                headers=headers,
                timeout=5.0
            )
            
            logger.info(f"SSE Connection: {response.status_code}")
            if response.status_code == 200:
                # Read first few lines
                content = response.text[:500]
                logger.info(f"SSE Content Preview: {content}")
        except httpx.TimeoutException:
            logger.info("SSE connection established (timeout expected for streaming)")
        except Exception as e:
            logger.error(f"SSE Error: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("=== Official MCP Client Test Suite ===")
        logger.info(f"Server: {self.server_url}")
        logger.info("=" * 50)
        
        # Run tests in sequence
        await self.test_discovery()
        await self.test_oauth_flow()
        await self.test_claude_ai_endpoints()
        await self.test_mcp_initialize()
        await self.test_sse_connection()
        
        logger.info("\n=== Test Complete ===")


async def main():
    """Main test runner"""
    # Test against production
    async with OfficialMCPClientTester() as tester:
        await tester.run_all_tests()
    
    # Also test what Claude.ai might be doing
    logger.info("\n=== Simulating Claude.ai Behavior ===")
    async with httpx.AsyncClient() as client:
        # Claude.ai seems to expect this endpoint
        org_id = "705d85ef-0c93-4581-9884-d0151d86bb4a"
        auth_id = "test-auth-id"
        
        url = f"https://strunz.up.railway.app/api/organizations/{org_id}/mcp/start-auth/{auth_id}"
        logger.info(f"Testing Claude.ai URL: {url}")
        
        try:
            response = await client.get(url)
            logger.info(f"Response: {response.status_code}")
            logger.info(f"Content: {response.text}")
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())