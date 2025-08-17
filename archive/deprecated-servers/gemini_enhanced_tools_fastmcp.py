"""
Gemini-Enhanced MCP Tools for Auth-less Client Integration
These tools use Gemini API to provide intelligent search and synthesis
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.llm.gemini_client import GeminiClient, GeminiEnhancedSearch
from src.rag.search import KnowledgeSearcher

logger = logging.getLogger(__name__)


def register_gemini_tools(mcp_server: FastMCP, knowledge_searcher: KnowledgeSearcher):
    """
    Register Gemini-enhanced tools with the MCP server
    
    Args:
        mcp_server: FastMCP server instance
        knowledge_searcher: KnowledgeSearcher instance
    """
    
    # Check if Gemini API key is available
    if not os.getenv('GOOGLE_GEMINI_API_KEY'):
        logger.warning("GOOGLE_GEMINI_API_KEY not found - Gemini-enhanced tools will not be available")
        return
    
    @mcp_server.tool()
    async def search_knowledge_gemini(
        query: str,
        limit: int = 10,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search Dr. Strunz's knowledge base with Gemini-powered synthesis.
        This provides intelligent answers by combining search results with LLM understanding.
        
        Args:
            query: Search query string
            limit: Maximum number of results to synthesize (1-20)
            sources: Optional list of sources to filter (books, news, forum)
        
        Returns:
            Synthesized search results with key insights
        """
        try:
            # Validate parameters
            limit = max(1, min(limit, 20))
            
            # Create Gemini client
            async with GeminiClient() as gemini_client:
                enhanced_search = GeminiEnhancedSearch(knowledge_searcher, gemini_client)
                
                # Perform enhanced search
                results = await enhanced_search.search(
                    query=query,
                    k=limit,
                    sources=sources
                )
                
                return {
                    "status": "success",
                    "query": results['query'],
                    "answer": results['synthesis'],
                    "key_concepts": results['key_concepts'],
                    "sources_used": results['sources_used'],
                    "raw_results_count": len(results['raw_results']),
                    "enhanced_by": results['enhanced_by']
                }
                
        except Exception as e:
            logger.error(f"Gemini search error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Use search_knowledge tool for non-Gemini search"
            }
    
    @mcp_server.tool()
    async def ask_strunz_gemini(
        question: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask a direct question about Dr. Strunz's health and nutrition philosophy.
        Uses Gemini to provide intelligent, contextualized answers.
        
        Args:
            question: Your health or nutrition question
            context: Optional context about your situation
        
        Returns:
            Personalized answer based on Dr. Strunz's teachings
        """
        try:
            # Search for relevant content first
            results = knowledge_searcher.search(question, k=10)
            
            # Format search results
            search_context = []
            for result in results:
                search_context.append(f"Source: {result.source}\nContent: {result.text[:300]}...")
            
            # Create prompt
            full_context = "\n\n".join(search_context)
            if context:
                full_context = f"User Context: {context}\n\n{full_context}"
            
            prompt = f"""You are Dr. Strunz's knowledgeable assistant, helping people understand and apply his health and nutrition principles.

Based on Dr. Strunz's teachings and the following knowledge base excerpts, please answer this question:

Question: {question}

Relevant Knowledge from Dr. Strunz:
{full_context}

Provide a helpful, practical answer that:
1. Directly addresses the question
2. Includes specific recommendations from Dr. Strunz
3. Mentions any relevant vitamins, minerals, or nutrients
4. Suggests practical action steps
5. Notes any scientific backing mentioned

Keep the tone informative yet accessible."""

            async with GeminiClient() as gemini_client:
                answer = await gemini_client.generate_content(prompt)
                
                # Extract key recommendations
                concepts = await gemini_client.extract_key_concepts(answer)
                
                return {
                    "status": "success",
                    "question": question,
                    "answer": answer,
                    "key_recommendations": concepts,
                    "sources_consulted": len(results),
                    "has_context": bool(context)
                }
                
        except Exception as e:
            logger.error(f"Gemini ask error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "suggestion": "Try rephrasing your question or use search_knowledge_gemini"
            }
    
    @mcp_server.tool()
    async def analyze_health_topic_gemini(
        topic: str,
        aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get a comprehensive analysis of a health topic from Dr. Strunz's perspective.
        Uses Gemini to synthesize information across multiple sources.
        
        Args:
            topic: Health topic to analyze (e.g., "vitamin D", "stress", "immune system")
            aspects: Optional specific aspects to focus on (e.g., ["benefits", "dosage", "sources"])
        
        Returns:
            Comprehensive analysis with multiple perspectives
        """
        try:
            # Default aspects if none provided
            if not aspects:
                aspects = ["benefits", "recommendations", "scientific evidence", "practical tips"]
            
            # Search for comprehensive information
            results = knowledge_searcher.search(topic, k=20)
            
            # Group results by source type
            books_content = []
            news_content = []
            forum_content = []
            
            for result in results:
                content_snippet = f"{result.text[:400]}..."
                if 'book' in result.source.lower():
                    books_content.append(content_snippet)
                elif 'news' in result.source.lower():
                    news_content.append(content_snippet)
                else:
                    forum_content.append(content_snippet)
            
            # Create comprehensive prompt
            prompt = f"""Provide a comprehensive analysis of "{topic}" based on Dr. Strunz's teachings.

Information from Books:
{chr(10).join(books_content[:5]) if books_content else 'No book content found'}

Information from News Articles:
{chr(10).join(news_content[:5]) if news_content else 'No news content found'}

Information from Forum Discussions:
{chr(10).join(forum_content[:5]) if forum_content else 'No forum content found'}

Please analyze the following aspects:
{chr(10).join(f"- {aspect}" for aspect in aspects)}

Structure your analysis with:
1. Overview of Dr. Strunz's perspective on {topic}
2. Detailed analysis of each requested aspect
3. Practical recommendations
4. Any warnings or considerations
5. Summary of key takeaways"""

            async with GeminiClient() as gemini_client:
                analysis = await gemini_client.generate_content(prompt, temperature=0.5)
                
                return {
                    "status": "success",
                    "topic": topic,
                    "aspects_analyzed": aspects,
                    "analysis": analysis,
                    "sources": {
                        "books": len(books_content),
                        "news": len(news_content),
                        "forum": len(forum_content)
                    },
                    "total_sources": len(results)
                }
                
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp_server.tool()
    async def validate_gemini_connection() -> Dict[str, Any]:
        """
        Validate that Gemini API connection is working.
        Useful for testing auth-less client integration.
        
        Returns:
            Connection status and API information
        """
        try:
            async with GeminiClient() as gemini_client:
                # Test API key
                is_valid = await gemini_client.validate_api_key()
                
                # Get API info
                test_response = await gemini_client.generate_content(
                    "Briefly describe Dr. Strunz's approach to health in one sentence."
                )
                
                return {
                    "status": "success",
                    "api_key_valid": is_valid,
                    "api_key_configured": bool(os.getenv('GOOGLE_GEMINI_API_KEY')),
                    "model": "gemini-2.5-flash",
                    "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response,
                    "ready_for_client": is_valid,
                    "auth_less_compatible": True
                }
                
        except Exception as e:
            logger.error(f"Gemini validation error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(os.getenv('GOOGLE_GEMINI_API_KEY')),
                "ready_for_client": False,
                "auth_less_compatible": False,
                "suggestion": "Check GOOGLE_GEMINI_API_KEY environment variable"
            }
    
    logger.info("Gemini-enhanced tools registered successfully")
    return True


# Utility function to test Gemini tools
async def test_gemini_tools():
    """Test the Gemini-enhanced tools"""
    from src.rag.search import KnowledgeSearcher
    
    # Initialize components
    searcher = KnowledgeSearcher()
    mcp = FastMCP(name="Test Server")
    
    # Register tools
    register_gemini_tools(mcp, searcher)
    
    # Test validation
    print("Testing Gemini connection...")
    # This would need to be called through the MCP server in practice
    
    return True


if __name__ == "__main__":
    asyncio.run(test_gemini_tools())