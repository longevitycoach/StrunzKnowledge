#!/usr/bin/env python3
"""
MCP Server with proper stdio implementation for Claude Desktop
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp import Server, Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Import our tools from enhanced server
try:
    from src.mcp.enhanced_server import StrunzKnowledgeMCP
    HAS_ENHANCED_SERVER = True
except ImportError:
    HAS_ENHANCED_SERVER = False

class StrunzMCPServer:
    def __init__(self):
        self.server = Server("strunz-knowledge")
        self.setup_tools()
        
        # Initialize enhanced server if available
        if HAS_ENHANCED_SERVER:
            self.enhanced = StrunzKnowledgeMCP()
            self.tool_registry = self.enhanced.tool_registry
        else:
            self.tool_registry = {}
    
    def setup_tools(self):
        """Register all MCP tools"""
        
        @self.server.tool()
        async def knowledge_search(query: str, sources: Optional[List[str]] = None, limit: int = 10) -> List[TextContent]:
            """Search Dr. Strunz knowledge base across books, news, and forum"""
            if HAS_ENHANCED_SERVER and "knowledge_search" in self.tool_registry:
                result = await self.tool_registry["knowledge_search"](query, sources, limit)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Enhanced server not available")]
        
        @self.server.tool()
        async def get_dr_strunz_biography() -> List[TextContent]:
            """Get comprehensive biography of Dr. Ulrich Strunz"""
            if HAS_ENHANCED_SERVER and "get_dr_strunz_biography" in self.tool_registry:
                result = await self.tool_registry["get_dr_strunz_biography"]()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Biography not available")]
        
        @self.server.tool()
        async def get_mcp_server_purpose() -> List[TextContent]:
            """Get information about this MCP server's purpose and capabilities"""
            if HAS_ENHANCED_SERVER and "get_mcp_server_purpose" in self.tool_registry:
                result = await self.tool_registry["get_mcp_server_purpose"]()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Server information not available")]
        
        @self.server.tool()
        async def get_vector_db_analysis() -> List[TextContent]:
            """Get analysis of the vector database content"""
            if HAS_ENHANCED_SERVER and "get_vector_db_analysis" in self.tool_registry:
                result = await self.tool_registry["get_vector_db_analysis"]()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Database analysis not available")]
        
        @self.server.tool()
        async def find_contradictions(topic: str, include_reasoning: bool = True) -> List[TextContent]:
            """Find contradictions or evolving viewpoints on a topic"""
            if HAS_ENHANCED_SERVER and "find_contradictions" in self.tool_registry:
                result = await self.tool_registry["find_contradictions"](topic, include_reasoning)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Contradiction analysis not available")]
        
        @self.server.tool()
        async def trace_topic_evolution(topic: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[TextContent]:
            """Trace how Dr. Strunz's views on a topic evolved over time"""
            if HAS_ENHANCED_SERVER and "trace_topic_evolution" in self.tool_registry:
                result = await self.tool_registry["trace_topic_evolution"](topic, start_year, end_year)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Topic evolution analysis not available")]
        
        @self.server.tool()
        async def create_health_protocol(condition: str, user_profile: Optional[Dict] = None) -> List[TextContent]:
            """Create a comprehensive health protocol based on Dr. Strunz's methods"""
            if HAS_ENHANCED_SERVER and "create_health_protocol" in self.tool_registry:
                result = await self.tool_registry["create_health_protocol"](condition, user_profile)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Protocol creation not available")]
        
        @self.server.tool()
        async def compare_approaches(health_issue: str, alternative_approaches: List[str]) -> List[TextContent]:
            """Compare Dr. Strunz's approach with other health methodologies"""
            if HAS_ENHANCED_SERVER and "compare_approaches" in self.tool_registry:
                result = await self.tool_registry["compare_approaches"](health_issue, alternative_approaches)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Comparison not available")]
        
        @self.server.tool()
        async def analyze_supplement_stack(supplements: List[str], health_goals: List[str]) -> List[TextContent]:
            """Analyze a supplement stack based on Dr. Strunz's recommendations"""
            if HAS_ENHANCED_SERVER and "analyze_supplement_stack" in self.tool_registry:
                result = await self.tool_registry["analyze_supplement_stack"](supplements, health_goals)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Supplement analysis not available")]
        
        @self.server.tool()
        async def nutrition_calculator(age: int, gender: str, activity_level: str, health_goals: List[str]) -> List[TextContent]:
            """Calculate personalized nutrition recommendations"""
            if HAS_ENHANCED_SERVER and "nutrition_calculator" in self.tool_registry:
                result = await self.tool_registry["nutrition_calculator"](age, gender, activity_level, health_goals)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Nutrition calculator not available")]
        
        @self.server.tool()
        async def get_community_insights(topic: str, min_engagement: int = 5) -> List[TextContent]:
            """Get insights from the Strunz community forum"""
            if HAS_ENHANCED_SERVER and "get_community_insights" in self.tool_registry:
                result = await self.tool_registry["get_community_insights"](topic, min_engagement)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Community insights not available")]
        
        @self.server.tool()
        async def summarize_posts(category: str, limit: int = 10, timeframe: str = "last_month") -> List[TextContent]:
            """Summarize recent posts by category"""
            if HAS_ENHANCED_SERVER and "summarize_posts" in self.tool_registry:
                result = await self.tool_registry["summarize_posts"](category, limit, timeframe)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Post summaries not available")]
        
        @self.server.tool()
        async def get_trending_insights(days: int = 30) -> List[TextContent]:
            """Get trending health insights from recent content"""
            if HAS_ENHANCED_SERVER and "get_trending_insights" in self.tool_registry:
                result = await self.tool_registry["get_trending_insights"](days)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text="Trending insights not available")]
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = StrunzMCPServer()
    await server.run()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)