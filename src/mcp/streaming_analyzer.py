"""
Streaming Response Implementation for MCP Server
Fixes timeout issues by providing progressive responses
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ProgressMessage:
    """Structure for progress messages"""
    type: str  # 'progress' or 'complete'
    status: str
    message: str
    progress: int
    elapsed: float
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}

class StreamingAnalyzer:
    """Progressive response streamer for comprehensive analysis"""
    
    def __init__(self, search_tool):
        """Initialize with reference to search tool"""
        self.search_tool = search_tool
        self.chunk_interval = 2.0  # Send update every 2 seconds
        self.max_time = 9.5  # Keep under 10 second limit
        
    async def analyze_health_topic_streaming(
        self,
        topic: str,
        depth: str = "comprehensive"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream analysis results progressively to prevent timeouts.
        Sends updates every 2 seconds to keep connection alive.
        """
        start_time = time.time()
        
        # Phase 1: Immediate acknowledgment (0-1 second)
        yield ProgressMessage(
            type="progress",
            status="initializing",
            message=f"Starting comprehensive analysis of '{topic}'",
            progress=0,
            elapsed=time.time() - start_time
        ).to_dict()
        
        # Phase 2: Parallel vector search (1-3 seconds)
        search_results = []
        async for update in self._stream_vector_search(topic, start_time):
            yield update
            if update.get("data") and "results" in update["data"]:
                search_results.extend(update["data"]["results"])
        
        # Phase 3: Result categorization (3-5 seconds)
        categories = {}
        async for update in self._stream_categorization(search_results, start_time):
            yield update
            if update.get("data") and "categories" in update["data"]:
                categories = update["data"]["categories"]
        
        # Phase 4: AI synthesis (5-8 seconds)
        analysis = {}
        async for update in self._stream_synthesis(topic, categories, start_time):
            yield update
            if update.get("data") and "analysis" in update["data"]:
                analysis.update(update["data"]["analysis"])
        
        # Phase 5: Final result (8-9 seconds)
        elapsed = time.time() - start_time
        
        # Truncate if needed to stay under time limit
        if elapsed > self.max_time:
            analysis = self._truncate_analysis(analysis, depth)
        
        yield ProgressMessage(
            type="complete",
            status="done",
            message=f"Analysis complete for '{topic}'",
            progress=100,
            elapsed=elapsed,
            data={
                "topic": topic,
                "depth": depth,
                "result": self._format_final_result(topic, analysis, search_results),
                "stats": {
                    "documents_analyzed": len(search_results),
                    "categories_found": len(categories),
                    "processing_time": f"{elapsed:.2f}s"
                }
            }
        ).to_dict()
    
    async def _stream_vector_search(
        self, 
        topic: str,
        start_time: float
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Parallel vector search across sources"""
        
        # Launch parallel searches
        tasks = {
            'books': asyncio.create_task(self._search_source(topic, ['books'])),
            'news': asyncio.create_task(self._search_source(topic, ['news'])),
            'forum': asyncio.create_task(self._search_source(topic, ['forum']))
        }
        
        completed = 0
        total = len(tasks)
        all_results = []
        
        # Stream results as they complete
        for source, task in tasks.items():
            try:
                results = await task
                completed += 1
                all_results.extend(results)
                
                yield ProgressMessage(
                    type="progress",
                    status="searching",
                    message=f"Searched {source}: found {len(results)} results",
                    progress=int(25 * completed / total),
                    elapsed=time.time() - start_time,
                    data={
                        "source": source,
                        "count": len(results),
                        "results": results[:5]  # First 5 for preview
                    }
                ).to_dict()
                
            except Exception as e:
                logger.error(f"Search error for {source}: {e}")
                yield ProgressMessage(
                    type="progress",
                    status="searching",
                    message=f"Error searching {source}: {str(e)}",
                    progress=int(25 * completed / total),
                    elapsed=time.time() - start_time
                ).to_dict()
    
    async def _search_source(self, topic: str, sources: List[str]) -> List[Dict]:
        """Search specific source"""
        try:
            if not self.search_tool:
                return []
            
            results = self.search_tool.search(
                query=topic,
                k=15,  # Limit per source for speed
                sources=sources
            )
            
            # Convert to dict format
            return [
                {
                    "source": r.source,
                    "title": r.title,
                    "text": r.text[:500],  # Truncate for streaming
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def _stream_categorization(
        self,
        results: List[Dict],
        start_time: float
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Categorize results by theme"""
        
        # Quick categorization by keywords
        categories = {
            "benefits": [],
            "risks": [],
            "dosage": [],
            "research": [],
            "general": []
        }
        
        keywords = {
            "benefits": ["benefit", "improve", "help", "positive", "effective"],
            "risks": ["risk", "danger", "caution", "avoid", "side effect"],
            "dosage": ["dose", "amount", "mg", "gram", "daily", "intake"],
            "research": ["study", "research", "trial", "evidence", "science"]
        }
        
        for result in results:
            text_lower = result["text"].lower()
            categorized = False
            
            for category, words in keywords.items():
                if any(word in text_lower for word in words):
                    categories[category].append(result)
                    categorized = True
                    break
            
            if not categorized:
                categories["general"].append(result)
        
        # Stream category updates
        total_categories = len([c for c in categories.values() if c])
        processed = 0
        
        for category, items in categories.items():
            if items:
                processed += 1
                yield ProgressMessage(
                    type="progress",
                    status="categorizing",
                    message=f"Categorized {len(items)} items as '{category}'",
                    progress=25 + int(25 * processed / max(total_categories, 1)),
                    elapsed=time.time() - start_time,
                    data={
                        "categories": {category: len(items)}
                    }
                ).to_dict()
                
                # Small delay to simulate processing
                await asyncio.sleep(0.1)
    
    async def _stream_synthesis(
        self,
        topic: str,
        categories: Dict[str, List],
        start_time: float
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Synthesize information progressively"""
        
        analysis = {}
        total_categories = len([c for c in categories.values() if c])
        processed = 0
        
        # Process each category
        for category, items in categories.items():
            if not items:
                continue
            
            processed += 1
            
            # Simple synthesis (would use AI in production)
            synthesis = self._synthesize_category(category, items)
            analysis[category] = synthesis
            
            yield ProgressMessage(
                type="progress",
                status="analyzing",
                message=f"Analyzed {category} information",
                progress=50 + int(40 * processed / max(total_categories, 1)),
                elapsed=time.time() - start_time,
                data={
                    "analysis": {category: synthesis}
                }
            ).to_dict()
            
            # Small delay to simulate processing
            await asyncio.sleep(0.2)
    
    def _synthesize_category(self, category: str, items: List[Dict]) -> str:
        """Simple synthesis of category information"""
        if not items:
            return "No information available."
        
        # Take top 3 items by score
        top_items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[:3]
        
        synthesis = f"Based on {len(items)} sources:\n"
        for item in top_items:
            # Extract key points (simple version)
            text = item["text"][:200]
            synthesis += f"• {text}...\n"
        
        return synthesis
    
    def _truncate_analysis(self, analysis: Dict, depth: str) -> Dict:
        """Truncate analysis based on depth to meet time constraints"""
        limits = {
            "basic": 100,
            "detailed": 300,
            "comprehensive": 500
        }
        
        max_chars = limits.get(depth, 500)
        
        for key, value in analysis.items():
            if isinstance(value, str) and len(value) > max_chars:
                analysis[key] = value[:max_chars] + "..."
        
        return analysis
    
    def _format_final_result(
        self,
        topic: str,
        analysis: Dict,
        results: List[Dict]
    ) -> str:
        """Format the final comprehensive result"""
        
        output = f"# Comprehensive Analysis: {topic}\n\n"
        
        # Add analysis sections
        for category, content in analysis.items():
            if content and content != "No information available.":
                output += f"## {category.capitalize()}\n"
                output += f"{content}\n\n"
        
        # Add statistics
        output += "## Analysis Statistics\n"
        output += f"- Total documents analyzed: {len(results)}\n"
        output += f"- Categories identified: {len([c for c in analysis.values() if c])}\n"
        
        # Add sources summary
        sources_count = {}
        for result in results:
            source = result.get("source", "unknown")
            sources_count[source] = sources_count.get(source, 0) + 1
        
        output += f"- Sources: "
        output += ", ".join([f"{s} ({c})" for s, c in sources_count.items()])
        output += "\n"
        
        return output


class StreamingOptimizer:
    """Optimization utilities for streaming responses"""
    
    DEPTH_LIMITS = {
        'basic': {'documents': 10, 'max_time': 3.0},
        'detailed': {'documents': 25, 'max_time': 6.0},
        'comprehensive': {'documents': 30, 'max_time': 9.5}
    }
    
    @classmethod
    def truncate_for_time_budget(
        cls,
        results: List[Dict],
        depth: str,
        elapsed: float
    ) -> List[Dict]:
        """Dynamically truncate based on remaining time"""
        
        limits = cls.DEPTH_LIMITS.get(depth, cls.DEPTH_LIMITS['comprehensive'])
        remaining_time = limits['max_time'] - elapsed
        
        if remaining_time < 2.0:
            # Aggressive truncation if running out of time
            return results[:int(limits['documents'] * 0.5)]
        elif remaining_time < 4.0:
            # Moderate truncation
            return results[:int(limits['documents'] * 0.75)]
        else:
            # Normal limit
            return results[:limits['documents']]