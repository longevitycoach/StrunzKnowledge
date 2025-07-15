#!/usr/bin/env python3
"""
FastMCP Server with full MCP protocol support for Railway deployment
Supports SSE transport for Claude Desktop and Fast Agent testing
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastMCP
try:
    from fastmcp import FastMCP
    logger.info("FastMCP imported successfully")
except ImportError as e:
    logger.error(f"Failed to import FastMCP: {e}")
    raise

# Import enhanced server tools
try:
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    from src.rag.search import KnowledgeSearcher
    logger.info("Enhanced server modules imported")
except ImportError as e:
    logger.warning(f"Could not import enhanced modules: {e}")
    StrunzKnowledgeMCP = None

def create_fastmcp_server():
    """Create FastMCP server with all Strunz Knowledge tools"""
    
    # Create FastMCP instance
    mcp = FastMCP("strunz-knowledge")
    logger.info("FastMCP server created")
    
    # Initialize knowledge base if available
    knowledge_base = None
    if StrunzKnowledgeMCP:
        try:
            enhanced = StrunzKnowledgeMCP()
            knowledge_base = enhanced
            logger.info(f"Knowledge base initialized with {len(enhanced.tool_registry)} tools")
        except Exception as e:
            logger.warning(f"Could not initialize knowledge base: {e}")
    
    # Register MCP tools
    
    @mcp.tool()
    async def knowledge_search(
        query: str,
        sources: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search Dr. Strunz knowledge base across books, news, and forum"""
        if knowledge_base and "knowledge_search" in knowledge_base.tool_registry:
            return await knowledge_base.tool_registry["knowledge_search"](query, sources, limit)
        return {
            "results": [],
            "error": "Knowledge base not available"
        }
    
    @mcp.tool()
    async def get_dr_strunz_biography() -> Dict[str, Any]:
        """Get comprehensive biography of Dr. Ulrich Strunz"""
        if knowledge_base and "get_dr_strunz_biography" in knowledge_base.tool_registry:
            return await knowledge_base.tool_registry["get_dr_strunz_biography"]()
        return {
            "biography": "Dr. Ulrich Strunz is a renowned German physician and author specializing in preventive medicine.",
            "error": "Full biography not available"
        }
    
    @mcp.tool()
    async def get_mcp_server_purpose() -> Dict[str, Any]:
        """Get information about this MCP server's purpose and capabilities"""
        return {
            "purpose": "Dr. Strunz Knowledge Base MCP Server",
            "description": "A comprehensive knowledge base containing Dr. Ulrich Strunz's medical insights, research, and recommendations",
            "version": "1.0.0",
            "transport": "SSE/HTTP",
            "capabilities": {
                "search": True,
                "protocols": True,
                "analysis": True,
                "community": True
            },
            "tools_available": 19 if knowledge_base else 3
        }
    
    @mcp.tool()
    async def find_contradictions(
        topic: str,
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """Find contradictions or evolving viewpoints on a topic"""
        if knowledge_base and "find_contradictions" in knowledge_base.tool_registry:
            return await knowledge_base.tool_registry["find_contradictions"](topic, include_reasoning)
        return {
            "contradictions": [],
            "error": "Contradiction analysis not available"
        }
    
    @mcp.tool()
    async def create_health_protocol(
        condition: str,
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a comprehensive health protocol based on Dr. Strunz's methods"""
        if knowledge_base and "create_health_protocol" in knowledge_base.tool_registry:
            return await knowledge_base.tool_registry["create_health_protocol"](condition, user_profile)
        return {
            "protocol": {
                "condition": condition,
                "recommendations": ["Consult Dr. Strunz's books for detailed protocols"],
                "note": "Full protocol generation requires knowledge base access"
            }
        }
    
    @mcp.tool()
    async def test_connection() -> Dict[str, Any]:
        """Test MCP connection and server status"""
        return {
            "status": "connected",
            "server": "FastMCP Strunz Knowledge Server",
            "timestamp": datetime.now().isoformat(),
            "transport": os.environ.get("MCP_TRANSPORT", "unknown"),
            "environment": os.environ.get("RAILWAY_ENVIRONMENT", "local")
        }
    
    logger.info(f"Registered {len([m for m in dir(mcp) if hasattr(getattr(mcp, m), '__call__') and not m.startswith('_')])} tools")
    return mcp

def main():
    """Main entry point for FastMCP server"""
    logger.info("Starting FastMCP Strunz Knowledge Server")
    
    # Create server
    mcp = create_fastmcp_server()
    
    # Determine transport based on environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Railway deployment - use SSE for Claude Desktop
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Running on Railway with SSE transport on port {port}")
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        # Local development - use stdio by default
        transport = os.environ.get('MCP_TRANSPORT', 'stdio')
        
        if transport == 'sse':
            port = int(os.environ.get('PORT', 8000))
            logger.info(f"Running SSE transport on port {port}")
            mcp.run(transport="sse", host="127.0.0.1", port=port)
        elif transport == 'http':
            port = int(os.environ.get('PORT', 8000))
            logger.info(f"Running HTTP transport on port {port}")
            mcp.run(transport="http", host="127.0.0.1", port=port, path="/mcp")
        else:
            logger.info("Running stdio transport")
            mcp.run()

if __name__ == "__main__":
    main()