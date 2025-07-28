#!/usr/bin/env python3
"""
Dr. Strunz Knowledge Base MCP Server - Version 6.0
Hybrid approach using FastMCP with uvicorn for proper SSE support
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

# Initialize the knowledge searcher at module load time
initialize_knowledge_searcher()

# Create FastMCP server with stateful session management
mcp = FastMCP(
    name="Dr. Strunz Knowledge Server v6.0",
    # Enable stateful session management for proper SSE support
    stateless_http=False,
    # Disable JSON responses to use proper SSE streaming
    json_response=False
)

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
def get_health_stats() -> str:
    """
    Get statistics about the Dr. Strunz knowledge base.
    
    Returns:
        Statistics about available content
    """
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

# Export the run_server function for main.py
async def run_server():
    """Run the SSE server using uvicorn"""
    import uvicorn
    
    # Get the SSE app from FastMCP
    app = mcp.sse_app()
    
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Dr. Strunz Knowledge MCP Server v6.0 on port {port}")
    
    # Run with uvicorn
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # For direct execution, run the server
    asyncio.run(run_server())