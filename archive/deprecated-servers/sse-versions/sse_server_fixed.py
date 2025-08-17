#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - Fixed SSE Transport
Using official MCP SDK patterns with proper session management
Version: 2.0.1
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Starlette and FastMCP
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# Import MCP SDK - Using FastMCP for simplified implementation
from mcp.server.fastmcp import FastMCP

# Import our knowledge search functionality
from src.rag.search import KnowledgeSearcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global knowledge searcher instance
knowledge_searcher = None

async def initialize_knowledge_searcher():
    """Initialize the knowledge searcher singleton"""
    global knowledge_searcher
    if knowledge_searcher is None:
        logger.info("Initializing KnowledgeSearcher...")
        knowledge_searcher = KnowledgeSearcher()
        await knowledge_searcher.initialize()
        logger.info("KnowledgeSearcher initialized successfully")

# Create FastMCP server with proper configuration
mcp = FastMCP(
    name="Dr. Strunz Knowledge Server",
    # Enable stateful session management for proper SSE support
    stateless_http=False,
    # Enable JSON responses for compatibility
    json_response=False
)

@mcp.tool()
async def search_knowledge(
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
        await initialize_knowledge_searcher()
    
    try:
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Perform search
        results = await knowledge_searcher.search(query, limit=limit)
        
        if not results:
            return f"No results found for query: {query}"
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            content_preview = result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', '')
            
            formatted_result = f"""**Result {i}:**
**Source:** {result.get('source', 'Unknown')}
**Content:** {content_preview}
**Relevance Score:** {result.get('score', 0):.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} results for "{query}":

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"

@mcp.tool()
async def search_knowledge_advanced(
    query: str,
    content_types: list[str] = None,
    limit: int = 10
) -> str:
    """
    Advanced search with content type filtering.
    
    Args:
        query: Search query string
        content_types: List of content types to search (books, news, forum)
        limit: Maximum number of results (1-50)
    
    Returns:
        Formatted search results with source information
    """
    if not knowledge_searcher:
        await initialize_knowledge_searcher()
    
    try:
        # Validate parameters
        limit = max(1, min(limit, 50))
        if content_types is None:
            content_types = ["books", "news", "forum"]
        
        # Perform search with filters
        results = await knowledge_searcher.search_advanced(
            query=query,
            content_types=content_types,
            limit=limit
        )
        
        if not results:
            return f"No results found for query: {query} in {content_types}"
        
        # Format results with type information
        formatted_results = []
        for i, result in enumerate(results, 1):
            content_preview = result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', '')
            content_type = result.get('type', 'unknown')
            
            formatted_result = f"""**Result {i}:**
**Type:** {content_type.upper()}
**Source:** {result.get('source', 'Unknown')}
**Content:** {content_preview}
**Relevance Score:** {result.get('score', 0):.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} results for "{query}" in {content_types}:

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return f"Advanced search failed: {str(e)}"

@mcp.tool()
async def get_book_content(
    book_title: str,
    page_range: str = "1-5"
) -> str:
    """
    Get content from a specific Dr. Strunz book.
    
    Args:
        book_title: Title or partial title of the book
        page_range: Page range (e.g., "1-5", "10-15")
    
    Returns:
        Book content for specified pages
    """
    if not knowledge_searcher:
        await initialize_knowledge_searcher()
    
    try:
        # Search for book content specifically
        results = await knowledge_searcher.search_books(
            book_title=book_title,
            page_range=page_range
        )
        
        if not results:
            return f"No content found for book '{book_title}' pages {page_range}"
        
        # Format book content results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""**Page {result.get('page', 'Unknown')}:**
{result.get('content', '')}

**Source:** {result.get('source', 'Unknown')}
"""
            formatted_results.append(formatted_result)
        
        return f"""Content from "{book_title}" (pages {page_range}):

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Book content error: {e}")
        return f"Failed to get book content: {str(e)}"

@mcp.tool()
async def search_news(
    query: str,
    limit: int = 10
) -> str:
    """
    Search Dr. Strunz news articles specifically.
    
    Args:
        query: Search query string
        limit: Maximum number of results (1-50)
    
    Returns:
        News articles matching the query
    """
    if not knowledge_searcher:
        await initialize_knowledge_searcher()
    
    try:
        # Search news specifically
        results = await knowledge_searcher.search_news(query, limit=max(1, min(limit, 50)))
        
        if not results:
            return f"No news articles found for query: {query}"
        
        # Format news results
        formatted_results = []
        for i, result in enumerate(results, 1):
            date = result.get('date', 'Unknown date')
            url = result.get('url', '')
            content_preview = result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', '')
            
            formatted_result = f"""**Article {i}:**
**Date:** {date}
**URL:** {url}
**Content:** {content_preview}
**Relevance Score:** {result.get('score', 0):.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} news articles for "{query}":

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"News search error: {e}")
        return f"News search failed: {str(e)}"

@mcp.tool()
async def get_health_stats() -> str:
    """
    Get statistics about the Dr. Strunz knowledge base.
    
    Returns:
        Statistics about available content
    """
    if not knowledge_searcher:
        await initialize_knowledge_searcher()
    
    try:
        stats = await knowledge_searcher.get_stats()
        
        return f"""**Dr. Strunz Knowledge Base Statistics:**

📚 **Books:** {stats.get('books', 0)} books processed
📰 **News Articles:** {stats.get('news', 0)} articles available  
💬 **Forum Posts:** {stats.get('forum', 0)} forum entries
📊 **Total Documents:** {stats.get('total_documents', 0)}
🔍 **Vector Embeddings:** {stats.get('total_vectors', 0)}

**Content Date Range:**
- Earliest: {stats.get('earliest_date', 'Unknown')}
- Latest: {stats.get('latest_date', 'Unknown')}

**Search Capabilities:**
- Semantic search across all content types
- Multi-language support (German primary)
- Advanced filtering by content type
- Book-specific content retrieval
"""
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return f"Failed to get statistics: {str(e)}"

# Health check endpoint
async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "2.0.1",
        "transport": "sse",
        "mcp_implementation": "Official MCP Python SDK (FastMCP)",
        "protocol_version": "2025-11-05",
        "tools_count": 5,
        "session_management": "stateful",
        "endpoints": {
            "sse": "/sse",
            "mcp": "/mcp",
            "oauth_register": "/oauth/register",
            "oauth_authorize": "/oauth/authorize",
            "oauth_token": "/oauth/token"
        }
    })

# OAuth endpoints for Claude.ai compatibility
async def oauth_register(request):
    """OAuth registration endpoint for Claude.ai"""
    return JSONResponse({
        "client_id": "strunz-knowledge-server",
        "client_secret": "demo-secret",
        "authorization_endpoint": f"{request.base_url}oauth/authorize",
        "token_endpoint": f"{request.base_url}oauth/token",
        "scope": "read"
    })

async def oauth_authorize(request):
    """OAuth authorization endpoint"""
    # Simple OAuth flow - in production, implement proper OAuth
    redirect_uri = request.query_params.get('redirect_uri')
    state = request.query_params.get('state', '')
    
    # Generate mock authorization code
    auth_code = "mock_auth_code_12345"
    
    from starlette.responses import RedirectResponse
    return RedirectResponse(f"{redirect_uri}?code={auth_code}&state={state}")

async def oauth_token(request):
    """OAuth token endpoint"""
    return JSONResponse({
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read"
    })

# Create Starlette app with proper MCP mounting and OAuth endpoints
app = Starlette(
    routes=[
        Route("/", endpoint=health_check, methods=["GET"]),
        Route("/health", endpoint=health_check, methods=["GET"]),
        # OAuth endpoints for Claude.ai compatibility
        Route("/oauth/register", endpoint=oauth_register, methods=["GET", "POST"]),
        Route("/oauth/authorize", endpoint=oauth_authorize, methods=["GET"]),
        Route("/oauth/token", endpoint=oauth_token, methods=["POST"]),
        # Claude.ai specific auth endpoints
        Route("/api/organizations/{org_id}/mcp/start-auth/{auth_id}", endpoint=oauth_authorize, methods=["GET"]),
        Route("/api/mcp/auth_callback", endpoint=oauth_authorize, methods=["GET"]),
        # Mount the MCP server for SSE transport
        Mount("/mcp", app=mcp.sse_app()),
        Mount("/sse", app=mcp.sse_app()),
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup event to initialize knowledge searcher
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v2.0.1 (Fixed SSE Transport)")
    logger.info("Using official MCP Python SDK (FastMCP)")
    await initialize_knowledge_searcher()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting fixed SSE server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)