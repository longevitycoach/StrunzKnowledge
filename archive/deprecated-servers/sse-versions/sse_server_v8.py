#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - Version 8.0
Enhanced with Gemini API endpoints and rate limiting
"""

import os
import sys
import logging
import contextlib
from pathlib import Path
from typing import Optional, List, Union

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import FastAPI and Starlette
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Mount

# Import MCP SDK - Using FastMCP for simplified implementation
from mcp.server.fastmcp import FastMCP

# Import our knowledge search functionality
from src.rag.search import KnowledgeSearcher

# Import Gemini API endpoint creator
from src.api.gemini_endpoint import create_gemini_endpoint

# Import Gemini-enhanced tools (if API key is available)
try:
    from src.mcp.tools.gemini_enhanced_tools import register_gemini_tools
    GEMINI_AVAILABLE = bool(os.environ.get('GOOGLE_GEMINI_API_KEY'))
except ImportError:
    GEMINI_AVAILABLE = False
    register_gemini_tools = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global knowledge searcher instance
knowledge_searcher = None

def initialize_knowledge_searcher():
    """Initialize the knowledge searcher singleton synchronously"""
    global knowledge_searcher
    if knowledge_searcher is None:
        logger.info("Initializing KnowledgeSearcher...")
        knowledge_searcher = KnowledgeSearcher()
        logger.info("KnowledgeSearcher initialized successfully")

# Create FastMCP server with stateful session management
mcp_server = FastMCP(
    name="Dr. Strunz Knowledge Server v2.3.0",
    # Enable stateful session management for proper SSE support
    stateless_http=False,
    # Disable JSON responses to use proper SSE streaming
    json_response=False
)

# Register all the existing MCP tools (search_knowledge, etc.)
# ... (keeping all existing tool definitions from v7)

@mcp_server.tool()
def search_knowledge(
    query: str,
    limit: int = 10
) -> str:
    """
    Search Dr. Strunz's knowledge base with semantic search.
    
    Args:
        query: Search query string
        limit: Maximum number of results (1-50)
    
    Returns:
        Formatted search results with source information
    """
    if not knowledge_searcher:
        initialize_knowledge_searcher()
    
    try:
        # Validate and sanitize parameters
        if not query or not isinstance(query, str):
            return "Error: Query must be a non-empty string"
        
        # Clean query
        query = query.strip()
        if not query:
            return "Error: Query cannot be empty"
        
        # Validate limit
        limit = max(1, min(limit, 50))
        
        logger.info(f"Searching for: '{query}' with limit={limit}")
        
        # Perform search - only pass the parameters that the method accepts
        results = knowledge_searcher.search(query=query, k=limit)
        
        if not results:
            return f"No results found for query: {query}"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            content_preview = result.text[:200] + "..." if len(result.text) > 200 else result.text
            
            formatted_result = f"""**Result {i}:**
**Source:** {result.source}
**Content:** {content_preview}
**Relevance Score:** {result.score:.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} results for "{query}":

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return f"Search failed: {str(e)}"

# Create FastAPI app
app = FastAPI(
    title="Dr. Strunz Knowledge MCP Server",
    version="2.3.0",
    description="MCP server with Gemini API integration and rate limiting"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth endpoints for Claude.ai compatibility
@app.get("/oauth/register")
@app.post("/oauth/register")
async def oauth_register(request: Request):
    """OAuth registration endpoint for Claude.ai"""
    return JSONResponse({
        "client_id": "strunz-knowledge-server",
        "client_secret": "demo-secret",
        "authorization_endpoint": f"{request.base_url}oauth/authorize",
        "token_endpoint": f"{request.base_url}oauth/token",
        "scope": "read"
    })

@app.get("/oauth/authorize")
async def oauth_authorize(request: Request):
    """OAuth authorization endpoint"""
    # Simple OAuth flow - in production, implement proper OAuth
    redirect_uri = request.query_params.get('redirect_uri')
    state = request.query_params.get('state', '')
    
    if redirect_uri:
        # Generate mock authorization code
        auth_code = "mock_auth_code_12345"
        return RedirectResponse(f"{redirect_uri}?code={auth_code}&state={state}")
    else:
        # Return HTML response for iframe communication
        return HTMLResponse('''
            <html>
                <body>
                    <h1>✓ Authorization Successful</h1>
                    <p>You can close this window.</p>
                    <script>
                        if (window.parent !== window) {
                            window.parent.postMessage({
                                type: 'mcp-oauth-success',
                                code: 'mock_auth_code_12345',
                                state: 'success'
                            }, '*');
                        }
                    </script>
                </body>
            </html>
        ''')

@app.post("/oauth/token")
async def oauth_token(request: Request):
    """OAuth token endpoint"""
    return JSONResponse({
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read"
    })

@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def start_auth(request: Request, org_id: str, auth_id: str):
    """Claude.ai start auth endpoint"""
    redirect_url = request.query_params.get('redirect_url')
    
    # Check if OAuth should be skipped (simplified mode)
    if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "true").lower() == "true":
        return JSONResponse({
            "status": "success",
            "auth_not_required": True,
            "server_url": str(request.base_url).rstrip('/')
        })
    
    # Otherwise redirect to OAuth flow
    auth_url = f"{request.base_url}oauth/authorize?client_id=strunz-{auth_id[:16]}&response_type=code&scope=read"
    return RedirectResponse(url=auth_url, status_code=302)

