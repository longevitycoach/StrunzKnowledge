#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server
Clean implementation using ONLY the official MCP Python SDK
Version: 2.0.0
"""

import os
import sys
import logging
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP SDK
try:
    from mcp import Server, Tool
    from mcp.server import NotificationOptions, RequestContext
    from mcp.server.models import InitializationOptions
    from mcp.types import (
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
    # Import both stdio AND sse transports
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
except ImportError as e:
    print(f"Error: MCP SDK not installed. Please run: pip install mcp")
    print(f"Details: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize vector store and tools
vector_store = None
search_tool = None

async def initialize_vector_store():
    """Initialize the vector store"""
    global vector_store, search_tool
    try:
        from src.rag.search import SearchTool
        search_tool = SearchTool()
        await search_tool.initialize()
        logger.info("Vector store initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        return False

# Create MCP Server instance
mcp_server = Server("strunz-knowledge")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools"""
    tools = [
        Tool(
            name="knowledge_search",
            description="Search through Dr. Strunz's knowledge base with semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by sources: books, news, forum"
                    },
                    "limit": {"type": "integer", "description": "Number of results (default: 10)"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_mcp_server_purpose",
            description="Get information about this MCP server",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_dr_strunz_biography",
            description="Get Dr. Strunz's biography and philosophy",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="find_contradictions",
            description="Find contradictions or conflicts in Dr. Strunz's knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to analyze for contradictions"}
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="trace_topic_evolution",
            description="Track how a health topic evolved over time in Dr. Strunz's content",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Health topic to trace"}
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="create_health_protocol",
            description="Create a personalized health protocol based on Dr. Strunz's knowledge",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Health condition or goal"},
                    "age": {"type": "integer", "description": "Age of person"},
                    "gender": {"type": "string", "description": "Gender (male/female)"},
                    "activity_level": {"type": "string", "description": "Activity level"}
                },
                "required": ["condition"]
            }
        )
    ]
    return tools

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Optional[Dict[str, Any]], context: Optional[RequestContext]) -> List[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    
    if name == "knowledge_search":
        if not search_tool:
            return [TextContent(text="Vector store not initialized. Please try again later.")]
        
        query = arguments.get("query", "")
        sources = arguments.get("sources", ["books", "news", "forum"])
        limit = arguments.get("limit", 10)
        
        try:
            results = await search_tool.search(
                query=query,
                k=limit,
                filter_source=sources if isinstance(sources, list) else None
            )
            
            if not results:
                return [TextContent(text="No results found for your query.")]
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(
                    f"**Result {i+1}:**\n"
                    f"Source: {result.get('source', 'Unknown')}\n"
                    f"Score: {result.get('score', 0):.2f}\n"
                    f"Content: {result.get('content', '')}\n"
                )
            
            return [TextContent(text="\n---\n".join(formatted_results))]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [TextContent(text=f"Search failed: {str(e)}")]
    
    elif name == "get_mcp_server_purpose":
        return [TextContent(text="""
# Dr. Strunz Knowledge MCP Server

This MCP server provides access to Dr. Ulrich Strunz's comprehensive health and nutrition knowledge base.

## Features:
- Semantic search across 13 books, 6,953 news articles, and forum content
- Find contradictions and trace topic evolution
- Create personalized health protocols
- Access Dr. Strunz's biography and philosophy

## Version: 2.0.0
Clean implementation using the official MCP Python SDK with proper SSE/HTTP support.
        """)]
    
    elif name == "get_dr_strunz_biography":
        return [TextContent(text="""
# Dr. Ulrich Strunz

Dr. med. Ulrich Strunz is a German physician specializing in molecular medicine and preventive healthcare.

## Background:
- Medical doctor and molecular medicine specialist
- Former triathlete and marathon runner
- Author of over 30 bestselling books on health and nutrition
- Pioneer of the "Forever Young" concept in Germany

## Philosophy:
- Focus on preventive medicine through nutrition, exercise, and mindset
- Evidence-based approach combining traditional medicine with modern research
- Emphasis on measuring and optimizing blood values
- Holistic view of health encompassing body, mind, and spirit
        """)]
    
    elif name == "find_contradictions":
        topic = arguments.get("topic", "")
        # Simplified implementation for now
        return [TextContent(text=f"Analyzing contradictions for topic: {topic}\n\nThis feature will search for conflicting information across different time periods and sources.")]
    
    elif name == "trace_topic_evolution":
        topic = arguments.get("topic", "")
        # Simplified implementation for now
        return [TextContent(text=f"Tracing evolution of topic: {topic}\n\nThis feature will show how Dr. Strunz's views on this topic have developed over time.")]
    
    elif name == "create_health_protocol":
        condition = arguments.get("condition", "")
        # Simplified implementation for now
        return [TextContent(text=f"Creating health protocol for: {condition}\n\nThis feature will generate a personalized protocol based on Dr. Strunz's recommendations.")]
    
    else:
        return [TextContent(text=f"Tool '{name}' not implemented")]

async def run_stdio():
    """Run the server with stdio transport (for Claude Desktop)"""
    logger.info("Starting MCP server with stdio transport...")
    
    # Initialize vector store
    await initialize_vector_store()
    
    # Run with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="strunz-knowledge",
                server_version="2.0.0"
            ),
            raise_exceptions=True
        )

async def run_sse():
    """Run the server with SSE transport (for web/Claude.ai)"""
    logger.info("Starting MCP server with SSE transport...")
    
    # Initialize vector store
    await initialize_vector_store()
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    
    # Run with SSE transport
    from mcp.server.sse import create_sse_transport
    
    async with create_sse_transport(port=port) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="strunz-knowledge",
                server_version="2.0.0"
            )
        )

async def main():
    """Main entry point - detect transport and run appropriate server"""
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    
    if transport == "sse" or os.environ.get("RAILWAY_ENVIRONMENT"):
        # Use SSE for web deployment
        await run_sse()
    else:
        # Use stdio for local Claude Desktop
        await run_stdio()

if __name__ == "__main__":
    asyncio.run(main())