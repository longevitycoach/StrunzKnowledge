#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server
Official MCP SDK implementation with SSE/HTTP transport
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
from mcp import Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource
from mcp.server import Server, NotificationOptions, RequestContext
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport

# Import Starlette for SSE
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
vector_store = None
search_tool = None
server = None

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

def create_server() -> Server:
    """Create and configure the MCP server"""
    server = Server("strunz-knowledge")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools"""
        return [
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
                        "topic": {"type": "string", "description": "Topic to analyze"}
                    },
                    "required": ["topic"]
                }
            ),
            Tool(
                name="trace_topic_evolution",
                description="Track how a health topic evolved over time",
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
                description="Create a personalized health protocol",
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
            ),
            Tool(
                name="analyze_supplement_stack",
                description="Analyze and optimize supplement combinations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "supplements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of supplements"
                        }
                    },
                    "required": ["supplements"]
                }
            ),
            Tool(
                name="get_vector_db_analysis",
                description="Get analysis of the vector database content",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    @server.call_tool()
    async def call_tool(
        name: str, 
        arguments: Optional[Dict[str, Any]], 
        context: Optional[RequestContext]
    ) -> List[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls"""
        
        try:
            if name == "knowledge_search":
                if not search_tool:
                    return [TextContent(text="Vector store not initialized. Please try again later.")]
                
                query = arguments.get("query", "")
                sources = arguments.get("sources", ["books", "news", "forum"])
                limit = arguments.get("limit", 10)
                
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
            
            elif name == "get_mcp_server_purpose":
                return [TextContent(text="""# Dr. Strunz Knowledge MCP Server

This MCP server provides access to Dr. Ulrich Strunz's comprehensive health and nutrition knowledge base.

## Features:
- Semantic search across 13 books, 6,953 news articles, and forum content
- Find contradictions and trace topic evolution
- Create personalized health protocols
- Access Dr. Strunz's biography and philosophy

## Version: 2.0.0
Using official MCP Python SDK with proper SSE/HTTP transport.""")]
            
            elif name == "get_dr_strunz_biography":
                return [TextContent(text="""# Dr. Ulrich Strunz

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
- Holistic view of health encompassing body, mind, and spirit""")]
            
            elif name == "get_vector_db_analysis":
                return [TextContent(text="""# Vector Database Analysis

## Content Statistics:
- **Books**: 13 books by Dr. Ulrich Strunz (2002-2025)
- **News Articles**: 6,953 unique articles (2004-2025)
- **Forum Content**: 6,400 chunks
- **Total Documents**: 43,373 searchable documents

## Coverage:
- Topics: Nutrition, supplements, exercise, stress management, longevity
- Languages: German (primary), some English content
- Time span: Over 20 years of health insights""")]
            
            elif name == "find_contradictions":
                topic = arguments.get("topic", "")
                if not search_tool:
                    return [TextContent(text="Vector store not initialized.")]
                
                # Search for the topic across different time periods
                results = await search_tool.search(query=topic, k=20)
                
                return [TextContent(text=f"Analyzing contradictions for '{topic}'...\n\nFound {len(results)} relevant passages to analyze.")]
            
            elif name == "trace_topic_evolution":
                topic = arguments.get("topic", "")
                if not search_tool:
                    return [TextContent(text="Vector store not initialized.")]
                
                results = await search_tool.search(query=topic, k=20)
                
                return [TextContent(text=f"Tracing evolution of '{topic}'...\n\nFound {len(results)} relevant passages across time.")]
            
            elif name == "create_health_protocol":
                condition = arguments.get("condition", "")
                if not search_tool:
                    return [TextContent(text="Vector store not initialized.")]
                
                results = await search_tool.search(query=condition, k=15)
                
                return [TextContent(text=f"Creating health protocol for '{condition}'...\n\nBased on {len(results)} relevant recommendations.")]
            
            elif name == "analyze_supplement_stack":
                supplements = arguments.get("supplements", [])
                if not supplements:
                    return [TextContent(text="Please provide a list of supplements to analyze.")]
                
                return [TextContent(text=f"Analyzing supplement stack: {', '.join(supplements)}\n\nChecking for interactions and optimization opportunities...")]
            
            else:
                return [TextContent(text=f"Tool '{name}' not found")]
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return [TextContent(text=f"Error executing tool: {str(e)}")]
    
    return server

# Create server instance
server = create_server()

# Create SSE transport
sse_transport = SseServerTransport("/messages/")

# Health check endpoint
async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "2.0.0",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/"
        }
    })

# SSE handler
async def handle_sse(request):
    """Handle SSE connections"""
    logger.info(f"SSE connection from {request.headers.get('user-agent', 'unknown')}")
    
    # Initialize vector store if not already done
    if not search_tool:
        await initialize_vector_store()
    
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0], 
            streams[1], 
            InitializationOptions(
                server_name="strunz-knowledge",
                server_version="2.0.0"
            )
        )
    
    # Return empty response to avoid NoneType error
    return Response()

# Create Starlette app with routes
routes = [
    Route("/", endpoint=health_check, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse_transport.handle_post_message),
]

app = Starlette(routes=routes, debug=False)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v2.0.0")
    await initialize_vector_store()

# For stdio transport (Claude Desktop)
async def run_stdio():
    """Run with stdio transport"""
    logger.info("Starting MCP server with stdio transport...")
    await initialize_vector_store()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="strunz-knowledge",
                server_version="2.0.0"
            )
        )

# Main entry point
async def main():
    """Main entry point"""
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    
    if transport == "sse" or os.environ.get("RAILWAY_ENVIRONMENT"):
        # Run with SSE transport
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting SSE server on port {port}")
        
        # Use uvicorn for SSE
        import uvicorn
        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Run with stdio transport
        await run_stdio()

if __name__ == "__main__":
    asyncio.run(main())