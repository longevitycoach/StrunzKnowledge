#!/usr/bin/env python3
"""
Dr. Strunz Knowledge MCP Server using Official MCP Python SDK

This implementation uses the official MCP SDK instead of FastMCP to ensure
full compatibility with Claude.ai and Claude Desktop, especially for prompts.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import MCP SDK
from mcp import MCPServer, MCPConnectionInterface
from mcp.types import (
    ServerCapabilities,
    ServerInfo,
    Tool,
    ToolCall,
    ToolCallContent,
    ToolListResult,
    PromptListResult,
    Prompt,
    PromptArgument,
    PromptGetResult,
    InitializeResult,
    CallToolResult,
    ListPromptsResult,
    GetPromptResult,
    ListToolsResult,
    Message,
    UserMessage,
    AssistantMessage,
    TextContent,
    ImageContent,
    EmbeddedContent
)

# Import our tools
from src.mcp.enhanced_server import tool_registry
from src.rag.search import get_vector_store_singleton, KnowledgeSearcher


class StrunzMCPServer(MCPServer):
    """Official MCP SDK implementation of Dr. Strunz Knowledge Server"""
    
    def __init__(self):
        super().__init__(
            name="Dr. Strunz Knowledge MCP Server",
            version="0.6.2"
        )
        
        # Initialize components
        self.vector_store = None
        self.searcher = None
        self._initialize_components()
        
        # Register handlers
        self.register_request_handlers()
        
    def _initialize_components(self):
        """Initialize vector store and searcher"""
        try:
            self.vector_store = get_vector_store_singleton(index_path="data/faiss_indices")
            self.searcher = KnowledgeSearcher(self.vector_store)
            logger.info(f"Vector store loaded with {len(self.vector_store.documents)} documents")
        except Exception as e:
            logger.warning(f"Vector store not available: {e}")
            
    def register_request_handlers(self):
        """Register all MCP request handlers"""
        
        @self.on_request("initialize")
        async def handle_initialize(params: dict) -> InitializeResult:
            """Handle initialization request"""
            return InitializeResult(
                protocol_version="2025-03-26",
                server_info=ServerInfo(
                    name="Dr. Strunz Knowledge MCP Server",
                    version="0.6.2"
                ),
                capabilities=ServerCapabilities(
                    tools={"listChanged": False},
                    prompts={"listChanged": False}  # Critical for Claude.ai!
                )
            )
            
        @self.on_request("tools/list")
        async def handle_tools_list(params: dict) -> ListToolsResult:
            """List available tools"""
            tools = []
            
            for name, func in tool_registry.items():
                tools.append(Tool(
                    name=name,
                    description=func.__doc__ or f"Tool: {name}",
                    input_schema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": True
                    }
                ))
                
            return ListToolsResult(tools=tools)
            
        @self.on_request("tools/call")
        async def handle_tool_call(params: dict) -> CallToolResult:
            """Execute a tool"""
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in tool_registry:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            # Execute tool
            result = await self._execute_tool(tool_name, arguments)
            
            return CallToolResult(
                content=[TextContent(text=json.dumps(result, indent=2))]
            )
            
        @self.on_request("prompts/list")
        async def handle_prompts_list(params: dict) -> ListPromptsResult:
            """List available prompts"""
            prompts = [
                Prompt(
                    name="health_assessment",
                    description="Comprehensive health assessment based on symptoms and history",
                    arguments=[
                        PromptArgument(
                            name="symptoms",
                            description="Current symptoms",
                            required=True
                        ),
                        PromptArgument(
                            name="history",
                            description="Medical history",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="supplement_protocol",
                    description="Create personalized supplement protocol",
                    arguments=[
                        PromptArgument(
                            name="goals",
                            description="Health goals",
                            required=True
                        ),
                        PromptArgument(
                            name="conditions",
                            description="Existing conditions",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="nutrition_plan",
                    description="Design optimal nutrition plan",
                    arguments=[
                        PromptArgument(
                            name="dietary_preferences",
                            description="Dietary preferences and restrictions",
                            required=True
                        )
                    ]
                )
            ]
            
            return ListPromptsResult(prompts=prompts)
            
        @self.on_request("prompts/get")
        async def handle_prompt_get(params: dict) -> GetPromptResult:
            """Get a specific prompt"""
            prompt_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if prompt_name == "health_assessment":
                messages = [
                    UserMessage(
                        content=TextContent(
                            text=f"I need help with these symptoms: {arguments.get('symptoms', 'general health concerns')}"
                        )
                    ),
                    AssistantMessage(
                        content=TextContent(
                            text="I'll help analyze your symptoms based on Dr. Strunz's approach. Let me search for relevant information..."
                        )
                    )
                ]
                
                # Add search results if available
                if self.searcher and arguments.get('symptoms'):
                    results = self.searcher.search(arguments['symptoms'], limit=3)
                    if results:
                        messages.append(
                            AssistantMessage(
                                content=TextContent(
                                    text=f"Based on Dr. Strunz's teachings, here are relevant insights:\n\n{json.dumps(results[0], indent=2)}"
                                )
                            )
                        )
                        
            elif prompt_name == "supplement_protocol":
                messages = [
                    UserMessage(
                        content=TextContent(
                            text=f"My health goals are: {arguments.get('goals', 'optimal health')}"
                        )
                    ),
                    AssistantMessage(
                        content=TextContent(
                            text="I'll create a personalized supplement protocol based on Dr. Strunz's recommendations..."
                        )
                    )
                ]
                
            elif prompt_name == "nutrition_plan":
                messages = [
                    UserMessage(
                        content=TextContent(
                            text=f"My dietary preferences: {arguments.get('dietary_preferences', 'flexible')}"
                        )
                    ),
                    AssistantMessage(
                        content=TextContent(
                            text="I'll design an optimal nutrition plan following Dr. Strunz's molecular medicine principles..."
                        )
                    )
                ]
            else:
                raise ValueError(f"Unknown prompt: {prompt_name}")
                
            return GetPromptResult(
                messages=messages,
                description=f"Prompt for {prompt_name}"
            )
            
    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Execute a tool and return results"""
        tool_func = tool_registry[tool_name]
        
        # Handle special cases that need searcher
        if tool_name == "knowledge_search" and self.searcher:
            return self.searcher.search(
                query=arguments.get("query", ""),
                sources=arguments.get("sources"),
                limit=arguments.get("limit", 10),
                filters=arguments.get("filters", {})
            )
            
        # Execute other tools
        if tool_func:
            return tool_func(**arguments)
        else:
            return {"error": f"Tool {tool_name} not implemented"}


def create_sse_app():
    """Create SSE application for HTTP transport"""
    from mcp.server.sse import MCPSSEServer
    
    server = StrunzMCPServer()
    sse_server = MCPSSEServer(server)
    
    return sse_server.app


def create_stdio_app():
    """Create stdio application"""
    from mcp.server.stdio import MCPStdioServer
    
    server = StrunzMCPServer()
    stdio_server = MCPStdioServer(server)
    
    return stdio_server


def main():
    """Main entry point"""
    # Check environment
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
    if is_railway or os.environ.get('USE_SSE'):
        # HTTP/SSE mode for Railway or explicit SSE
        logger.info("Starting MCP server with SSE transport")
        app = create_sse_app()
        
        # For Railway/production
        import uvicorn
        port = int(os.environ.get('PORT', 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Stdio mode for local development
        logger.info("Starting MCP server with stdio transport")
        stdio_server = create_stdio_app()
        stdio_server.run()


if __name__ == "__main__":
    main()