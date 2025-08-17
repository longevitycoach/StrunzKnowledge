#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - FINAL VERSION
Official MCP Python SDK implementation with all migrations complete
No feature flags - all tools permanently enabled
Version: 3.0.0
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

# Import MCP SDK
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

# Global variables for all tool modules
search_tool = None
health_tools = None
analysis_tools = None
gemini_tools = None

async def initialize_vector_store():
    """Initialize the vector store and all tool modules"""
    global search_tool, health_tools, analysis_tools, gemini_tools
    try:
        # Initialize base search tool
        from src.rag.search import KnowledgeSearcher
        search_tool = KnowledgeSearcher()
        logger.info("Knowledge searcher initialized")
        
        # Initialize all tool batches (no more feature flags!)
        from src.mcp.batch2_health_tools import HealthAssessmentTools
        health_tools = HealthAssessmentTools(search_tool)
        logger.info("Health assessment tools initialized")
        
        from src.mcp.batch3_analysis_tools import ComplexAnalysisTools
        analysis_tools = ComplexAnalysisTools(search_tool)
        logger.info("Complex analysis tools initialized")
        
        from src.mcp.batch4_gemini_tools import GeminiEnhancedTools
        gemini_tools = GeminiEnhancedTools(search_tool)
        logger.info("Gemini-enhanced tools initialized")
        
        if os.environ.get('GOOGLE_GEMINI_API_KEY'):
            logger.info("Gemini API key detected - AI features available")
        else:
            logger.info("No Gemini API key - AI features will use fallback messages")
        
        logger.info("All tool modules initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize tools: {e}")
        return False

# Create the MCP server
app = Server("strunz-knowledge")

