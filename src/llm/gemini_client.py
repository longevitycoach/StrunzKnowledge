"""
Gemini API Client for Auth-less MCP Integration
Enables direct LLM-powered search without server-side authentication
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Optional API key, defaults to environment variable
        """
        self.api_key = api_key or os.getenv('GOOGLE_GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "models/gemini-2.5-flash"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate content using Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Gemini API error: {response.status} - {error_text}")
                    raise Exception(f"Gemini API error: {response.status}")
                
                data = await response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
            
    async def search_knowledge_with_context(self, 
                                          query: str, 
                                          search_results: List[Dict[str, Any]],
                                          limit: int = 10) -> str:
        """
        Use Gemini to intelligently synthesize search results
        
        Args:
            query: User's search query
            search_results: Raw search results from vector store
            limit: Maximum number of results to include
            
        Returns:
            Synthesized response from Gemini
        """
        # Format search results for context
        context_parts = []
        for i, result in enumerate(search_results[:limit], 1):
            context_parts.append(f"""
Result {i}:
Source: {result.get('source', 'Unknown')}
Content: {result.get('text', '')[:500]}...
Relevance Score: {result.get('score', 0):.3f}
""")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are an expert on Dr. Ulrich Strunz's health and nutrition knowledge. 
Based on the following search results from Dr. Strunz's work, provide a comprehensive answer to the user's query.

User Query: {query}

Search Results from Dr. Strunz's Knowledge Base:
{context}

Please provide:
1. A direct answer to the user's question based on Dr. Strunz's teachings
2. Key insights and recommendations from the search results
3. Practical applications or action steps
4. Any relevant scientific backing mentioned in the results

Format your response in a clear, structured way that helps the user understand and apply Dr. Strunz's knowledge."""

        response = await self.generate_content(prompt, temperature=0.7)
        return response
        
    async def extract_key_concepts(self, text: str) -> List[str]:
        """
        Extract key health and nutrition concepts from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of key concepts
        """
        prompt = f"""Extract the key health and nutrition concepts from the following text.
Focus on:
- Vitamins and minerals
- Health conditions
- Nutrition principles
- Exercise and fitness concepts
- Medical terms

Text: {text[:1000]}...

Return only a comma-separated list of key concepts, nothing else."""

        response = await self.generate_content(prompt, temperature=0.3)
        concepts = [c.strip() for c in response.split(',') if c.strip()]
        return concepts[:10]  # Limit to top 10 concepts
        
    async def validate_api_key(self) -> bool:
        """
        Validate that the API key works
        
        Returns:
            True if API key is valid
        """
        try:
            response = await self.generate_content("Hello, please respond with 'API key is valid'")
            return "valid" in response.lower()
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False


class GeminiEnhancedSearch:
    """Enhanced search using Gemini for intelligent result synthesis"""
    
    def __init__(self, knowledge_searcher, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize enhanced search
        
        Args:
            knowledge_searcher: The base knowledge searcher instance
            gemini_client: Optional Gemini client instance
        """
        self.knowledge_searcher = knowledge_searcher
        self.gemini_client = gemini_client or GeminiClient()
        
    async def search(self, query: str, k: int = 10, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform enhanced search with Gemini synthesis
        
        Args:
            query: Search query
            k: Number of results
            sources: Optional source filters
            
        Returns:
            Enhanced search results with Gemini synthesis
        """
        # First, get raw search results
        raw_results = self.knowledge_searcher.search(query, k=k*2, sources=sources)  # Get more for better context
        
        # Format results for Gemini
        formatted_results = []
        for result in raw_results:
            formatted_results.append({
                'text': result.text,
                'source': result.source,
                'score': result.score,
                'metadata': result.metadata
            })
        
        # Get Gemini synthesis
        synthesis = await self.gemini_client.search_knowledge_with_context(
            query=query,
            search_results=formatted_results,
            limit=k
        )
        
        # Extract key concepts for enhanced understanding
        concepts = await self.gemini_client.extract_key_concepts(synthesis)
        
        return {
            'query': query,
            'synthesis': synthesis,
            'key_concepts': concepts,
            'raw_results': formatted_results[:k],
            'sources_used': list(set(r['source'] for r in formatted_results[:k])),
            'enhanced_by': 'gemini-2.5-flash'
        }


# Utility function for testing
async def test_gemini_integration():
    """Test Gemini integration with a sample query"""
    try:
        async with GeminiClient() as client:
            # Test basic generation
            print("Testing basic generation...")
            response = await client.generate_content("What are the benefits of Vitamin D according to Dr. Strunz?")
            print(f"Response: {response[:200]}...")
            
            # Test API key validation
            print("\nValidating API key...")
            is_valid = await client.validate_api_key()
            print(f"API key valid: {is_valid}")
            
            return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini_integration())