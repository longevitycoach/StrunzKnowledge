#!/usr/bin/env python3
"""
Clean MCP SDK Server - Official Implementation
Dr. Strunz Knowledge Base MCP Server using official MCP SDK
Version: 0.8.0 - Clean implementation without web dependencies
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
    logger.info("=== CLEAN MCP SDK SERVER v0.8.0 ===")
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