@app.get("/api/mcp/auth_callback")
async def auth_callback(request: Request):
    """OAuth callback handler"""
    code = request.query_params.get('code')
    state = request.query_params.get('state', '')
    
    # Return success HTML with postMessage for iframe communication
    return HTMLResponse(f'''
        <html>
            <body>
                <h1>✓ Successfully Connected!</h1>
                <p>Authorization complete. You can close this window.</p>
                <script>
                    if (window.parent !== window) {{
                        window.parent.postMessage({{
                            type: 'mcp-oauth-success',
                            code: '{code}',
                            state: '{state}'
                        }}, '*');
                    }}
                </script>
            </body>
        </html>
    ''')

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint - minimal public information"""
    # Calculate actual tools count
    tools_count = 12  # Standard tools (including search_knowledge)
    if GEMINI_AVAILABLE:
        tools_count += 4  # Gemini-enhanced tools
    
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "2.3.0",
        "mcp_version": "2025-11-05",
        "tools_available": tools_count,
        "knowledge_base": {
            "books": 13,
            "news_articles": 6953,
            "forum_discussions": 14435
        }
    })

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return await health_check(None)

# Simple search API endpoint for frontend
@app.post("/api/search")
async def api_search(request: Request):
    """Simple search endpoint for frontend compatibility"""
    try:
        body = await request.json()
        query = body.get('query', '')
        limit = body.get('limit', 10)
    except:
        return JSONResponse({"error": "Invalid JSON request"}, status_code=400)
    
    if not knowledge_searcher:
        initialize_knowledge_searcher()
    
    try:
        # Validate and sanitize parameters like the MCP tool does
        if not query or not isinstance(query, str):
            return JSONResponse({"error": "Query must be a non-empty string"}, status_code=400)
        
        # Clean query
        query = query.strip()
        if not query:
            return JSONResponse({"error": "Query cannot be empty"}, status_code=400)
        
        # Validate limit
        limit = max(1, min(limit, 50))
        
        logger.info(f"API Search for: '{query}' with limit={limit}")
        
        # Perform search - use the same call pattern as the MCP tool
        results = knowledge_searcher.search(query=query, k=limit)
        
        if not results:
            return JSONResponse({"content": f"No results found for query: {query}"})
        
        # Format results for frontend
        formatted_results = []
        for i, result in enumerate(results, 1):
            content_preview = result.text[:200] + "..." if len(result.text) > 200 else result.text
            
            formatted_result = f"""**Result {i}:**
**Source:** {result.source}
**Content:** {content_preview}
**Relevance Score:** {result.score:.3f}
"""
            formatted_results.append(formatted_result)
        
        response_text = f"""Found {len(results)} results for "{query}":

{chr(10).join(formatted_results)}"""
        
        return JSONResponse({"content": response_text})
        
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return JSONResponse({"error": f"Search failed: {str(e)}"}, status_code=500)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v8.0")
    logger.info("Using official MCP Python SDK (FastMCP)")
    logger.info("Enhanced with Gemini API endpoints and rate limiting")
    initialize_knowledge_searcher()
    
    # Register ALL standard tools first
    try:
        from src.mcp.tools.all_tools import register_all_tools
        register_all_tools(mcp_server, knowledge_searcher)
        logger.info("✅ All 12 standard tools registered successfully")
    except Exception as e:
        logger.error(f"Failed to register standard tools: {e}")
    
    # Register Gemini-enhanced tools if available
    if GEMINI_AVAILABLE and register_gemini_tools:
        try:
            register_gemini_tools(mcp_server, knowledge_searcher)
            logger.info("✅ Gemini-enhanced tools registered successfully")
            logger.info("🔑 Using server-side Gemini API key with rate limiting")
        except Exception as e:
            logger.warning(f"Failed to register Gemini tools: {e}")
    else:
        logger.info("ℹ️  Gemini tools not available (no API key configured)")
    
    # Create Gemini API endpoints
    if GEMINI_AVAILABLE:
        await create_gemini_endpoint(app)
        logger.info("✅ Gemini API endpoints created with rate limiting")

# Mount MCP SSE app at specific endpoints to avoid intercepting all routes
# This allows health checks and other endpoints to work properly
sse_app = mcp_server.sse_app()
app.mount("/sse", sse_app)
app.mount("/messages", sse_app)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Dr. Strunz Knowledge MCP Server v8.0 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)