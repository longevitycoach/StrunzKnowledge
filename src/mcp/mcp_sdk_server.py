#!/usr/bin/env python3
"""
Dr. Strunz Knowledge MCP Server - Official SDK Implementation

This is a clean implementation using the official MCP Python SDK that properly
supports prompts capability for Claude.ai and Claude Desktop.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Sequence

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MCP SDK
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport

# Import FastAPI for SSE
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our components
try:
    from src.rag.search import get_vector_store_singleton, KnowledgeSearcher
    from src.mcp.enhanced_server import tool_registry
    from src.mcp.mcp_input_parser import preprocess_tool_arguments
    TOOLS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Tools not fully available: {e}")
    TOOLS_AVAILABLE = False
    tool_registry = {}
    
    def preprocess_tool_arguments(tool_name: str, arguments: dict) -> dict:
        return arguments


# Create the MCP server
server = Server("Dr. Strunz Knowledge MCP Server")

# Store vector store and searcher
vector_store = None
searcher = None


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools"""
    tools = []
    
    for name, func in tool_registry.items():
        tools.append(types.Tool(
            name=name,
            description=(func.__doc__ or "").strip() or f"Tool: {name}",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": True
            }
        ))
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent | types.ImageContent]:
    """Execute a tool"""
    if name not in tool_registry:
        raise ValueError(f"Unknown tool: {name}")
    
    # Preprocess arguments to handle Claude's JSON string inputs
    processed_args = preprocess_tool_arguments(name, arguments)
    
    try:
        # Special handling for knowledge_search
        if name == "knowledge_search":
            if searcher:
                result = searcher.search(
                    query=processed_args.get("query", ""),
                    sources=processed_args.get("sources"),
                    limit=processed_args.get("limit", 10),
                    filters=processed_args.get("filters", {})
                )
            else:
                result = {
                    "error": "Vector store not available",
                    "suggestion": "Please ensure FAISS indices are properly loaded"
                }
        else:
            # Call the tool function
            tool_func = tool_registry[name]
            result = tool_func(**processed_args)
        
        # Return as text content
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        error_result = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_result, indent=2)
        )]


@server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List available prompts - CRITICAL for Claude.ai integration!"""
    return [
        types.Prompt(
            name="health_assessment",
            description="Comprehensive health assessment based on symptoms and history",
            arguments=[
                types.PromptArgument(
                    name="symptoms",
                    description="Current symptoms or health concerns",
                    required=True
                ),
                types.PromptArgument(
                    name="history",
                    description="Medical history and background",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="supplement_protocol",
            description="Create personalized supplement protocol based on Dr. Strunz principles",
            arguments=[
                types.PromptArgument(
                    name="goals",
                    description="Health optimization goals",
                    required=True
                ),
                types.PromptArgument(
                    name="current_supplements",
                    description="Currently taking supplements",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="nutrition_plan",
            description="Design optimal nutrition plan following molecular medicine",
            arguments=[
                types.PromptArgument(
                    name="dietary_preferences",
                    description="Dietary preferences and restrictions",
                    required=True
                ),
                types.PromptArgument(
                    name="health_goals",
                    description="Specific health goals to address",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
    """Get a specific prompt with filled arguments"""
    if not arguments:
        arguments = {}
    
    messages = []
    
    if name == "health_assessment":
        symptoms = arguments.get("symptoms", "general health concerns")
        history = arguments.get("history", "")
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"I need help with these symptoms: {symptoms}. {f'My medical history includes: {history}' if history else ''}"
                )
            ),
            types.PromptMessage(
                role="assistant", 
                content=types.TextContent(
                    type="text",
                    text="I'll analyze your symptoms based on Dr. Strunz's molecular medicine approach. Let me search for relevant information..."
                )
            )
        ]
        
    elif name == "supplement_protocol":
        goals = arguments.get("goals", "optimal health")
        current = arguments.get("current_supplements", "")
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"My health goals are: {goals}. {f'I currently take: {current}' if current else ''}"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text="I'll create a personalized supplement protocol based on Dr. Strunz's recommendations for your goals..."
                )
            )
        ]
        
    elif name == "nutrition_plan":
        prefs = arguments.get("dietary_preferences", "flexible")
        goals = arguments.get("health_goals", "")
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"My dietary preferences: {prefs}. {f'Health goals: {goals}' if goals else ''}"
                )
            ),
            types.PromptMessage(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text="I'll design an optimal nutrition plan following Dr. Strunz's molecular medicine principles..."
                )
            )
        ]
    else:
        raise ValueError(f"Unknown prompt: {name}")
    
    return types.GetPromptResult(
        description=f"Prompt template for {name}",
        messages=messages
    )


def initialize_components():
    """Initialize vector store and searcher"""
    global vector_store, searcher
    
    try:
        vector_store = get_vector_store_singleton(index_path="data/faiss_indices")
        searcher = KnowledgeSearcher(vector_store)
        logger.info(f"Vector store loaded with {len(vector_store.documents)} documents")
    except Exception as e:
        logger.warning(f"Vector store not available: {e}")


# For SSE/HTTP deployment
app = FastAPI(title="Dr. Strunz Knowledge MCP Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    initialize_components()
    logger.info("Server initialized with official MCP SDK")


@app.get("/")
async def health():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": "Dr. Strunz Knowledge MCP Server",
        "version": "0.6.2",
        "sdk": "official-mcp-python",
        "capabilities": {
            "tools": len(tool_registry),
            "prompts": 3
        }
    })


# SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication"""
    logger.info("SSE connection established")
    
    # Create SSE transport
    transport = SseServerTransport()
    
    # Create response
    async def event_generator():
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connection', 'status': 'ready'})}\n\n"
            
            # Handle MCP communication
            async for message in transport.run(server):
                yield f"data: {json.dumps(message)}\n\n"
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def main():
    """Main entry point"""
    # Check environment
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    use_sse = os.environ.get('USE_SSE') == 'true'
    
    # Initialize components
    initialize_components()
    
    if is_railway or use_sse:
        # HTTP/SSE mode
        logger.info("Starting MCP server with SSE transport (official SDK)")
        port = int(os.environ.get('PORT', 8000))
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        # Stdio mode
        logger.info("Starting MCP server with stdio transport (official SDK)")
        asyncio.run(stdio_server(server).run())


if __name__ == "__main__":
    main()