# Global prompt handler
prompt_handler = None

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources for navigation"""
    from src.mcp.resource_navigation import ResourceNavigator
    
    navigator = ResourceNavigator(search_tool)
    resources = await navigator.list_resources()
    
    return [
        types.Resource(
            uri=res["uri"],
            name=res["name"],
            description=res["description"],
            mimeType="application/json"
        )
        for res in resources
    ]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available tools - no more feature flags!"""
    tools = [
        # Core search tool
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
        
        # Basic information tools
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
        
        # Health assessment tools (Batch 2)
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
            name="analyze_health_topic",
            description="Get comprehensive analysis of a health topic from Dr. Strunz's perspective",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Health topic to analyze"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["basic", "moderate", "comprehensive"],
                        "description": "Analysis depth (default: moderate)"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="analyze_forum_trends",
            description="Analyze forum discussion trends on a specific health topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to analyze in forum discussions"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for analysis (optional)"
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
        
        # Complex analysis tools (Batch 3)
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
            name="get_vector_db_analysis",
            description="Get detailed analysis of the vector database content and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="search_by_date_range",
            description="Search knowledge base with temporal filtering by date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD format)"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results (default: 10)",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="ping",
            description="Health check endpoint to verify system components are operational",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    # Add Gemini tools if API key is configured
    gemini_tools_list = [
        types.Tool(
            name="search_knowledge_gemini",
            description="Search with Gemini-powered AI synthesis for intelligent answers",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to synthesize (1-20)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by sources: books, news, forum"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="ask_strunz_gemini",
            description="Ask a direct question about Dr. Strunz's health philosophy with AI-powered answers",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Your health or nutrition question"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about your situation"
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="analyze_health_topic_gemini",
            description="Get comprehensive AI-synthesized analysis of a health topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Health topic to analyze"
                    },
                    "aspects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific aspects to focus on"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="validate_gemini_connection",
            description="Validate Gemini API connection and configuration status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    # Always include Gemini tools (they handle unavailability gracefully)
    tools.extend(gemini_tools_list)
    
    return tools

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompts for knowledge activation"""
    from src.mcp.prompt_templates import MCPPromptHandler
    
    global prompt_handler
    if not prompt_handler:
        prompt_handler = MCPPromptHandler()
    
    prompts = await prompt_handler.list_prompts()
    
    return [
        types.Prompt(
            name=p["name"],
            description=p["description"],
            arguments=[
                types.PromptArgument(
                    name=arg["name"],
                    description=arg["description"],
                    required=True
                )
                for arg in p["arguments"]
            ]
        )
        for p in prompts
    ]

@app.get_prompt()
async def get_prompt(
    name: str,
    arguments: dict | None
) -> types.GetPromptResult:
    """Get a specific prompt filled with arguments"""
    from src.mcp.prompt_templates import MCPPromptHandler
    
    global prompt_handler
    if not prompt_handler:
        prompt_handler = MCPPromptHandler()
    
    if not arguments:
        arguments = {}
    
    result = await prompt_handler.get_prompt(name, arguments)
    
    if "error" in result:
        return types.GetPromptResult(
            description=result["error"],
            messages=[]
        )
    
    return types.GetPromptResult(
        description=f"Knowledge activation prompt for {name}",
        messages=result["messages"]
    )

@app.call_tool()
async def call_tool(
    name: str, 
    arguments: dict | None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls - all tools permanently enabled"""
    
    if not arguments:
        arguments = {}
    
    try:
        # Core search tool (Batch 3 enhanced)
        if name == "knowledge_search":
            if analysis_tools:
                query = arguments.get("query", "")
                if not query:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a search query."
                    )]
                
                k = arguments.get("k", arguments.get("limit", 10))
                sources = arguments.get("sources")
                
                result = await analysis_tools.knowledge_search(
                    query=query,
                    k=k,
                    sources=sources
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Knowledge base not initialized."
                )]
        
        # Basic information tools
        elif name == "get_mcp_server_purpose":
            return [types.TextContent(
                type="text",
                text="""# Dr. Strunz Knowledge MCP Server

This MCP server provides access to Dr. Ulrich Strunz's comprehensive health and nutrition knowledge base.

## Features:
- Semantic search across 13 books, 6,953 news articles, and forum content
- AI-enhanced search with Gemini integration (when configured)
- Health protocol creation and supplement analysis
- Contradiction detection and topic evolution tracking

## Version: 3.0.0
Final version with complete FastMCP migration to Official MCP SDK."""
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
        
        # Health assessment tools (Batch 2)
        elif name == "create_health_protocol":
            if health_tools:
                condition = arguments.get("condition", "")
                if not condition:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a health condition or goal."
                    )]
                
                result = await health_tools.create_health_protocol(
                    condition=condition,
                    age=arguments.get("age"),
                    gender=arguments.get("gender"),
                    activity_level=arguments.get("activity_level")
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Health tools not initialized."
                )]
        
        elif name == "analyze_supplement_stack":
            if health_tools:
                supplements = arguments.get("supplements", [])
                if not supplements:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a list of supplements to analyze."
                    )]
                
                result = await health_tools.analyze_supplement_stack(supplements)
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Health tools not initialized."
                )]
        
        elif name == "analyze_health_topic":
            if health_tools:
                topic = arguments.get("topic", "")
                if not topic:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a health topic to analyze."
                    )]
                
                depth = arguments.get("depth", "moderate")
                result = await health_tools.analyze_health_topic(topic, depth)
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Health tools not initialized."
                )]
        
        elif name == "analyze_forum_trends":
            if health_tools:
                topic = arguments.get("topic", "")
                if not topic:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a topic to analyze."
                    )]
                
                time_period = arguments.get("time_period")
                result = await health_tools.analyze_forum_trends(topic, time_period)
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Health tools not initialized."
                )]
        
        elif name == "trace_topic_evolution":
            if health_tools:
                topic = arguments.get("topic", "")
                if not topic:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a topic to trace."
                    )]
                
                result = await health_tools.trace_topic_evolution(topic)
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Health tools not initialized."
                )]
        
        # Complex analysis tools (Batch 3)
        elif name == "find_contradictions":
            if analysis_tools:
                topic = arguments.get("topic", "")
                if not topic:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a topic to analyze for contradictions."
                    )]
                
                time_window = arguments.get("time_window")
                result = await analysis_tools.find_contradictions(
                    topic=topic,
                    time_window=time_window
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Analysis tools not initialized."
                )]
        
        elif name == "get_vector_db_analysis":
            if analysis_tools:
                result = await analysis_tools.get_vector_db_analysis()
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Analysis tools not initialized."
                )]
        
        elif name == "search_by_date_range":
            if analysis_tools:
                query = arguments.get("query", "")
                if not query:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a search query."
                    )]
                
                result = await analysis_tools.search_by_date_range(
                    query=query,
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date"),
                    k=arguments.get("k", 10)
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Analysis tools not initialized."
                )]
        
        elif name == "ping":
            if analysis_tools:
                result = await analysis_tools.ping()
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="# System Health Check\n\n✅ MCP Server is operational\n\n*Health check endpoint*"
                )]
        
        # Gemini-enhanced tools (Batch 4)
        elif name == "search_knowledge_gemini":
            if gemini_tools:
                query = arguments.get("query", "")
                if not query:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a search query."
                    )]
                
                result = await gemini_tools.search_knowledge_gemini(
                    query=query,
                    limit=arguments.get("limit", 10),
                    sources=arguments.get("sources")
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Gemini tools not initialized."
                )]
        
        elif name == "ask_strunz_gemini":
            if gemini_tools:
                question = arguments.get("question", "")
                if not question:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a question."
                    )]
                
                result = await gemini_tools.ask_strunz_gemini(
                    question=question,
                    context=arguments.get("context")
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Gemini tools not initialized."
                )]
        
        elif name == "analyze_health_topic_gemini":
            if gemini_tools:
                topic = arguments.get("topic", "")
                if not topic:
                    return [types.TextContent(
                        type="text",
                        text="Please provide a health topic to analyze."
                    )]
                
                result = await gemini_tools.analyze_health_topic_gemini(
                    topic=topic,
                    aspects=arguments.get("aspects")
                )
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="Gemini tools not initialized."
                )]
        
        elif name == "validate_gemini_connection":
            if gemini_tools:
                result = await gemini_tools.validate_gemini_connection()
                return [types.TextContent(type="text", text=result)]
            else:
                return [types.TextContent(
                    type="text",
                    text="# Gemini Validation\n\nGemini tools not initialized."
                )]
        
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
    # Initialize all tool modules
    await initialize_vector_store()
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        # Create initialization options
        init_options = InitializationOptions(
            server_name="strunz-knowledge",
            server_version="3.0.0",
            capabilities=types.ServerCapabilities(
                tools=types.ToolsCapability(),
                prompts=types.PromptsCapability(),
                resources=types.ResourcesCapability(),
            ),
        )
        
        await app.run(
            read_stream,
            write_stream,
            init_options
        )

if __name__ == "__main__":
    asyncio.run(main())