import asyncio
import json
import logging
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

from ..rag import FAISSVectorStore, DocumentProcessor

logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("strunz-knowledge-base")

# Initialize FastAPI for SSE endpoint
app = FastAPI(title="Strunz Knowledge Base MCP Server")

# Global vector store instance
vector_store = FAISSVectorStore()

# MCP System Prompt
SYSTEM_PROMPT = """You are "Strunz-Wissen-GPT", a specialized AI assistant. Your sole purpose is to provide users with accurate, evidence-based insights from the knowledge base of Dr. Ulrich Strunz.

**Your Context:**
- You have access to a comprehensive, private database of articles and forum discussions written by or related to Dr. Strunz.
- This knowledge covers topics like nutrition, fitness, health, mental well-being, and preventative medicine.
- You operate exclusively based on the information within this database. Do not use external knowledge.

**Your Instructions:**
1.  **Prioritize Relevance and Recency:** When answering questions, always prioritize the most relevant information. When multiple sources are relevant, give precedence to the newest articles and the forum posts with the most user engagement.
2.  **Use Your Tools:** You have a set of tools to search the knowledge base. Use them to find information before formulating an answer. Announce which tool you are using (e.g., "Searching for the latest insights on Vitamin D...").
3.  **Cite Your Sources:** For every piece of information you provide, you MUST cite the source article or forum post title and its publication date.
4.  **Be Precise and Objective:** Answer questions directly. If the knowledge base does not contain an answer, state that clearly. Do not speculate or offer personal opinions.
5.  **User Roles:** Be aware that users may be patients, athletes, or general health enthusiasts. Tailor the complexity of your answers accordingly, but never sacrifice accuracy."""


@mcp.tool()
async def knowledge_search(
    query: str, 
    category: Optional[str] = None, 
    min_date: Optional[str] = None
) -> List[Dict]:
    """Search the vector database for relevant information.
    
    Args:
        query: Search query
        category: Optional category filter (News, Fitness, Gesundheit, etc.)
        min_date: Optional minimum date filter (YYYY-MM-DD format)
    
    Returns:
        List of relevant text chunks with metadata
    """
    logger.info(f"Searching for: {query} (category: {category}, min_date: {min_date})")
    
    # Build metadata filter
    filter_metadata = {}
    if category:
        filter_metadata['category'] = category
    
    # Perform search
    results = vector_store.search(query, k=5, filter_metadata=filter_metadata)
    
    # Format results
    formatted_results = []
    for doc, score in results:
        result = {
            'content': doc.content,
            'score': score,
            'metadata': doc.metadata
        }
        
        # Apply date filter if specified
        if min_date and 'post_date' in doc.metadata:
            try:
                post_date = datetime.strptime(doc.metadata['post_date'], '%d.%m.%Y')
                min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
                if post_date < min_date_obj:
                    continue
            except:
                pass
        
        formatted_results.append(result)
    
    logger.info(f"Found {len(formatted_results)} results")
    return formatted_results


@mcp.tool()
async def summarize_posts(post_ids: List[str]) -> str:
    """Generate a summary of specific posts.
    
    Args:
        post_ids: List of post IDs to summarize
    
    Returns:
        Concise summary of the posts
    """
    logger.info(f"Summarizing posts: {post_ids}")
    
    # Retrieve posts
    posts = []
    for post_id in post_ids:
        if post_id in vector_store.id_to_idx:
            idx = vector_store.id_to_idx[post_id]
            doc = vector_store.documents[idx]
            posts.append(doc)
    
    if not posts:
        return "Keine Posts mit den angegebenen IDs gefunden."
    
    # Create summary
    summary_parts = []
    for post in posts:
        title = post.metadata.get('post_title', 'Unbekannter Titel')
        date = post.metadata.get('post_date', 'Unbekanntes Datum')
        content_preview = post.content[:200] + "..." if len(post.content) > 200 else post.content
        
        summary_parts.append(f"**{title}** ({date}): {content_preview}")
    
    return "\n\n".join(summary_parts)


