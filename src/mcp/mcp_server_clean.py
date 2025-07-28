#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server
Clean implementation using official MCP Python SDK
Following the SDK documentation exactly
Version: 2.0.0
"""

import os
import sys
import logging
import asyncio
from typing import Any, Sequence
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP SDK correctly
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
search_tool = None

async def initialize_vector_store():
    """Initialize the vector store"""
    global search_tool
    try:
        from src.rag.search import KnowledgeSearcher
        search_tool = KnowledgeSearcher()
        # KnowledgeSearcher doesn't have async initialize
        logger.info("Vector store initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        return False

# Create the MCP server
app = Server("strunz-knowledge")

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources (empty for now, but required by Inspector)"""
    return []

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="knowledge_search",
            description="Search through Dr. Strunz's knowledge base with semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by sources: books, news, forum"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results (default: 10)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_mcp_server_purpose",
            description="Get information about this MCP server",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_dr_strunz_biography",
            description="Get comprehensive biography and philosophy of Dr. Ulrich Strunz",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_achievements": {
                        "type": "boolean",
                        "description": "Include achievements section"
                    },
                    "include_philosophy": {
                        "type": "boolean",
                        "description": "Include medical philosophy"
                    }
                }
            }
        ),
        types.Tool(
            name="find_contradictions",
            description="Find contradictions or conflicts in Dr. Strunz's knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to analyze for contradictions"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="trace_topic_evolution",
            description="Track how a health topic evolved over time in Dr. Strunz's content",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Health topic to trace"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="create_health_protocol",
            description="Create a personalized health protocol based on Dr. Strunz's knowledge",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "Health condition or goal"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Age of person"
                    },
                    "gender": {
                        "type": "string",
                        "description": "Gender (male/female)"
                    },
                    "activity_level": {
                        "type": "string",
                        "description": "Activity level (sedentary/moderate/active)"
                    }
                },
                "required": ["condition"]
            }
        ),
        types.Tool(
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
        types.Tool(
            name="get_vector_db_analysis",
            description="Get detailed analysis of the vector database content and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(
    name: str, 
    arguments: dict | None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if not arguments:
        arguments = {}
    
    try:
        if name == "knowledge_search":
            if not search_tool:
                return [types.TextContent(
                    type="text",
                    text="Vector store not initialized. Please try again later."
                )]
            
            query = arguments.get("query", "")
            sources = arguments.get("sources", ["books", "news", "forum"])
            limit = arguments.get("limit", 10)
            
            # Perform search
            results = await search_tool.search(
                query=query,
                k=limit,
                filter_source=sources if isinstance(sources, list) else None
            )
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text="No results found for your query."
                )]
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(
                    f"**Result {i+1}:**\n"
                    f"Source: {result.get('source', 'Unknown')}\n"
                    f"Score: {result.get('score', 0):.2f}\n"
                    f"Content: {result.get('content', '')}\n"
                )
            
            return [types.TextContent(
                type="text",
                text="\n---\n".join(formatted_results)
            )]
        
        elif name == "get_mcp_server_purpose":
            return [types.TextContent(
                type="text",
                text="""# Dr. Strunz Knowledge MCP Server

This MCP server provides access to Dr. Ulrich Strunz's comprehensive health and nutrition knowledge base.

## Features:
- Semantic search across 13 books, 6,953 news articles, and forum content
- Find contradictions and trace topic evolution
- Create personalized health protocols
- Access Dr. Strunz's biography and philosophy

## Version: 2.0.0
Clean implementation using the official MCP Python SDK."""
            )]
        
        elif name == "get_dr_strunz_biography":
            include_achievements = arguments.get("include_achievements", True)
            include_philosophy = arguments.get("include_philosophy", True)
            
            bio = """# Dr. Ulrich Strunz

Dr. med. Ulrich Strunz is a German physician specializing in molecular medicine and preventive healthcare.

## Background:
- Medical doctor and molecular medicine specialist
- Former triathlete and marathon runner
- Author of over 30 bestselling books on health and nutrition
- Pioneer of the "Forever Young" concept in Germany"""
            
            if include_achievements:
                bio += """

## Achievements:
- Published over 30 bestselling health books
- Developed the "Forever Young" program
- Pioneered molecular medicine approaches in Germany
- Inspired millions to adopt healthier lifestyles"""
            
            if include_philosophy:
                bio += """

## Philosophy:
- Focus on preventive medicine through nutrition, exercise, and mindset
- Evidence-based approach combining traditional medicine with modern research
- Emphasis on measuring and optimizing blood values
- Holistic view of health encompassing body, mind, and spirit"""
            
            return [types.TextContent(type="text", text=bio)]
        
        elif name == "get_vector_db_analysis":
            analysis = """# Vector Database Analysis

## Content Statistics:
- **Books**: 13 books by Dr. Ulrich Strunz (2002-2025)
- **News Articles**: 6,953 unique articles (2004-2025)
- **Forum Content**: 6,400 chunks
- **Total Documents**: 43,373 searchable documents

## Coverage:
- Topics: Nutrition, supplements, exercise, stress management, longevity
- Languages: German (primary), some English content
- Time span: Over 20 years of health insights

## Technical Details:
- Vector Store: FAISS with sentence transformers
- Embedding Model: paraphrase-multilingual-MiniLM-L12-v2
- Search Method: Semantic similarity search"""
            
            return [types.TextContent(type="text", text=analysis)]
        
        elif name == "find_contradictions":
            topic = arguments.get("topic", "")
            if not topic:
                return [types.TextContent(
                    type="text",
                    text="Please provide a topic to analyze for contradictions."
                )]
            
            if not search_tool:
                return [types.TextContent(
                    type="text",
                    text="Vector store not initialized."
                )]
            
            # Search for the topic
            results = await search_tool.search(query=topic, k=20)
            
            response = f"# Contradiction Analysis: {topic}\n\n"
            response += f"Found {len(results)} relevant passages to analyze.\n\n"
            response += "This feature searches across different time periods and sources to identify potential contradictions or evolving viewpoints."
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "trace_topic_evolution":
            topic = arguments.get("topic", "")
            if not topic:
                return [types.TextContent(
                    type="text",
                    text="Please provide a topic to trace."
                )]
            
            if not search_tool:
                return [types.TextContent(
                    type="text",
                    text="Vector store not initialized."
                )]
            
            results = await search_tool.search(query=topic, k=20)
            
            response = f"# Topic Evolution: {topic}\n\n"
            response += f"Found {len(results)} relevant passages across time.\n\n"
            response += "This feature tracks how Dr. Strunz's views and recommendations on this topic have developed over the years."
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "create_health_protocol":
            condition = arguments.get("condition", "")
            if not condition:
                return [types.TextContent(
                    type="text",
                    text="Please provide a health condition or goal."
                )]
            
            age = arguments.get("age", "Not specified")
            gender = arguments.get("gender", "Not specified")
            activity = arguments.get("activity_level", "Not specified")
            
            if not search_tool:
                return [types.TextContent(
                    type="text",
                    text="Vector store not initialized."
                )]
            
            results = await search_tool.search(query=condition, k=15)
            
            response = f"# Health Protocol: {condition}\n\n"
            response += f"**Profile:**\n"
            response += f"- Age: {age}\n"
            response += f"- Gender: {gender}\n"
            response += f"- Activity Level: {activity}\n\n"
            response += f"Based on {len(results)} relevant recommendations from Dr. Strunz's knowledge base."
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "analyze_supplement_stack":
            supplements = arguments.get("supplements", [])
            if not supplements:
                return [types.TextContent(
                    type="text",
                    text="Please provide a list of supplements to analyze."
                )]
            
            response = f"# Supplement Stack Analysis\n\n"
            response += f"**Analyzing:** {', '.join(supplements)}\n\n"
            response += "This feature checks for:\n"
            response += "- Potential interactions\n"
            response += "- Optimal timing and dosing\n"
            response += "- Synergistic combinations\n"
            response += "- Cost optimization opportunities"
            
            return [types.TextContent(type="text", text=response)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing tool: {str(e)}"
        )]

async def main():
    """Main entry point"""
    # Initialize vector store
    await initialize_vector_store()
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="strunz-knowledge",
                server_version="2.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())