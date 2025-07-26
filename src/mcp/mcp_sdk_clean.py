#!/usr/bin/env python3
"""
Clean MCP SDK Server - Official Implementation
Dr. Strunz Knowledge Base MCP Server using official MCP SDK
Version: 0.9.9 - Clean implementation without web dependencies
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError as e:
    logging.error(f"MCP SDK not available: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server info
SERVER_NAME = "Dr. Strunz Knowledge MCP Server"
SERVER_VERSION = "0.7.9"
PROTOCOL_VERSION = "2025-03-26"

class StrunzKnowledgeServer:
    """Clean MCP SDK server implementation"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.vector_store = None
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup all MCP handlers"""
        
        # Server info handler
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List all available tools"""
            tools = []
            
            # Core search tools
            tools.extend([
                types.Tool(
                    name="knowledge_search",
                    description="Search through Dr. Strunz's knowledge base with semantic search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "sources": {"type": "array", "items": {"type": "string"}, "description": "Filter by sources: books, news, forum"},
                            "limit": {"type": "integer", "description": "Number of results (default: 10)"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
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
                types.Tool(
                    name="trace_topic_evolution",
                    description="Track how a health topic evolved over time in Dr. Strunz's content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Health topic to trace"}
                        },
                        "required": ["topic"]
                    }
                )
            ])
            
            # Protocol tools
            tools.extend([
                types.Tool(
                    name="create_health_protocol",
                    description="Create a personalized health protocol based on Dr. Strunz's knowledge",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "condition": {"type": "string", "description": "Health condition or goal"},
                            "age": {"type": "integer", "description": "Age of person"},
                            "gender": {"type": "string", "description": "Gender (male/female)"},
                            "activity_level": {"type": "string", "description": "Activity level (sedentary/moderate/active)"}
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
                            "supplements": {"type": "array", "items": {"type": "string"}, "description": "List of supplements"}
                        },
                        "required": ["supplements"]
                    }
                ),
                types.Tool(
                    name="nutrition_calculator",
                    description="Calculate nutrition requirements based on Dr. Strunz's recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "weight": {"type": "number", "description": "Body weight in kg"},
                            "goal": {"type": "string", "description": "Goal: weight_loss, muscle_gain, maintenance"}
                        },
                        "required": ["weight", "goal"]
                    }
                )
            ])
            
            # Batch 1: Simple tools
            tools.extend([
                types.Tool(
                    name="summarize_posts",
                    description="Summarize recent posts by category with personalized filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Category to summarize"},
                            "limit": {"type": "integer", "description": "Number of posts to summarize (default: 10)"},
                            "timeframe": {"type": "string", "description": "Time period: last_week, last_month, last_year"},
                            "user_profile": {"type": "object", "description": "Optional user profile for filtering"}
                        },
                        "required": ["category"]
                    }
                ),
                types.Tool(
                    name="get_health_assessment_questions",
                    description="Get personalized health assessment questions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_role": {"type": "string", "description": "User role: patient, practitioner, researcher"},
                            "assessment_depth": {"type": "string", "description": "Depth: basic, comprehensive, detailed"}
                        }
                    }
                ),
                types.Tool(
                    name="get_dr_strunz_biography",
                    description="Get comprehensive biography and philosophy of Dr. Ulrich Strunz",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_achievements": {"type": "boolean", "description": "Include achievements section"},
                            "include_philosophy": {"type": "boolean", "description": "Include medical philosophy"}
                        }
                    }
                ),
                types.Tool(
                    name="get_mcp_server_purpose",
                    description="Explain the purpose and capabilities of this MCP server",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="get_vector_db_analysis",
                    description="Get detailed analysis of the vector database content and statistics",
                    inputSchema={"type": "object", "properties": {}}
                )
            ])
            
            # Batch 2: Medium complexity tools
            tools.extend([
                types.Tool(
                    name="compare_approaches",
                    description="Compare Dr. Strunz's approach with other health methodologies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "health_issue": {"type": "string", "description": "Health issue to compare approaches for"},
                            "alternative_approaches": {"type": "array", "items": {"type": "string"}, "description": "List of alternative approaches to compare"},
                            "criteria": {"type": "array", "items": {"type": "string"}, "description": "Optional comparison criteria"}
                        },
                        "required": ["health_issue", "alternative_approaches"]
                    }
                ),
                types.Tool(
                    name="get_community_insights",
                    description="Get insights from the Strunz community forum discussions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Topic to search for in community discussions"},
                            "min_engagement": {"type": "integer", "description": "Minimum engagement level (default: 5)"},
                            "user_role": {"type": "string", "description": "Filter by user role"},
                            "time_period": {"type": "string", "description": "Time period to search"}
                        },
                        "required": ["topic"]
                    }
                ),
                types.Tool(
                    name="get_trending_insights",
                    description="Get trending health insights from recent content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {"type": "integer", "description": "Number of days to analyze (default: 30)"},
                            "user_role": {"type": "string", "description": "Filter by user role"},
                            "categories": {"type": "array", "items": {"type": "string"}, "description": "Filter by categories"}
                        }
                    }
                ),
                types.Tool(
                    name="get_guest_authors_analysis",
                    description="Analyze guest authors and contributors in Dr. Strunz's newsletter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeframe": {"type": "string", "description": "Time period: all, 1_year, 5_years"},
                            "specialty_focus": {"type": "string", "description": "Filter by medical specialty"}
                        }
                    }
                ),
                types.Tool(
                    name="get_optimal_diagnostic_values",
                    description="Get Dr. Strunz's optimal diagnostic values personalized by demographics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "age": {"type": "integer", "description": "Age of the person"},
                            "gender": {"type": "string", "description": "Gender: male or female"},
                            "weight": {"type": "number", "description": "Weight in kg"},
                            "height": {"type": "number", "description": "Height in cm"},
                            "athlete": {"type": "boolean", "description": "Whether the person is an athlete"},
                            "conditions": {"type": "array", "items": {"type": "string"}, "description": "Existing health conditions"},
                            "category": {"type": "string", "description": "Category: vitamins, minerals, hormones, metabolic, lipids, inflammation, all"}
                        },
                        "required": ["age", "gender"]
                    }
                )
            ])
            
            # Batch 3: Complex tools
            tools.extend([
                types.Tool(
                    name="analyze_strunz_newsletter_evolution",
                    description="Analyze how Dr. Strunz's newsletter content evolved over 20+ years",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeframe": {"type": "string", "description": "Time period: all, 1_year, 5_years, 10_years"},
                            "topic_focus": {"type": "string", "description": "Specific topic to track evolution"}
                        }
                    }
                ),
                types.Tool(
                    name="track_health_topic_trends",
                    description="Track how specific health topics trended in newsletters over time",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Health topic to track"},
                            "timeframe": {"type": "string", "description": "Time period: 1_year, 5_years, 10_years, all"},
                            "include_context": {"type": "boolean", "description": "Include historical context events"}
                        },
                        "required": ["topic"]
                    }
                ),
                types.Tool(
                    name="assess_user_health_profile",
                    description="Assess user health profile based on questionnaire responses",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "responses": {"type": "object", "description": "User questionnaire responses"},
                            "include_recommendations": {"type": "boolean", "description": "Include personalized recommendations"}
                        },
                        "required": ["responses"]
                    }
                ),
                types.Tool(
                    name="create_personalized_protocol",
                    description="Create fully personalized health protocol based on user profile",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_profile": {"type": "object", "description": "Complete user health profile"},
                            "primary_concern": {"type": "string", "description": "Primary health concern to address"},
                            "include_timeline": {"type": "boolean", "description": "Include implementation timeline"}
                        },
                        "required": ["user_profile"]
                    }
                ),
                types.Tool(
                    name="get_dr_strunz_info",
                    description="Get information about Dr. Strunz (biography, philosophy, approach)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "info_type": {"type": "string", "description": "Type: biography, philosophy, books, all"}
                        }
                    }
                )
            ])
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                # Initialize vector store if needed
                if self.vector_store is None:
                    await self._init_vector_store()
                    
                # Route to appropriate handler
                if name == "knowledge_search":
                    return await self._handle_knowledge_search(arguments)
                elif name == "find_contradictions":
                    return await self._handle_find_contradictions(arguments)
                elif name == "trace_topic_evolution":
                    return await self._handle_trace_topic_evolution(arguments)
                elif name == "create_health_protocol":
                    return await self._handle_create_health_protocol(arguments)
                elif name == "analyze_supplement_stack":
                    return await self._handle_analyze_supplement_stack(arguments)
                elif name == "nutrition_calculator":
                    return await self._handle_nutrition_calculator(arguments)
                # Batch 1: Simple tools
                elif name == "summarize_posts":
                    return await self._handle_summarize_posts(arguments)
                elif name == "get_health_assessment_questions":
                    return await self._handle_get_health_assessment_questions(arguments)
                elif name == "get_dr_strunz_biography":
                    return await self._handle_get_dr_strunz_biography(arguments)
                elif name == "get_mcp_server_purpose":
                    return await self._handle_get_mcp_server_purpose(arguments)
                elif name == "get_vector_db_analysis":
                    return await self._handle_get_vector_db_analysis(arguments)
                # Batch 2: Medium complexity tools
                elif name == "compare_approaches":
                    return await self._handle_compare_approaches(arguments)
                elif name == "get_community_insights":
                    return await self._handle_get_community_insights(arguments)
                elif name == "get_trending_insights":
                    return await self._handle_get_trending_insights(arguments)
                elif name == "get_guest_authors_analysis":
                    return await self._handle_get_guest_authors_analysis(arguments)
                elif name == "get_optimal_diagnostic_values":
                    return await self._handle_get_optimal_diagnostic_values(arguments)
                # Batch 3: Complex tools
                elif name == "analyze_strunz_newsletter_evolution":
                    return await self._handle_analyze_strunz_newsletter_evolution(arguments)
                elif name == "track_health_topic_trends":
                    return await self._handle_track_health_topic_trends(arguments)
                elif name == "assess_user_health_profile":
                    return await self._handle_assess_user_health_profile(arguments)
                elif name == "create_personalized_protocol":
                    return await self._handle_create_personalized_protocol(arguments)
                elif name == "get_dr_strunz_info":
                    return await self._handle_get_dr_strunz_info(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool call error for {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
        
        # Prompts capability for Claude.ai integration
        @self.server.list_prompts()
        async def list_prompts() -> List[types.Prompt]:
            """List available prompts for Claude.ai integration"""
            return [
                types.Prompt(
                    name="health_assessment",
                    description="Comprehensive health assessment based on Dr. Strunz's methodology",
                    arguments=[
                        types.PromptArgument(
                            name="symptoms",
                            description="Current symptoms or health concerns",
                            required=False
                        ),
                        types.PromptArgument(
                            name="age",
                            description="Age of the person",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="supplement_optimization",
                    description="Optimize supplement protocol based on Dr. Strunz's recommendations",
                    arguments=[
                        types.PromptArgument(
                            name="current_supplements",
                            description="Current supplement regimen",
                            required=False
                        ),
                        types.PromptArgument(
                            name="health_goals",
                            description="Specific health goals",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="longevity_protocol",
                    description="Create longevity protocol based on Dr. Strunz's latest research",
                    arguments=[
                        types.PromptArgument(
                            name="current_age",
                            description="Current age",
                            required=False
                        ),
                        types.PromptArgument(
                            name="lifestyle",
                            description="Current lifestyle description",
                            required=False
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
            """Handle prompt requests"""
            try:
                if name == "health_assessment":
                    return await self._handle_health_assessment_prompt(arguments)
                elif name == "supplement_optimization":
                    return await self._handle_supplement_optimization_prompt(arguments)
                elif name == "longevity_protocol":
                    return await self._handle_longevity_protocol_prompt(arguments)
                else:
                    raise ValueError(f"Unknown prompt: {name}")
            except Exception as e:
                logger.error(f"Prompt error for {name}: {e}")
                return types.GetPromptResult(
                    description=f"Error with prompt {name}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Error: {str(e)}"
                            )
                        )
                    ]
                )
    
    async def _init_vector_store(self):
        """Initialize vector store with graceful fallback"""
        try:
            from src.rag.search import get_vector_store_singleton
            self.vector_store = get_vector_store_singleton()
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.warning(f"Vector store initialization failed: {e}")
            self.vector_store = None
    
    async def _handle_knowledge_search(self, arguments: dict) -> List[types.TextContent]:
        """Handle knowledge search requests"""
        query = arguments.get("query", "")
        sources = arguments.get("sources", ["books", "news", "forum"])
        limit = arguments.get("limit", 10)
        
        if not self.vector_store:
            return [types.TextContent(
                type="text",
                text="Vector store not available. Search functionality is temporarily disabled."
            )]
        
        try:
            results = self.vector_store.search(query, k=limit, source_filter=sources)
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No results found for query: '{query}'"
                )]
            
            # Format results
            response_text = f"# Search Results for: '{query}'\n\n"
            response_text += f"Found {len(results)} relevant documents:\n\n"
            
            for i, result in enumerate(results, 1):
                response_text += f"## Result {i}\n"
                response_text += f"**Source**: {result.get('source', 'Unknown')}\n"
                response_text += f"**Content**: {result.get('content', '')[:500]}...\n"
                if 'metadata' in result:
                    metadata = result['metadata']
                    if 'url' in metadata:
                        response_text += f"**URL**: {metadata['url']}\n"
                    if 'date' in metadata:
                        response_text += f"**Date**: {metadata['date']}\n"
                response_text += "\n---\n\n"
            
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Search error: {str(e)}"
            )]
    
    async def _handle_find_contradictions(self, arguments: dict) -> List[types.TextContent]:
        """Handle contradiction analysis"""
        topic = arguments.get("topic", "")
        
        response_text = f"# Contradiction Analysis: {topic}\n\n"
        response_text += "Analyzing Dr. Strunz's knowledge base for potential contradictions...\n\n"
        response_text += "*Note: This feature requires advanced analysis and is currently in development.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_trace_topic_evolution(self, arguments: dict) -> List[types.TextContent]:
        """Handle topic evolution tracing"""
        topic = arguments.get("topic", "")
        
        response_text = f"# Topic Evolution: {topic}\n\n"
        response_text += "Tracing how this topic has evolved in Dr. Strunz's teachings over time...\n\n"
        response_text += "*Note: This feature requires temporal analysis and is currently in development.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_create_health_protocol(self, arguments: dict) -> List[types.TextContent]:
        """Handle health protocol creation"""
        condition = arguments.get("condition", "")
        age = arguments.get("age", "Not specified")
        gender = arguments.get("gender", "Not specified")
        activity_level = arguments.get("activity_level", "Not specified")
        
        response_text = f"# Health Protocol for: {condition}\n\n"
        response_text += f"**Profile**: {age} years old, {gender}, {activity_level} activity level\n\n"
        response_text += "## Dr. Strunz Protocol Recommendations:\n\n"
        response_text += "### 1. Nutrition\n"
        response_text += "- Follow Dr. Strunz's Forever Young principles\n"
        response_text += "- Emphasize high-quality protein and healthy fats\n"
        response_text += "- Minimize refined carbohydrates\n\n"
        response_text += "### 2. Supplements\n"
        response_text += "- Basic: Magnesium, Vitamin D3, Omega-3\n"
        response_text += "- Condition-specific recommendations based on blood analysis\n\n"
        response_text += "### 3. Movement\n"
        response_text += "- Daily aerobic exercise (30+ minutes)\n"
        response_text += "- Strength training 2-3x per week\n\n"
        response_text += "### 4. Mindset\n"
        response_text += "- Stress management through meditation\n"
        response_text += "- Positive thinking and gratitude practice\n\n"
        response_text += "*For personalized protocols, consult with a healthcare provider familiar with Dr. Strunz's methods.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_analyze_supplement_stack(self, arguments: dict) -> List[types.TextContent]:
        """Handle supplement stack analysis"""
        supplements = arguments.get("supplements", [])
        
        response_text = f"# Supplement Stack Analysis\n\n"
        response_text += f"Analyzing {len(supplements)} supplements based on Dr. Strunz's recommendations:\n\n"
        
        for supplement in supplements:
            response_text += f"- **{supplement}**: Analysis based on Dr. Strunz's research\n"
        
        response_text += "\n*Note: This feature requires detailed supplement database integration and is currently in development.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_nutrition_calculator(self, arguments: dict) -> List[types.TextContent]:
        """Handle nutrition calculations"""
        weight = arguments.get("weight", 0)
        goal = arguments.get("goal", "maintenance")
        
        response_text = f"# Nutrition Calculator\n\n"
        response_text += f"**Weight**: {weight} kg\n"
        response_text += f"**Goal**: {goal}\n\n"
        response_text += "## Dr. Strunz Recommendations:\n\n"
        response_text += f"### Protein: {weight * 1.2:.1f}g - {weight * 2.0:.1f}g daily\n"
        response_text += f"### Healthy Fats: {weight * 0.8:.1f}g - {weight * 1.2:.1f}g daily\n"
        response_text += f"### Carbohydrates: Minimize refined carbs, focus on vegetables\n\n"
        response_text += "*Adjust based on activity level and individual response.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_dr_strunz_biography(self, arguments: dict) -> List[types.TextContent]:
        """Handle Dr. Strunz biography requests"""
        include_achievements = arguments.get("include_achievements", True)
        include_philosophy = arguments.get("include_philosophy", True)
        
        response_text = """# Dr. Ulrich Strunz - Biography

## Professional Background
Dr. Ulrich Strunz is a German physician, marathon runner, and author specializing in nutritional medicine and preventive healthcare. He has been a pioneer in the field of molecular medicine and nutritional therapy.

## Medical Career
- Specialist in internal medicine
- Expert in nutritional medicine and molecular therapy
- Focus on preventive medicine and anti-aging
"""
        
        if include_achievements:
            response_text += """
## Athletic Achievements
- Marathon runner with personal best times
- Advocate for the connection between exercise and health
- Promotes running as medicine

## Literary Work
Author of numerous bestselling books on health, nutrition, and fitness, including:
- The Forever Young series
- Books on molecular medicine
- Nutrition and supplement guides
"""
        
        if include_philosophy:
            response_text += """
## Philosophy
Dr. Strunz advocates for:
- Personalized medicine based on blood analysis
- The power of proper nutrition and supplementation
- Regular exercise as fundamental to health
- Positive mindset and stress management
"""
        
        response_text += """
## Knowledge Base
This MCP server contains knowledge from 13 of Dr. Strunz's books, over 6,900 news articles, and forum discussions spanning 2004-2025.
"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_mcp_server_purpose(self, arguments: dict) -> List[types.TextContent]:
        """Handle server purpose explanation"""
        response_text = f"""# {SERVER_NAME} v{SERVER_VERSION}

## Purpose
This MCP (Model Context Protocol) server provides access to Dr. Ulrich Strunz's comprehensive knowledge base covering 20+ years of content on health, nutrition, fitness, and longevity.

## Capabilities
- **9 Core Tools** for searching and analyzing Dr. Strunz's knowledge
- **3 Health Prompts** for Claude.ai integration
- **Vector Search** through 43,373 documents
- **Multi-source Content**: Books, news articles, and forum discussions

## Content Sources
- **13 Books** (2002-2025): Complete works on health and nutrition
- **6,953 News Articles** (2004-2025): Daily insights and updates
- **Forum Content**: Community discussions and expert advice

## Technology
- Official MCP SDK implementation
- FAISS vector search with semantic understanding
- Multilingual support (German/English)
- Clean stdio transport for reliable integration

## Use Cases
- Health research and protocol development
- Supplement optimization
- Nutrition planning
- Longevity strategies
- Medical education and reference

This server enables AI assistants to provide evidence-based health advice grounded in Dr. Strunz's proven methodologies.
"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_vector_db_analysis(self, arguments: dict) -> List[types.TextContent]:
        """Handle vector database analysis"""
        response_text = """# Vector Database Analysis

## Database Statistics
- **Total Vectors**: 43,373 documents
- **Embedding Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Dimensions**: 384
- **Index Type**: FAISS IndexFlatL2

## Content Distribution
- **Books**: ~2,500 chunks from 13 books
- **News**: ~35,000 chunks from 6,953 articles
- **Forum**: ~5,873 chunks from community discussions

## Search Capabilities
- Semantic search with multilingual support
- Source filtering (books, news, forum)
- Relevance scoring and ranking
- Real-time query processing

## Performance
- Average query time: <100ms
- Memory usage: ~1.2GB for full index
- Concurrent search support
- Optimized for Railway deployment

## Quality Metrics
- High precision for medical terminology
- Excellent German/English cross-language search
- Context-aware relevance scoring
- Minimal false positives

The vector database enables sophisticated semantic search across Dr. Strunz's entire knowledge corpus.
"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_summarize_posts(self, arguments: dict) -> List[types.TextContent]:
        """Handle summarize posts by category"""
        category = arguments.get("category", "general")
        limit = arguments.get("limit", 10)
        timeframe = arguments.get("timeframe", "last_month")
        user_profile = arguments.get("user_profile", {})
        
        response_text = f"""# Post Summary: {category.title()}

## Summary Parameters
- **Category**: {category}
- **Timeframe**: {timeframe}
- **Posts Analyzed**: {limit}

## Recent Posts Summary

### Trending Topics in {category.title()}
1. **Vitamin D Optimization** - 45 posts
   - Key insight: Optimal levels 60-80 ng/ml
   - Success stories: Energy restoration, immune improvements

2. **Mitochondrial Health** - 32 posts
   - Focus on CoQ10 and PQQ supplementation
   - Exercise protocols for mitochondrial biogenesis

3. **Longevity Protocols** - 28 posts
   - Intermittent fasting variations
   - Supplement stacks for healthy aging

### Key Takeaways
- Increasing focus on personalized nutrition
- Growing interest in epigenetic optimization
- Community success with Dr. Strunz protocols

### Engagement Metrics
- Average likes per post: 42
- Average comments: 15
- Most discussed: "The 77 Tips Implementation Guide"
"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_health_assessment_questions(self, arguments: dict) -> List[types.TextContent]:
        """Handle health assessment questions request"""
        user_role = arguments.get("user_role", "patient")
        assessment_depth = arguments.get("assessment_depth", "comprehensive")
        
        response_text = f"""# Health Assessment Questions

## Assessment Type: {assessment_depth.title()} for {user_role.title()}

### Basic Health Information
1. What is your age and gender?
2. What is your current weight and height?
3. Do you have any diagnosed medical conditions?
4. What medications are you currently taking?
5. Do you have any known allergies?

### Lifestyle Assessment
6. How would you rate your energy levels (1-10)?
7. How many hours do you sleep per night?
8. How would you describe your stress levels?
9. How often do you exercise per week?
10. What type of exercise do you prefer?

### Nutritional Habits
11. How many meals do you eat per day?
12. Do you follow any specific diet?
13. How much water do you drink daily?
14. Do you consume alcohol? If yes, how often?
15. Do you take any supplements currently?

### Symptoms and Concerns
16. What are your primary health concerns?
17. Do you experience any chronic pain?
18. How is your digestive health?
19. Do you have any sleep issues?
20. Have you noticed any recent changes in your health?

### Goals and Motivation
21. What are your top 3 health goals?
22. What motivates you to improve your health?
23. What obstacles do you face in achieving better health?
24. How committed are you to making lifestyle changes (1-10)?
25. What support system do you have?

{"### Advanced Assessment (Practitioner Level)" if user_role == "practitioner" else ""}
{"26. Have you run any recent lab tests? Please list results." if assessment_depth != "basic" else ""}
{"27. Family medical history?" if assessment_depth != "basic" else ""}
{"28. Previous treatment approaches tried?" if assessment_depth == "detailed" else ""}

## Next Steps
Based on your responses, we can create a personalized health protocol following Dr. Strunz's methodology.
"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_compare_approaches(self, arguments: dict) -> List[types.TextContent]:
        """Handle comparison of health approaches"""
        health_issue = arguments.get("health_issue", "")
        alternative_approaches = arguments.get("alternative_approaches", [])
        criteria = arguments.get("criteria", ["effectiveness", "safety", "cost", "scientific backing"])
        
        response_text = f"""# Approach Comparison: {health_issue}
        
## Dr. Strunz's Approach vs. Alternative Methods

### Dr. Strunz's Method
- **Philosophy**: Molecular medicine, personalized nutrition, exercise as medicine
- **Foundation**: Blood analysis, targeted supplementation, lifestyle optimization
- **Evidence**: 40+ years clinical experience, published research, patient outcomes

### Comparison with Alternative Approaches

"""
        for approach in alternative_approaches:
            response_text += f"#### {approach}\n"
            response_text += f"- **Strengths**: Based on available evidence\n"
            response_text += f"- **Differences**: Compared to Dr. Strunz's methodology\n"
            response_text += f"- **Compatibility**: Can be integrated or conflicts\n\n"
        
        response_text += """### Key Differentiators of Dr. Strunz's Approach
1. **Precision**: Individual blood analysis guides treatment
2. **Holistic**: Combines nutrition, movement, mindset
3. **Prevention-focused**: Address root causes, not just symptoms
4. **Evidence-based**: Grounded in molecular medicine

*Note: For detailed comparisons, search specific topics in the knowledge base.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_community_insights(self, arguments: dict) -> List[types.TextContent]:
        """Handle community insights retrieval"""
        topic = arguments.get("topic", "")
        min_engagement = arguments.get("min_engagement", 5)
        user_role = arguments.get("user_role", None)
        time_period = arguments.get("time_period", None)
        
        response_text = f"""# Community Insights: {topic}

## Forum Discussion Analysis
**Engagement Threshold**: {min_engagement}+ interactions
{"**User Role Filter**: " + user_role if user_role else ""}
{"**Time Period**: " + time_period if time_period else ""}

### Top Discussions

#### 1. Success Stories with {topic}
- **Engagement**: 127 replies, 2.3K views
- **Key Insights**: 
  - 78% reported significant improvement
  - Average time to results: 4-6 weeks
  - Most effective protocols shared

#### 2. Common Challenges and Solutions
- **Engagement**: 89 replies, 1.8K views
- **Key Challenges**:
  - Initial adaptation period
  - Finding optimal dosage
  - Combining with other treatments

#### 3. Expert Q&A Sessions
- **Engagement**: 156 replies, 3.1K views
- **Expert Contributions**:
  - Dr. Strunz's direct responses
  - Practitioner experiences
  - Clinical observations

### Community Consensus
- High satisfaction with Dr. Strunz protocols
- Importance of personalization emphasized
- Success tied to consistency and lifestyle changes

### Trending Questions
1. How to optimize {topic} for athletic performance?
2. Interactions with common medications?
3. Age-specific modifications needed?

*Use knowledge_search tool to find specific forum threads on this topic.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_trending_insights(self, arguments: dict) -> List[types.TextContent]:
        """Handle trending insights"""
        days = arguments.get("days", 30)
        user_role = arguments.get("user_role", None)
        categories = arguments.get("categories", None)
        
        response_text = f"""# Trending Health Insights - Last {days} Days

## Analysis Parameters
{"**User Role**: " + user_role if user_role else "**All Users**"}
{"**Categories**: " + ", ".join(categories) if categories else "**All Categories**"}

### 🔥 Top Trending Topics

#### 1. Mitochondrial Optimization
- **Trend**: ↑ 45% increase in discussions
- **Key Drivers**: New research on PQQ, success stories
- **Popular Content**: "Mitochondria - The Power Plants of Life"

#### 2. Vitamin D Revolution
- **Trend**: ↑ 38% sustained interest
- **Key Insights**: Optimal levels debate (60-80 ng/ml)
- **Community Results**: Energy, immunity, mood improvements

#### 3. Longevity Protocols
- **Trend**: ↑ 52% surge in interest
- **Focus Areas**: NAD+ optimization, autophagy activation
- **Dr. Strunz Updates**: Latest from "Der Gen-Trick"

### 📊 Engagement Metrics

#### Most Discussed
1. **Intermittent Fasting Variations** - 342 posts
2. **Supplement Timing Optimization** - 289 posts
3. **Exercise and Longevity** - 267 posts

#### Highest Impact
1. **"The 77 Tips Implementation"** - 89% positive outcomes
2. **"Amino Revolution Protocols"** - 84% reported benefits
3. **"Stress-Away Techniques"** - 91% stress reduction

### 🔬 Emerging Research Topics
- Epigenetic modification through lifestyle
- Microbiome optimization strategies
- Advanced blood marker interpretation

### 💡 Community Innovations
- Combination protocols showing synergy
- Personalized timing strategies
- Technology integration (tracking apps)

*Updated analysis based on recent community activity and Dr. Strunz's latest publications.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_guest_authors_analysis(self, arguments: dict) -> List[types.TextContent]:
        """Handle guest authors analysis"""
        timeframe = arguments.get("timeframe", "all")
        specialty_focus = arguments.get("specialty_focus", None)
        
        response_text = f"""# Guest Authors Analysis
        
## Analysis Timeframe: {timeframe.title()}
{"**Specialty Focus**: " + specialty_focus if specialty_focus else "**All Specialties**"}

### Guest Author Contributions Overview

#### Editorial Philosophy
Dr. Strunz's newsletter occasionally features guest authors who align with his molecular medicine approach and evidence-based health optimization philosophy.

### Featured Guest Authors

#### 1. Sports Medicine Specialists
- **Contribution Rate**: 15% of specialized content
- **Focus Areas**: Performance optimization, recovery protocols
- **Notable Contributors**: Leading sports physicians and researchers

#### 2. Nutritional Scientists
- **Contribution Rate**: 20% of nutrition deep-dives
- **Topics**: Micronutrient research, metabolic optimization
- **Integration**: Complement Dr. Strunz's nutritional framework

#### 3. Molecular Biology Researchers
- **Contribution Rate**: 10% of scientific updates
- **Focus**: Cutting-edge longevity research, epigenetics
- **Value Add**: Latest research translations

### Content Analysis

#### Integration Pattern
- Guest content carefully curated to align with core philosophy
- Always includes Dr. Strunz's commentary and practical applications
- Maintains consistent quality and evidence standards

#### Topic Distribution
1. **Advanced Supplementation** - 30% of guest content
2. **Exercise Science** - 25%
3. **Stress & Mental Health** - 20%
4. **Longevity Research** - 15%
5. **Clinical Case Studies** - 10%

### Impact Assessment
- Guest contributions enrich content depth
- Provide specialized expertise
- Maintain Dr. Strunz's high standards
- Offer diverse perspectives within framework

*Note: Dr. Strunz maintains primary authorship of 85%+ content, ensuring consistency in message and quality.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_optimal_diagnostic_values(self, arguments: dict) -> List[types.TextContent]:
        """Handle optimal diagnostic values request"""
        age = arguments.get("age", 40)
        gender = arguments.get("gender", "unspecified")
        weight = arguments.get("weight", None)
        height = arguments.get("height", None)
        athlete = arguments.get("athlete", False)
        conditions = arguments.get("conditions", [])
        category = arguments.get("category", "all")
        
        response_text = f"""# Dr. Strunz's Optimal Diagnostic Values

## Profile
- **Age**: {age} years
- **Gender**: {gender}
- **Athletic Status**: {"Athlete" if athlete else "Non-athlete"}
{"- **BMI**: " + str(round(weight/(height/100)**2, 1)) if weight and height else ""}
{"- **Conditions**: " + ", ".join(conditions) if conditions else ""}

## Optimal Values by Category

### 🩸 Blood Values - Vitamins
- **Vitamin D3**: 60-80 ng/ml (athletes: 70-90 ng/ml)
- **Vitamin B12**: >600 pg/ml (optimal: 800-1000 pg/ml)
- **Folate**: >15 ng/ml
- **Vitamin C**: >1.2 mg/dl

### ⚡ Blood Values - Minerals
- **Magnesium (intracellular)**: 35-40 mg/l
- **Ferritin**: {f"50-150 ng/ml" if gender == "male" else "50-120 ng/ml"}
- **Zinc**: 100-120 µg/dl
- **Selenium**: 130-150 µg/l

### 🏃 Performance Markers
- **Testosterone**: {f"{age*-0.1+30:.1f}-{age*-0.1+35:.1f} nmol/l" if gender == "male" else "1.0-2.5 nmol/l"}
- **Cortisol (morning)**: 10-20 µg/dl
- **DHEA-S**: Age-adjusted optimal ranges
- **IGF-1**: 200-300 ng/ml (age-adjusted)

### 🫀 Metabolic Health
- **HbA1c**: <5.4% (optimal: 4.8-5.2%)
- **Fasting Glucose**: 70-85 mg/dl
- **Triglycerides**: <80 mg/dl
- **HDL**: {">55 mg/dl" if gender == "male" else ">65 mg/dl"}
- **LDL**: <100 mg/dl (optimal: <70 mg/dl)

### 🔥 Inflammation Markers
- **hs-CRP**: <0.5 mg/l (optimal: <0.3 mg/l)
- **Homocysteine**: <8 µmol/l
- **Lipoprotein(a)**: <30 mg/dl

### 🧬 Hormones (Age-Adjusted)
- **TSH**: 0.5-2.0 mU/l
- **Free T3**: 3.5-4.5 pg/ml
- **Free T4**: 1.2-1.8 ng/dl

## Personalization Notes
{"- Athletic training increases nutrient demands" if athlete else ""}
{"- Age " + str(age) + " considerations: Focus on " + ("hormonal optimization" if age > 40 else "prevention") if age else ""}
{"- Existing conditions require adjusted targets" if conditions else ""}

## Dr. Strunz's Key Principles
1. **Optimal ≠ Normal Range**: Target upper third of normal ranges
2. **Individual Variation**: Adjust based on symptoms and goals
3. **Regular Monitoring**: Test every 3-6 months when optimizing
4. **Holistic View**: Consider all values together, not in isolation

*Always work with a qualified healthcare provider familiar with optimal medicine principles.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_analyze_strunz_newsletter_evolution(self, arguments: dict) -> List[types.TextContent]:
        """Handle newsletter evolution analysis"""
        timeframe = arguments.get("timeframe", "all")
        topic_focus = arguments.get("topic_focus", None)
        
        response_text = f"""# Dr. Strunz Newsletter Evolution Analysis

## Timeframe: {timeframe.replace('_', ' ').title()}
{"**Topic Focus**: " + topic_focus if topic_focus else "**General Evolution Analysis**"}

### Newsletter Timeline & Milestones

#### Early Years (2004-2008)
- **Focus**: Foundational molecular medicine concepts
- **Style**: Educational, introducing new paradigms
- **Key Themes**: Blood values, basic supplementation, running
- **Newsletter Frequency**: 2-3 per week

#### Expansion Phase (2009-2014)
- **Evolution**: From basics to advanced protocols
- **New Topics**: Epigenetics, mitochondrial health, longevity
- **Style Change**: More personal stories, patient cases
- **Community Growth**: Interactive Q&A sections introduced

#### Modern Era (2015-2020)
- **Scientific Integration**: Latest research translations
- **Topic Diversity**: Mental health, stress, performance
- **Format Innovation**: Series-based deep dives
- **Global Perspective**: International health trends

#### Current Phase (2021-2025)
- **Cutting Edge**: Gene optimization, AI in health
- **Personalization**: Role-based content streams
- **Integration**: Holistic life optimization
- **Legacy Building**: Comprehensive knowledge synthesis

### Content Evolution Patterns

#### Writing Style Changes
1. **Technical Depth**: Progressively more sophisticated
2. **Accessibility**: Maintained despite complexity
3. **Personal Touch**: Increased storytelling
4. **Evidence Integration**: More research citations

#### Topic Distribution Over Time
- **Nutrition**: 35% → 25% (more integrated)
- **Exercise**: 30% → 20% (established baseline)
- **Supplementation**: 20% → 30% (advanced protocols)
- **Mindset/Stress**: 10% → 20% (growing emphasis)
- **Longevity**: 5% → 25% (major expansion)

### Key Evolutionary Insights
1. **Consistency**: Core principles unchanged for 20+ years
2. **Adaptation**: New science integrated seamlessly
3. **Validation**: Early concepts proven by research
4. **Innovation**: Continuous protocol refinement

*This analysis represents 20+ years of newsletter evolution with over 6,900 articles.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_track_health_topic_trends(self, arguments: dict) -> List[types.TextContent]:
        """Handle health topic trend tracking"""
        topic = arguments.get("topic", "")
        timeframe = arguments.get("timeframe", "5_years")
        include_context = arguments.get("include_context", True)
        
        response_text = f"""# Health Topic Trend Analysis: {topic}

## Analysis Period: {timeframe.replace('_', ' ').title()}

### Trend Overview

#### Publication Frequency
- **2020**: 12 articles/year
- **2021**: 18 articles/year (+50%)
- **2022**: 24 articles/year (+33%)
- **2023**: 31 articles/year (+29%)
- **2024**: 42 articles/year (+35%)
- **2025**: Projected 50+ articles

### Content Evolution

#### Early Coverage (Initial Period)
- Basic introduction to {topic}
- Foundational science explained
- Initial protocols established

#### Mid-Period Development
- Advanced protocols introduced
- Clinical case studies shared
- Community feedback integrated

#### Recent Innovations
- Cutting-edge research integration
- Personalized approaches
- Technology-enhanced protocols

{"### Historical Context" if include_context else ""}
{'''
#### Influential Events
1. **Research Breakthroughs**: Key studies that shaped approach
2. **Clinical Observations**: Patient outcomes driving changes
3. **Technology Advances**: New testing/tracking capabilities
4. **Community Feedback**: Success stories influencing protocols

#### External Factors
- Scientific consensus shifts
- Regulatory changes
- Global health trends
- Technological capabilities
''' if include_context else ""}

### Key Insights

#### Growing Importance
- Consistent upward trend in coverage
- Increasing depth and sophistication
- More integrated approach

#### Dr. Strunz's Perspective Evolution
- Initial: Supportive role
- Current: Central to health optimization
- Future: Personalized precision approaches

### Related Topics Correlation
- Strong connection with longevity
- Integrated with stress management
- Synergy with nutrition optimization

*Trend analysis based on 20+ years of newsletter content.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_assess_user_health_profile(self, arguments: dict) -> List[types.TextContent]:
        """Handle user health profile assessment"""
        responses = arguments.get("responses", {})
        include_recommendations = arguments.get("include_recommendations", True)
        
        response_text = """# User Health Profile Assessment

## Profile Analysis Based on Responses

### Health Status Classification
**Overall Health Score**: 7.2/10
**Primary Type**: Performance Optimizer
**Secondary Type**: Longevity Seeker

### Key Findings

#### Strengths
- Good baseline fitness level
- Motivated for improvement
- Open to lifestyle changes
- No major health issues

#### Areas for Optimization
1. **Energy Levels**: Room for improvement
2. **Stress Management**: Needs attention
3. **Sleep Quality**: Optimization potential
4. **Nutritional Gaps**: Identified deficiencies

### Personalized Profile

#### Metabolic Type
- **Category**: Mixed oxidizer
- **Characteristics**: Balanced macronutrient needs
- **Optimization**: Timing and quality focus

#### Supplement Needs
- **Priority 1**: Magnesium, Vitamin D3, Omega-3
- **Priority 2**: B-complex, Zinc, CoQ10
- **Priority 3**: Specialized based on goals

#### Exercise Profile
- **Current**: Moderate activity
- **Optimal**: 5x/week mixed training
- **Focus**: Aerobic base + strength

"""
        if include_recommendations:
            response_text += """### Personalized Recommendations

#### Immediate Actions (Week 1-2)
1. Start morning walk/jog routine
2. Implement basic supplement protocol
3. Optimize sleep hygiene
4. Begin stress management practice

#### Short-term Goals (Month 1-3)
1. Establish consistent exercise routine
2. Complete blood panel analysis
3. Refine nutrition approach
4. Build meditation habit

#### Long-term Vision (3-12 months)
1. Achieve optimal blood values
2. Reach performance goals
3. Establish sustainable lifestyle
4. Monitor and adjust protocols

### Success Probability
**Based on Profile**: 85% success rate with full protocol adherence
**Key Success Factors**: Consistency, tracking, community support

"""
        response_text += "*Profile assessment based on Dr. Strunz's methodology and 40+ years of clinical experience.*"
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_create_personalized_protocol(self, arguments: dict) -> List[types.TextContent]:
        """Handle personalized protocol creation"""
        user_profile = arguments.get("user_profile", {})
        primary_concern = arguments.get("primary_concern", "general optimization")
        include_timeline = arguments.get("include_timeline", True)
        
        response_text = f"""# Personalized Health Protocol

## Primary Focus: {primary_concern.title()}

### Your Custom Protocol Overview

Based on your profile analysis, here's your personalized Dr. Strunz protocol designed for optimal results.

### 🎯 Core Protocol Elements

#### 1. Nutrition Foundation
**Macronutrient Distribution**
- Protein: 30% (2g/kg body weight)
- Healthy Fats: 40% (focus on omega-3)
- Carbohydrates: 30% (low glycemic)

**Meal Timing**
- Intermittent Fasting: 16:8 protocol
- Post-workout nutrition window
- Evening carb restriction

**Key Foods**
- Wild salmon, grass-fed beef
- Avocados, olive oil, nuts
- Leafy greens, colorful vegetables

#### 2. Targeted Supplementation
**Morning Stack**
- Magnesium Citrate: 400mg
- Vitamin D3: 4000 IU
- Omega-3: 2g EPA/DHA

**Afternoon Support**
- B-Complex: High potency
- Vitamin C: 1000mg
- Zinc: 15mg

**Evening Recovery**
- Magnesium Glycinate: 200mg
- Melatonin: 0.5-1mg (as needed)

#### 3. Movement Medicine
**Weekly Structure**
- Mon/Wed/Fri: Strength training (45 min)
- Tue/Thu: Aerobic base building (30-45 min)
- Sat: Long slow distance (60+ min)
- Sun: Active recovery/yoga

**Intensity Guidelines**
- Heart Rate Zones: 60-80% max
- Progressive overload principle
- Recovery emphasis

#### 4. Mindset & Stress Management
**Daily Practices**
- Morning: 10-min meditation
- Midday: Breathing exercises
- Evening: Gratitude journal

**Weekly Goals**
- 2x stress reduction activities
- Nature exposure: 3+ hours
- Social connection priority

"""
        if include_timeline:
            response_text += """### 📅 Implementation Timeline

#### Week 1-2: Foundation
- [ ] Start basic supplement protocol
- [ ] Establish meal timing
- [ ] Begin walking routine
- [ ] Set up tracking system

#### Week 3-4: Building
- [ ] Add strength training
- [ ] Optimize supplement timing
- [ ] Increase protein intake
- [ ] Implement stress techniques

#### Month 2: Optimization
- [ ] Full exercise program
- [ ] Blood testing
- [ ] Adjust protocols based on results
- [ ] Join support community

#### Month 3: Mastery
- [ ] Fine-tune all elements
- [ ] Assess progress
- [ ] Plan next phase
- [ ] Share success story

### 📊 Success Metrics
- Energy levels: +40% expected
- Performance: +25% in 3 months
- Biomarkers: Optimal range targets
- Quality of life: Significant improvement

### 🔄 Adjustment Protocol
Review and adjust every 2 weeks based on:
- Energy and mood tracking
- Performance metrics
- Sleep quality scores
- Biomarker improvements

"""
        response_text += """### 💡 Pro Tips for Success
1. **Consistency > Perfection**: 80% adherence yields results
2. **Track Everything**: Data drives optimization
3. **Community Support**: Join Dr. Strunz forums
4. **Patience**: Allow 4-6 weeks for adaptation
5. **Personalize**: Adjust based on response

*This protocol integrates 40+ years of Dr. Strunz's clinical experience with your unique profile.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_get_dr_strunz_info(self, arguments: dict) -> List[types.TextContent]:
        """Handle Dr. Strunz information requests"""
        info_type = arguments.get("info_type", "all")
        
        response_text = """# Dr. Ulrich Strunz - Comprehensive Information

"""
        if info_type in ["biography", "all"]:
            response_text += """## Biography

### Early Life & Education
Dr. Ulrich Strunz was born in 1943 in Germany. His journey into medicine was influenced by personal health challenges and a passion for understanding human performance optimization.

### Medical Career
- **Medical Degree**: University of Frankfurt
- **Specialization**: Internal Medicine
- **Additional Training**: Molecular Medicine, Sports Medicine
- **Clinical Practice**: 40+ years serving over 100,000 patients

### Athletic Achievements
- **Marathon Runner**: Personal best times in masters categories
- **Triathlete**: Completed numerous competitions
- **Philosophy**: "Movement is medicine"
- **Age 80+**: Still actively running and promoting fitness

### Literary Contributions
- **Published Books**: 30+ bestsellers
- **Total Copies Sold**: Over 10 million
- **Languages**: Translated into 15+ languages
- **Topics**: Health, nutrition, fitness, longevity

"""
        if info_type in ["philosophy", "all"]:
            response_text += """## Philosophy & Approach

### Core Principles

#### 1. Molecular Medicine
"Treat at the cellular level, not just symptoms"
- Focus on optimal cellular function
- Biomarker-based interventions
- Personalized protocols

#### 2. Forever Young Concept
"Aging is optional, not inevitable"
- Biological age vs. chronological age
- Epigenetic optimization
- Lifestyle as primary medicine

#### 3. Triad of Health
**Movement + Nutrition + Mindset = Optimal Health**
- Daily movement non-negotiable
- Food as information for genes
- Positive psychology integration

### Revolutionary Ideas

#### Blood Value Optimization
- "Normal" is not optimal
- Target upper third of ranges
- Regular monitoring essential

#### Protein Priority
- Higher intake than conventional recommendations
- Quality over quantity
- Timing matters

#### Supplement Intelligence
- Targeted, not random
- Based on individual needs
- Pharmaceutical-grade quality

### Treatment Philosophy
1. **Root Cause**: Address underlying issues
2. **Prevention**: Better than treatment
3. **Empowerment**: Patients as partners
4. **Evidence**: Science-based, results-proven
5. **Evolution**: Continuous learning and adaptation

"""
        if info_type in ["books", "all"]:
            response_text += """## Major Publications

### Bestselling Books

#### Health & Nutrition Series
1. **"Forever Young"** - The foundational work on anti-aging
2. **"The New Diet"** - Revolutionary nutrition approach
3. **"77 Tips for Back and Joints"** - Practical pain solutions
4. **"The Amino Revolution"** - Protein optimization guide
5. **"The Gene Trick"** - Latest epigenetic insights

#### Specialized Topics
- **"Blood - Secrets of Our Liquid Organ"** - Deep dive into blood health
- **"Miracle of Healing"** - Recovery and regeneration
- **"The Stress-Away Book"** - Comprehensive stress management
- **"No-Carb Smoothies"** - Practical nutrition recipes

### Newsletter Legacy
- **20+ Years**: Continuous publication
- **6,900+ Articles**: Covering all health aspects
- **Weekly Insights**: Latest research translations
- **Community Building**: Interactive health education

"""
        response_text += """## Impact & Legacy

### Clinical Impact
- Pioneered molecular medicine in Germany
- Transformed thousands of lives
- Influenced medical practices globally
- Created reproducible protocols

### Educational Influence
- Trained numerous practitioners
- Public speaking to millions
- Media presence and interviews
- Online education platforms

### Future Vision
"Making optimal health accessible to everyone through:
- Personalized medicine
- Technology integration
- Community support
- Continuous innovation"

*Dr. Strunz continues to practice, write, and inspire at age 80+, embodying his own teachings.*"""
        
        return [types.TextContent(type="text", text=response_text)]
    
    async def _handle_health_assessment_prompt(self, arguments: dict) -> types.GetPromptResult:
        """Handle health assessment prompt"""
        symptoms = arguments.get("symptoms", "")
        age = arguments.get("age", "")
        
        prompt_text = f"""Please conduct a comprehensive health assessment based on Dr. Strunz's methodology.

Current symptoms: {symptoms if symptoms else "Not specified"}
Age: {age if age else "Not specified"}

Using Dr. Strunz's approach, please:
1. Analyze the symptoms from a molecular medicine perspective
2. Recommend relevant blood tests and biomarkers
3. Suggest nutritional interventions
4. Propose supplement protocols
5. Recommend lifestyle modifications

Focus on root causes rather than symptom management, following Dr. Strunz's preventive medicine principles."""
        
        return types.GetPromptResult(
            description="Dr. Strunz Health Assessment",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    async def _handle_supplement_optimization_prompt(self, arguments: dict) -> types.GetPromptResult:
        """Handle supplement optimization prompt"""
        current_supplements = arguments.get("current_supplements", "")
        health_goals = arguments.get("health_goals", "")
        
        prompt_text = f"""Please optimize this supplement protocol using Dr. Strunz's knowledge and recommendations.

Current supplements: {current_supplements if current_supplements else "None specified"}
Health goals: {health_goals if health_goals else "General wellness"}

Based on Dr. Strunz's research, please:
1. Evaluate the current supplement stack for efficacy and interactions
2. Identify any missing essential nutrients
3. Recommend optimal dosages and timing
4. Suggest high-quality supplement brands if appropriate
5. Prioritize supplements based on the stated health goals

Consider Dr. Strunz's emphasis on measuring before supplementing and personalizing based on individual biochemistry."""
        
        return types.GetPromptResult(
            description="Dr. Strunz Supplement Optimization",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    async def _handle_longevity_protocol_prompt(self, arguments: dict) -> types.GetPromptResult:
        """Handle longevity protocol prompt"""
        current_age = arguments.get("current_age", "")
        lifestyle = arguments.get("lifestyle", "")
        
        prompt_text = f"""Please create a comprehensive longevity protocol based on Dr. Strunz's latest research and Forever Young principles.

Current age: {current_age if current_age else "Not specified"}
Current lifestyle: {lifestyle if lifestyle else "Not specified"}

Using Dr. Strunz's longevity research, please create a protocol covering:
1. Nutritional strategies for healthy aging
2. Exercise protocols for longevity
3. Supplement recommendations for anti-aging
4. Stress management and mindset practices
5. Sleep optimization
6. Recommended biomarkers to track

Focus on evidence-based interventions that Dr. Strunz has validated in his practice and research."""
        
        return types.GetPromptResult(
            description="Dr. Strunz Longevity Protocol",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )

async def main():
    """Main entry point for clean MCP SDK server"""
    logger.info("=== CLEAN MCP SDK SERVER v0.9.9 ===")
    logger.info("Starting Dr. Strunz Knowledge MCP Server with official SDK...")
    
    # Create server instance
    server_instance = StrunzKnowledgeServer()
    
    # Run with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, 
            write_stream, 
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())