@mcp.tool()
async def get_latest_insights(category: str, limit: int = 5) -> List[Dict]:
    """Get the most recent posts from a category.
    
    Args:
        category: Category name (News, Fitness, Gesundheit, etc.)
        limit: Maximum number of posts to return
    
    Returns:
        List of recent posts with metadata
    """
    logger.info(f"Getting latest insights for category: {category}")
    
    # Filter documents by category
    category_docs = []
    for doc in vector_store.documents:
        if doc.metadata.get('category') == category and not doc.metadata.get('deleted'):
            category_docs.append(doc)
    
    # Sort by date
    def get_date(doc):
        date_str = doc.metadata.get('post_date', '01.01.1900')
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except:
            return datetime(1900, 1, 1)
    
    category_docs.sort(key=get_date, reverse=True)
    
    # Return top results
    results = []
    for doc in category_docs[:limit]:
        results.append({
            'id': doc.id,
            'title': doc.metadata.get('post_title', 'Unbekannt'),
            'date': doc.metadata.get('post_date', 'Unbekannt'),
            'content_preview': doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
            'metadata': doc.metadata
        })
    
    return results


@mcp.tool()
async def get_most_discussed_topics(category: str, limit: int = 5) -> List[Dict]:
    """Get posts with the most engagement in a category.
    
    Args:
        category: Category name
        limit: Maximum number of topics to return
    
    Returns:
        List of most discussed topics
    """
    logger.info(f"Getting most discussed topics for category: {category}")
    
    # Filter documents by category
    category_docs = []
    for doc in vector_store.documents:
        if doc.metadata.get('category') == category and not doc.metadata.get('deleted'):
            category_docs.append(doc)
    
    # Sort by engagement metrics (using content length as proxy)
    category_docs.sort(key=lambda d: len(d.content), reverse=True)
    
    # Group by title to avoid duplicates
    seen_titles = set()
    results = []
    
    for doc in category_docs:
        title = doc.metadata.get('post_title', 'Unbekannt')
        if title not in seen_titles and len(results) < limit:
            seen_titles.add(title)
            results.append({
                'id': doc.id,
                'title': title,
                'date': doc.metadata.get('post_date', 'Unbekannt'),
                'engagement_score': len(doc.content),  # Using length as proxy
                'content_preview': doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                'metadata': doc.metadata
            })
    
    return results


# SSE Event Generator
async def generate_sse_events(request: Request, prompt: str) -> AsyncGenerator[str, None]:
    """Generate SSE events for streaming responses."""
    try:
        # Initial event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing request...'})}\n\n"
        
        # Simulate tool usage (in real implementation, this would call the LLM)
        yield f"data: {json.dumps({'type': 'tool_use', 'tool': 'knowledge_search', 'query': prompt})}\n\n"
        
        # Search knowledge base
        results = await knowledge_search(prompt)
        
        if results:
            # Stream results
            for i, result in enumerate(results):
                event_data = {
                    'type': 'result',
                    'index': i,
                    'content': result['content'][:500] + "...",
                    'metadata': result['metadata']
                }
                yield f"data: {json.dumps(event_data)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
        else:
            yield f"data: {json.dumps({'type': 'no_results', 'message': 'Keine relevanten Informationen gefunden.'})}\n\n"
        
        # Final event
        yield f"data: {json.dumps({'type': 'complete', 'message': 'Request completed'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in SSE generation: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


# FastAPI Routes
@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Strunz Knowledge Base MCP Server",
        "version": "1.0.0",
        "status": "running",
        "vector_store_stats": vector_store.get_stats()
    }


@app.get("/sse")
async def sse_endpoint(request: Request, q: str):
    """SSE endpoint for streaming responses."""
    return EventSourceResponse(generate_sse_events(request, q))


@app.post("/index/rebuild")
async def rebuild_index():
    """Rebuild the vector index from processed documents."""
    processor = DocumentProcessor(vector_store)
    stats = processor.process_all_documents()
    return {
        "status": "success",
        "stats": stats,
        "vector_store_stats": vector_store.get_stats()
    }


# Mount MCP to FastAPI
app.mount("/mcp", mcp)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"SSE endpoint available at http://{host}:{port}/sse")
    logger.info(f"MCP tools available at http://{host}:{port}/mcp")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()