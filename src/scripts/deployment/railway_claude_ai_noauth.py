#!/usr/bin/env python3
"""
Claude.ai Compatible MCP Server WITHOUT OAuth
This version completely removes OAuth endpoints to ensure Claude.ai compatibility
"""

import os
import sys
import asyncio
import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our components
from src.mcp.claude_compatible_server import (
    app,
    health_check,
    railway_health,
    railway_status,
    sse_endpoint,
    messages_endpoint,
    mcp_server_endpoint,
    tool_registry,
    PROTOCOL_VERSION
)

# Remove ALL OAuth endpoints
routes_to_remove = [
    "/.well-known/oauth-authorization-server",
    "/.well-known/oauth-protected-resource", 
    "/oauth/register",
    "/oauth/authorize",
    "/oauth/token",
    "/oauth/userinfo"
]

# Remove OAuth routes from the app
app.routes = [route for route in app.routes if route.path not in routes_to_remove]

# Override MCP resource discovery to ensure NO authentication
@app.get("/.well-known/mcp/resource")
async def mcp_resource_metadata_noauth():
    """MCP resource metadata for discovery - NO AUTHENTICATION"""
    base_url = os.environ.get('BASE_URL', 'https://strunz.up.railway.app')
    
    # Base metadata WITHOUT any authentication
    return {
        "mcpVersion": PROTOCOL_VERSION,
        "transport": ["sse"],
        "endpoints": {
            "sse": f"{base_url}/sse",
            "messages": f"{base_url}/messages"
        }
        # NO authentication field at all
    }

# Claude.ai specific endpoint that clearly indicates no auth needed
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth_noauth(
    org_id: str, 
    auth_id: str,
    redirect_url: Optional[str] = None,
    open_in_browser: Optional[int] = None
):
    """Claude.ai specific authentication endpoint - NO AUTH VERSION"""
    logger.info(f"Claude.ai auth request: org={org_id}, auth={auth_id}")
    
    # Always return that auth is not required
    return {
        "status": "success",
        "auth_not_required": True,
        "server_url": "https://strunz.up.railway.app",
        "message": "No authentication required - server is publicly accessible"
    }

# Add debug endpoint
@app.get("/debug/noauth")
async def debug_noauth():
    """Debug endpoint to confirm this is the no-auth version"""
    return {
        "version": "0.9.3-noauth",
        "oauth_enabled": False,
        "oauth_endpoints_removed": routes_to_remove,
        "message": "This is the Claude.ai compatible version without OAuth"
    }

async def main():
    """Main entry point for no-auth version"""
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"Starting Claude.ai NO-AUTH MCP server on port {port}")
    logger.info(f"Protocol version: {PROTOCOL_VERSION}")
    logger.info(f"Tools available: {len(tool_registry)}")
    logger.info("OAuth endpoints: REMOVED for Claude.ai compatibility")
    
    import uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())