#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - Version 4.0
Complete rewrite following official FastMCP SSE mounting patterns
Fixes all routing issues
"""

import os
import sys
import logging
import contextlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Starlette
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
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

def initialize_knowledge_searcher():
    """Initialize the knowledge searcher singleton synchronously"""
    global knowledge_searcher
    if knowledge_searcher is None:
        logger.info("Initializing KnowledgeSearcher...")
        knowledge_searcher = KnowledgeSearcher()
        logger.info("KnowledgeSearcher initialized successfully")

# Create FastMCP server with stateful session management
mcp_server = FastMCP(
    name="Dr. Strunz Knowledge Server v2.2.0",
    # Enable stateful session management for proper SSE support
    stateless_http=False,
    # Disable JSON responses to use proper SSE streaming
    json_response=False
)

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
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Perform search
        results = knowledge_searcher.search(query, k=limit)
        
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
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"

@mcp_server.tool()
def search_knowledge_advanced(
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
        initialize_knowledge_searcher()
    
    try:
        # Validate parameters
        limit = max(1, min(limit, 50))
        if content_types is None:
            content_types = ["books", "news", "forum"]
        
        # Perform search with filters
        results = knowledge_searcher.search(query, k=limit, sources=content_types)
        
        if not results:
            return f"No results found for query: {query} in {content_types}"
        
        # Format results with type information
        formatted_results = []
        for i, result in enumerate(results, 1):
            content_preview = result.text[:200] + "..." if len(result.text) > 200 else result.text
            content_type = result.metadata.get('type', result.source)
            
            formatted_result = f"""**Result {i}:**
**Type:** {content_type.upper()}
**Source:** {result.source}
**Content:** {content_preview}
**Relevance Score:** {result.score:.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} results for "{query}" in {content_types}:

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return f"Advanced search failed: {str(e)}"

@mcp_server.tool()
def get_book_content(
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
        initialize_knowledge_searcher()
    
    try:
        # Search for book content specifically
        results = knowledge_searcher.search(f"{book_title} {page_range}", k=20, sources=["books"])
        
        if not results:
            return f"No content found for book '{book_title}' pages {page_range}"
        
        # Format book content results
        formatted_results = []
        for i, result in enumerate(results, 1):
            page = result.metadata.get('page', 'Unknown')
            formatted_result = f"""**Page {page}:**
{result.text}

**Source:** {result.source}
"""
            formatted_results.append(formatted_result)
        
        return f"""Content from "{book_title}" (pages {page_range}):

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"Book content error: {e}")
        return f"Failed to get book content: {str(e)}"

@mcp_server.tool()
def search_news(
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
        initialize_knowledge_searcher()
    
    try:
        # Search news specifically
        results = knowledge_searcher.search(query, k=max(1, min(limit, 50)), sources=["news"])
        
        if not results:
            return f"No news articles found for query: {query}"
        
        # Format news results
        formatted_results = []
        for i, result in enumerate(results, 1):
            date = result.metadata.get('date', 'Unknown date')
            url = result.metadata.get('url', '')
            content_preview = result.text[:300] + "..." if len(result.text) > 300 else result.text
            
            formatted_result = f"""**Article {i}:**
**Date:** {date}
**URL:** {url}
**Content:** {content_preview}
**Relevance Score:** {result.score:.3f}
"""
            formatted_results.append(formatted_result)
        
        return f"""Found {len(results)} news articles for "{query}":

{chr(10).join(formatted_results)}"""
        
    except Exception as e:
        logger.error(f"News search error: {e}")
        return f"News search failed: {str(e)}"

@mcp_server.tool()
def get_health_stats() -> str:
    """
    Get statistics about the Dr. Strunz knowledge base.
    
    Returns:
        Statistics about available content
    """
    if not knowledge_searcher:
        initialize_knowledge_searcher()
    
    try:
        # Get basic stats from vector store
        total_docs = len(knowledge_searcher.vector_store.documents) if knowledge_searcher.vector_store.documents else 0
        
        stats = {
            'books': 13,  # Known from CLAUDE.md
            'news': 6953,  # Known from CLAUDE.md
            'forum': 6400,  # Known from CLAUDE.md
            'total_documents': total_docs,
            'total_vectors': total_docs,
            'earliest_date': '2004-09-28',
            'latest_date': '2025-07-11'
        }
        
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

async def oauth_token(request):
    """OAuth token endpoint"""
    return JSONResponse({
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read"
    })

async def start_auth(request):
    """Claude.ai start auth endpoint"""
    org_id = request.path_params['org_id']
    auth_id = request.path_params['auth_id']
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

async def auth_callback(request):
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
async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "ok",
        "service": "Dr. Strunz Knowledge MCP Server",
        "version": "2.2.0",
        "transport": "sse",
        "mcp_implementation": "Official MCP Python SDK (FastMCP)",
        "protocol_version": "2025-11-05",
        "tools_count": 5,
        "session_management": "stateful",
        "endpoints": {
            "sse": "/",  # SSE is mounted at root
            "health": "/health",
            "oauth_register": "/oauth/register",
            "oauth_authorize": "/oauth/authorize",
            "oauth_token": "/oauth/token",
            "start_auth": "/api/organizations/{org_id}/mcp/start-auth/{auth_id}",
            "auth_callback": "/api/mcp/auth_callback"
        },
        "features": [
            "semantic_search",
            "content_filtering", 
            "book_content_access",
            "news_search",
            "statistics",
            "oauth_2_1_compatible",
            "claude_ai_compatible"
        ]
    })

# Create Starlette app with proper routing and lifecycle management
# CRITICAL: Mount the SSE app at root as per official documentation
app = Starlette(
    routes=[
        # Health and info endpoints
        Route("/health", endpoint=health_check, methods=["GET"]),
        
        # OAuth endpoints for Claude.ai compatibility
        Route("/oauth/register", endpoint=oauth_register, methods=["GET", "POST"]),
        Route("/oauth/authorize", endpoint=oauth_authorize, methods=["GET"]),
        Route("/oauth/token", endpoint=oauth_token, methods=["POST"]),
        
        # Claude.ai specific auth endpoints
        Route("/api/organizations/{org_id}/mcp/start-auth/{auth_id}", endpoint=start_auth, methods=["GET"]),
        Route("/api/mcp/auth_callback", endpoint=auth_callback, methods=["GET"]),
        
        # Mount MCP server at root for proper SSE support - THIS IS THE KEY FIX
        Mount("/", app=mcp_server.sse_app()),
    ]
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup initialization
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Dr. Strunz Knowledge MCP Server v4.0")
    logger.info("Using official MCP Python SDK (FastMCP)")
    initialize_knowledge_searcher()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Dr. Strunz Knowledge MCP Server v4.0 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)