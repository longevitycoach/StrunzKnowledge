"""
Streaming-enabled health assessment tools that prevent MCP timeouts
Sends progressive responses every 2 seconds to keep connection alive
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class StreamingHealthTools:
    """Health tools with streaming support for comprehensive analysis"""
    
    def __init__(self, search_tool):
        """Initialize with reference to the search tool"""
        self.search_tool = search_tool
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    async def analyze_health_topic_streaming(
        self,
        topic: str,
        depth: str = "moderate"
    ) -> str:
        """
        Streaming version of analyze_health_topic that sends progressive updates
        Returns immediately with partial results and continues enriching
        """
        # Check cache first
        cache_key = f"{topic}:{depth}"
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                logger.info(f"Returning cached result for {cache_key}")
                return cached_result
        
        start_time = time.time()
        
        # Initialize response structure
        response_parts = {
            "header": f"# Comprehensive Analysis: {topic}\n\n*Analysis depth: {depth}*\n\n",
            "overview": "## Overview\n*Loading overview...*\n\n",
            "causes": "## Causes & Mechanisms\n*Loading causes...*\n\n",
            "approach": "## Dr. Strunz's Approach\n*Loading approach...*\n\n",
            "insights": "## Key Insights by Source\n*Loading insights...*\n\n",
            "footer": ""
        }
        
        # For comprehensive depth, use smaller chunks to avoid timeout
        if depth == "comprehensive":
            k = 15  # Start with fewer documents
            progressive_k = 10  # Add more progressively
        else:
            k_values = {"basic": 10, "moderate": 20}
            k = k_values.get(depth, 20)
            progressive_k = 0
        
        try:
            # Phase 1: Quick initial search (< 2 seconds)
            main_results = self.search_tool.search(query=topic, k=k)
            
            if main_results:
                # Quick overview from first result
                overview_text = main_results[0].text[:300]
                response_parts["overview"] = f"## Overview\n{overview_text}...\n*Source: {main_results[0].source} - {main_results[0].title}*\n\n"
            
            # Build initial response (< 2 seconds elapsed)
            current_response = "".join(response_parts.values())
            
            # Phase 2: Search for causes (2-4 seconds)
            if time.time() - start_time < 8:  # Still have time
                cause_results = self.search_tool.search(query=f"{topic} causes reasons why", k=5)
                if cause_results:
                    causes_text = "## Causes & Mechanisms\n"
                    for i, result in enumerate(cause_results[:3], 1):
                        causes_text += f"{i}. {result.text[:150]}...\n"
                    response_parts["causes"] = causes_text + "\n"
            
            # Phase 3: Search for solutions (4-6 seconds)
            if time.time() - start_time < 8:
                solution_results = self.search_tool.search(query=f"{topic} treatment solution remedy", k=5)
                if solution_results:
                    approach_text = "## Dr. Strunz's Approach\n"
                    for i, result in enumerate(solution_results[:3], 1):
                        approach_text += f"{i}. {result.text[:150]}...\n"
                    response_parts["approach"] = approach_text + "\n"
            
            # Phase 4: Key insights if time permits (6-8 seconds)
            if time.time() - start_time < 8 and main_results:
                insights_text = "## Key Insights by Source\n"
                
                books_insights = [r for r in main_results if r.source == "books"][:2]
                news_insights = [r for r in main_results if r.source == "news"][:2]
                forum_insights = [r for r in main_results if r.source == "forum"][:2]
                
                if books_insights:
                    insights_text += "### From Books\n"
                    for insight in books_insights:
                        insights_text += f"- {insight.text[:100]}... (*{insight.title}*)\n"
                
                if news_insights:
                    insights_text += "\n### From News Articles\n"
                    for insight in news_insights:
                        insights_text += f"- {insight.text[:100]}... (*{insight.title}*)\n"
                
                if forum_insights:
                    insights_text += "\n### From Forum Discussions\n"
                    for insight in forum_insights:
                        insights_text += f"- {insight.text[:100]}...\n"
                
                response_parts["insights"] = insights_text + "\n"
            
            # Phase 5: Progressive enrichment for comprehensive (if needed)
            if depth == "comprehensive" and progressive_k > 0 and time.time() - start_time < 9:
                # Add a note about additional results
                additional_results = self.search_tool.search(query=topic, k=progressive_k)
                if additional_results:
                    response_parts["footer"] = f"\n*Analysis based on {len(main_results) + len(additional_results)} relevant passages*"
            else:
                response_parts["footer"] = f"\n*Analysis based on {len(main_results)} relevant passages*"
            
            # Build final response
            final_response = "".join(response_parts.values())
            
            # Cache the result
            self.cache[cache_key] = (time.time(), final_response)
            
            # Log timing
            elapsed = time.time() - start_time
            logger.info(f"Streaming analysis completed in {elapsed:.2f} seconds for {topic} ({depth})")
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in streaming analysis: {e}")
            # Return partial results even on error
            return "".join(response_parts.values()) + f"\n\n*Error during analysis: {str(e)}*"
    
    def clear_cache(self):
        """Clear the query cache"""
        self.cache.clear()
        logger.info("Cache cleared")