"""
True SSE streaming implementation with progressive updates
Sends partial results every 2 seconds to prevent MCP timeouts
"""

import logging
import asyncio
import json
import time
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SSEProgressiveStreamer:
    """Handles progressive SSE streaming for long-running operations"""
    
    def __init__(self, search_tool):
        """Initialize with reference to the search tool"""
        self.search_tool = search_tool
        self.update_interval = 2.0  # Send update every 2 seconds
        self.max_time = 9.0  # Keep under 10 second MCP limit
        
    async def stream_health_analysis(
        self,
        topic: str,
        depth: str = "moderate"
    ) -> AsyncGenerator[str, None]:
        """
        Stream health topic analysis with progressive updates
        Yields SSE-formatted events every 2 seconds
        """
        start_time = time.time()
        
        # Initial response structure
        result = {
            "type": "progress",
            "status": "started",
            "topic": topic,
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
            "content": f"# Analyzing: {topic}\n\nStarting comprehensive analysis...\n"
        }
        
        # Send initial event
        yield self._format_sse_event("progress", result)
        
        # Phase 1: Overview (0-2 seconds)
        await asyncio.sleep(0.1)  # Small delay for realistic feeling
        
        try:
            # Search for main topic
            main_results = self.search_tool.search(query=topic, k=10)
            
            if main_results:
                overview = f"## Overview\n{main_results[0].text[:300]}...\n"
                overview += f"*Source: {main_results[0].source} - {main_results[0].title}*\n\n"
                
                result.update({
                    "status": "overview_complete",
                    "content": result["content"] + overview,
                    "progress": 25
                })
                
                if time.time() - start_time < self.update_interval:
                    await asyncio.sleep(self.update_interval - (time.time() - start_time))
                
                yield self._format_sse_event("progress", result)
            
            # Phase 2: Causes (2-4 seconds)
            if time.time() - start_time < self.max_time:
                cause_results = self.search_tool.search(query=f"{topic} causes reasons", k=5)
                
                if cause_results:
                    causes = "## Causes & Mechanisms\n"
                    for i, r in enumerate(cause_results[:3], 1):
                        causes += f"{i}. {r.text[:150]}...\n"
                    
                    result.update({
                        "status": "causes_complete",
                        "content": result["content"] + causes + "\n",
                        "progress": 50
                    })
                    
                    elapsed = time.time() - start_time
                    if elapsed < self.update_interval * 2:
                        await asyncio.sleep((self.update_interval * 2) - elapsed)
                    
                    yield self._format_sse_event("progress", result)
            
            # Phase 3: Solutions (4-6 seconds)
            if time.time() - start_time < self.max_time:
                solution_results = self.search_tool.search(query=f"{topic} treatment solution", k=5)
                
                if solution_results:
                    solutions = "## Dr. Strunz's Approach\n"
                    for i, r in enumerate(solution_results[:3], 1):
                        solutions += f"{i}. {r.text[:150]}...\n"
                    
                    result.update({
                        "status": "solutions_complete",
                        "content": result["content"] + solutions + "\n",
                        "progress": 75
                    })
                    
                    elapsed = time.time() - start_time
                    if elapsed < self.update_interval * 3:
                        await asyncio.sleep((self.update_interval * 3) - elapsed)
                    
                    yield self._format_sse_event("progress", result)
            
            # Phase 4: Key Insights (6-8 seconds)
            if time.time() - start_time < self.max_time and depth == "comprehensive":
                insights = "## Key Insights\n"
                
                # Group by source
                books = [r for r in main_results if r.source == "books"][:2]
                news = [r for r in main_results if r.source == "news"][:2]
                
                if books:
                    insights += "### From Books\n"
                    for b in books:
                        insights += f"- {b.text[:100]}... (*{b.title}*)\n"
                
                if news:
                    insights += "\n### From News\n"
                    for n in news:
                        insights += f"- {n.text[:100]}... (*{n.title}*)\n"
                
                result.update({
                    "status": "insights_complete",
                    "content": result["content"] + insights + "\n",
                    "progress": 90
                })
                
                yield self._format_sse_event("progress", result)
            
            # Final result
            footer = f"\n*Analysis complete. Based on {len(main_results)} sources.*"
            result.update({
                "type": "complete",
                "status": "completed",
                "content": result["content"] + footer,
                "progress": 100,
                "elapsed_time": time.time() - start_time
            })
            
            yield self._format_sse_event("complete", result)
            
        except Exception as e:
            logger.error(f"Error during streaming analysis: {e}")
            error_result = {
                "type": "error",
                "status": "error",
                "error": str(e),
                "content": result.get("content", "") + f"\n\n*Error: {str(e)}*",
                "elapsed_time": time.time() - start_time
            }
            yield self._format_sse_event("error", error_result)
    
    def _format_sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format data as SSE event"""
        event = f"event: {event_type}\n"
        event += f"data: {json.dumps(data)}\n\n"
        return event
    
    async def stream_supplement_analysis(
        self,
        supplements: list[str]
    ) -> AsyncGenerator[str, None]:
        """Stream supplement stack analysis with progressive updates"""
        start_time = time.time()
        
        result = {
            "type": "progress",
            "status": "started",
            "supplements": supplements,
            "timestamp": datetime.now().isoformat(),
            "content": f"# Analyzing Supplement Stack\n\nSupplements: {', '.join(supplements)}\n\n"
        }
        
        yield self._format_sse_event("progress", result)
        
        # Progressive analysis of each supplement
        for idx, supplement in enumerate(supplements):
            if time.time() - start_time > self.max_time:
                break
                
            results = self.search_tool.search(query=supplement, k=3)
            if results:
                supp_info = f"## {supplement}\n"
                supp_info += f"{results[0].text[:200]}...\n"
                supp_info += f"*Source: {results[0].source}*\n\n"
                
                result.update({
                    "status": f"analyzing_{idx+1}_of_{len(supplements)}",
                    "content": result["content"] + supp_info,
                    "progress": int((idx + 1) / len(supplements) * 70)
                })
                
                yield self._format_sse_event("progress", result)
                
                # Small delay between supplements
                await asyncio.sleep(0.5)
        
        # Check interactions
        if len(supplements) > 1 and time.time() - start_time < self.max_time:
            combo_query = " ".join(supplements) + " interaction"
            combo_results = self.search_tool.search(query=combo_query, k=5)
            
            if combo_results:
                interactions = "## Interaction Analysis\n"
                for r in combo_results[:2]:
                    if any(word in r.text.lower() for word in ['interaction', 'combine', 'together']):
                        interactions += f"- {r.text[:150]}...\n"
                
                result.update({
                    "status": "interactions_complete",
                    "content": result["content"] + interactions + "\n",
                    "progress": 90
                })
                
                yield self._format_sse_event("progress", result)
        
        # Final result
        result.update({
            "type": "complete",
            "status": "completed",
            "content": result["content"] + "\n*Analysis complete.*",
            "progress": 100,
            "elapsed_time": time.time() - start_time
        })
        
        yield self._format_sse_event("complete", result)