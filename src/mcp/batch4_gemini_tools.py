"""
Batch 4: Gemini-Enhanced Tools Implementation (Final Batch)
Dynamic integration with Gemini API for enhanced search and synthesis
This completes the FastMCP to Official MCP SDK migration
"""

import os
import logging
from typing import Optional, List, Dict, Any
from src.llm.gemini_client import GeminiClient, GeminiEnhancedSearch

logger = logging.getLogger(__name__)


class GeminiEnhancedTools:
    """Implementation of Batch 4 Gemini-enhanced tools with dynamic integration"""
    
    def __init__(self, search_tool):
        """Initialize with reference to the search tool"""
        self.search_tool = search_tool
        self.gemini_available = bool(os.getenv('GOOGLE_GEMINI_API_KEY'))
        
        if not self.gemini_available:
            logger.warning("GOOGLE_GEMINI_API_KEY not found - Gemini tools will return fallback messages")
    
    async def search_knowledge_gemini(
        self,
        query: str,
        limit: int = 10,
        sources: Optional[List[str]] = None
    ) -> str:
        """
        Search Dr. Strunz's knowledge base with Gemini-powered synthesis.
        Provides intelligent answers by combining search results with LLM understanding.
        
        Args:
            query: Search query string
            limit: Maximum number of results to synthesize (1-20)
            sources: Optional list of sources to filter (books, news, forum)
        
        Returns:
            Synthesized search results with key insights
        """
        if not self.gemini_available:
            return ("# Gemini-Enhanced Search Not Available\n\n"
                   "**Error**: GOOGLE_GEMINI_API_KEY not configured.\n\n"
                   "To enable Gemini-enhanced search:\n"
                   "1. Set the GOOGLE_GEMINI_API_KEY environment variable\n"
                   "2. Restart the server\n\n"
                   "**Alternative**: Use the standard `knowledge_search` tool instead.")
        
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Validate parameters
        limit = max(1, min(limit, 20))
        
        try:
            async with GeminiClient() as gemini_client:
                enhanced_search = GeminiEnhancedSearch(self.search_tool, gemini_client)
                
                # Perform enhanced search
                results = await enhanced_search.search(
                    query=query,
                    k=limit,
                    sources=sources
                )
                
                # Format response
                response = f"# Gemini-Enhanced Search: {query}\n\n"
                response += "## AI-Synthesized Answer\n\n"
                response += results['synthesis'] + "\n\n"
                
                if results.get('key_concepts'):
                    response += "## Key Concepts\n\n"
                    response += "- " + "\n- ".join(results['key_concepts']) + "\n\n"
                
                response += "## Sources Used\n\n"
                response += f"*Analyzed {len(results['raw_results'])} results from: "
                response += ", ".join(results['sources_used']) + "*\n\n"
                
                response += "---\n\n"
                response += f"*Enhanced by {results['enhanced_by']} for intelligent synthesis*"
                
                return response
                
        except Exception as e:
            logger.error(f"Gemini search error: {e}")
            return (f"# Gemini Search Error\n\n"
                   f"**Error**: {str(e)}\n\n"
                   f"**Suggestion**: Use the standard `knowledge_search` tool as fallback.\n\n"
                   f"*This error may indicate API rate limits or connectivity issues.*")
    
    async def ask_strunz_gemini(
        self,
        question: str,
        context: Optional[str] = None
    ) -> str:
        """
        Ask a direct question about Dr. Strunz's health and nutrition philosophy.
        Uses Gemini to provide intelligent, contextualized answers.
        
        Args:
            question: Your health or nutrition question
            context: Optional context about your situation
        
        Returns:
            Personalized answer based on Dr. Strunz's teachings
        """
        if not self.gemini_available:
            return ("# Gemini Q&A Not Available\n\n"
                   "**Error**: GOOGLE_GEMINI_API_KEY not configured.\n\n"
                   "To enable Gemini Q&A:\n"
                   "1. Set the GOOGLE_GEMINI_API_KEY environment variable\n"
                   "2. Restart the server\n\n"
                   "**Alternative**: Use `knowledge_search` with your question.")
        
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        try:
            # Search for relevant content first
            results = self.search_tool.search(question, k=10)
            
            if not results:
                return (f"# No Information Found\n\n"
                       f"Unfortunately, I couldn't find relevant information about '{question}' "
                       f"in Dr. Strunz's knowledge base.\n\n"
                       f"Try rephrasing your question or search for related topics.")
            
            # Format search results for context
            search_context = []
            for result in results[:8]:  # Use top 8 results
                search_context.append(
                    f"**Source**: {result.source}\n"
                    f"**Content**: {result.text[:400]}..."
                )
            
            # Create comprehensive prompt
            full_context = "\n\n".join(search_context)
            if context:
                full_context = f"**User Context**: {context}\n\n{full_context}"
            
            prompt = f"""You are Dr. Strunz's knowledgeable assistant, helping people understand and apply his health and nutrition principles.

Based on Dr. Strunz's teachings and the following knowledge base excerpts, please answer this question:

**Question**: {question}

**Relevant Knowledge from Dr. Strunz**:
{full_context}

Provide a helpful, practical answer that:
1. Directly addresses the question
2. Includes specific recommendations from Dr. Strunz
3. Mentions any relevant vitamins, minerals, or nutrients
4. Suggests practical action steps
5. Notes any scientific backing mentioned

Keep the tone informative yet accessible."""

            async with GeminiClient() as gemini_client:
                answer = await gemini_client.generate_content(prompt, temperature=0.7)
                
                # Extract key recommendations
                concepts = await gemini_client.extract_key_concepts(answer)
                
                # Format response
                response = f"# Dr. Strunz Q&A (Gemini-Enhanced)\n\n"
                response += f"**Your Question**: {question}\n\n"
                
                if context:
                    response += f"**Your Context**: {context}\n\n"
                
                response += "## Answer\n\n"
                response += answer + "\n\n"
                
                if concepts:
                    response += "## Key Recommendations\n\n"
                    response += "- " + "\n- ".join(concepts) + "\n\n"
                
                response += "---\n\n"
                response += f"*Based on {len(results)} sources from Dr. Strunz's knowledge base*\n"
                response += "*Enhanced with Gemini AI for personalized insights*"
                
                return response
                
        except Exception as e:
            logger.error(f"Gemini ask error: {e}")
            return (f"# Gemini Q&A Error\n\n"
                   f"**Error**: {str(e)}\n\n"
                   f"**Suggestion**: Try rephrasing your question or use `search_knowledge_gemini`.")
    
    async def analyze_health_topic_gemini(
        self,
        topic: str,
        aspects: Optional[List[str]] = None
    ) -> str:
        """
        Get a comprehensive analysis of a health topic from Dr. Strunz's perspective.
        Uses Gemini to synthesize information across multiple sources.
        
        Args:
            topic: Health topic to analyze (e.g., "vitamin D", "stress", "immune system")
            aspects: Optional specific aspects to focus on (e.g., ["benefits", "dosage", "sources"])
        
        Returns:
            Comprehensive analysis with multiple perspectives
        """
        if not self.gemini_available:
            return ("# Gemini Analysis Not Available\n\n"
                   "**Error**: GOOGLE_GEMINI_API_KEY not configured.\n\n"
                   "To enable Gemini analysis:\n"
                   "1. Set the GOOGLE_GEMINI_API_KEY environment variable\n"
                   "2. Restart the server\n\n"
                   "**Alternative**: Use `analyze_health_topic` for standard analysis.")
        
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        try:
            # Default aspects if none provided
            if not aspects:
                aspects = ["benefits", "recommendations", "scientific evidence", "practical tips"]
            
            # Search for comprehensive information
            results = self.search_tool.search(topic, k=20)
            
            if not results:
                return (f"# No Information Found\n\n"
                       f"No information about '{topic}' found in Dr. Strunz's knowledge base.")
            
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
            
            # Create comprehensive analysis prompt
            prompt = f"""Provide a comprehensive analysis of "{topic}" based on Dr. Strunz's teachings.

**Information from Books**:
{chr(10).join(books_content[:5]) if books_content else 'No book content found'}

**Information from News Articles**:
{chr(10).join(news_content[:5]) if news_content else 'No news content found'}

**Information from Forum Discussions**:
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
                
                # Format response
                response = f"# Comprehensive Analysis: {topic}\n\n"
                response += "*Powered by Gemini AI synthesis*\n\n"
                
                response += "## Aspects Analyzed\n\n"
                response += "- " + "\n- ".join(aspects) + "\n\n"
                
                response += "## Analysis\n\n"
                response += analysis + "\n\n"
                
                response += "## Source Distribution\n\n"
                response += f"- **Books**: {len(books_content)} excerpts\n"
                response += f"- **News Articles**: {len(news_content)} excerpts\n"
                response += f"- **Forum Discussions**: {len(forum_content)} excerpts\n"
                response += f"- **Total Sources**: {len(results)}\n\n"
                
                response += "---\n\n"
                response += "*Analysis synthesized from Dr. Strunz's comprehensive knowledge base*"
                
                return response
                
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return (f"# Gemini Analysis Error\n\n"
                   f"**Error**: {str(e)}\n\n"
                   f"**Suggestion**: Use `analyze_health_topic` for standard analysis.")
    
    async def validate_gemini_connection(self) -> str:
        """
        Validate that Gemini API connection is working.
        Useful for testing and debugging integration.
        
        Returns:
            Connection status and API information
        """
        response = "# Gemini Connection Status\n\n"
        
        if not self.gemini_available:
            response += "## ❌ Not Configured\n\n"
            response += "**GOOGLE_GEMINI_API_KEY**: Not found in environment\n\n"
            response += "### Setup Instructions\n\n"
            response += "1. Get an API key from: https://makersuite.google.com/app/apikey\n"
            response += "2. Set environment variable: `export GOOGLE_GEMINI_API_KEY=your-key`\n"
            response += "3. Restart the MCP server\n\n"
            response += "**Status**: Gemini tools unavailable"
            return response
        
        try:
            async with GeminiClient() as gemini_client:
                # Test API key
                is_valid = await gemini_client.validate_api_key()
                
                if is_valid:
                    # Get API info with test response
                    test_response = await gemini_client.generate_content(
                        "Briefly describe Dr. Strunz's approach to health in one sentence."
                    )
                    
                    response += "## ✅ Connected Successfully\n\n"
                    response += "**API Key Status**: Valid and working\n"
                    response += "**Model**: gemini-2.5-flash\n"
                    response += "**Ready for Use**: Yes\n\n"
                    
                    response += "### Test Response\n\n"
                    response += f"> {test_response[:200]}{'...' if len(test_response) > 200 else ''}\n\n"
                    
                    response += "### Available Gemini Tools\n\n"
                    response += "- `search_knowledge_gemini` - Enhanced search with AI synthesis\n"
                    response += "- `ask_strunz_gemini` - Direct Q&A with personalized answers\n"
                    response += "- `analyze_health_topic_gemini` - Comprehensive topic analysis\n"
                    response += "- `validate_gemini_connection` - This validation tool\n\n"
                    
                    response += "**Status**: All Gemini tools operational"
                else:
                    response += "## ⚠️ Invalid API Key\n\n"
                    response += "**API Key Status**: Invalid or expired\n"
                    response += "**Action Required**: Check your API key configuration\n\n"
                    response += "**Status**: Gemini tools unavailable"
                
                return response
                
        except Exception as e:
            response += "## ❌ Connection Error\n\n"
            response += f"**Error**: {str(e)}\n\n"
            response += "### Troubleshooting\n\n"
            response += "1. Check internet connectivity\n"
            response += "2. Verify API key is correct\n"
            response += "3. Check for API rate limits\n"
            response += "4. Review error logs for details\n\n"
            response += "**Status**: Gemini tools unavailable"
            
            return response