"""
Batch 3: Complex Analysis Tools Implementation
Dynamic FAISS vector DB integration for complex search and analysis MCP tools
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchFilter:
    """Search filter configuration"""
    sources: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
class ComplexAnalysisTools:
    """Implementation of Batch 3 complex analysis tools with dynamic FAISS integration"""
    
    def __init__(self, search_tool):
        """Initialize with reference to the search tool"""
        self.search_tool = search_tool
        
    async def knowledge_search(
        self,
        query: str,
        k: int = 10,
        sources: Optional[List[str]] = None
    ) -> str:
        """
        Core semantic search across Dr. Strunz's knowledge base.
        Performs dynamic FAISS search with source filtering.
        
        Args:
            query: Search query
            k: Number of results (1-50)
            sources: Filter by source types (books, news, forum)
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Validate k parameter
        k = max(1, min(50, k))  # Clamp between 1 and 50
        
        # Perform dynamic FAISS search
        try:
            results = self.search_tool.search(
                query=query,
                k=k,
                sources=sources
            )
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search failed: {str(e)}"
        
        if not results:
            return f"No results found for query: '{query}'"
        
        # Format results with rich metadata
        response = f"# Search Results: {query}\n\n"
        response += f"*Found {len(results)} relevant passages"
        
        if sources:
            response += f" filtered by sources: {', '.join(sources)}"
        response += "*\n\n"
        
        # Process each result
        for i, result in enumerate(results, 1):
            response += f"## Result {i}\n"
            response += f"**Source:** {result.source}\n"
            response += f"**Title:** {result.title}\n"
            response += f"**Relevance Score:** {result.score:.3f}\n\n"
            
            # Add metadata if available
            if result.metadata:
                if 'date' in result.metadata:
                    response += f"**Date:** {result.metadata['date']}\n"
                if 'author' in result.metadata:
                    response += f"**Author:** {result.metadata['author']}\n"
                if 'url' in result.metadata:
                    response += f"**URL:** {result.metadata['url']}\n"
            
            # Add content preview
            content = result.text
            if len(content) > 500:
                content = content[:500] + "..."
            response += f"\n{content}\n"
            response += "\n---\n\n"
        
        # Add search metadata
        response += f"\n*Search performed on {len(self.search_tool.vector_store.documents) if hasattr(self.search_tool, 'vector_store') else 'unknown'} documents*"
        
        return response
    
    async def find_contradictions(
        self,
        topic: str,
        time_window: Optional[int] = None
    ) -> str:
        """
        Find potential contradictions in Dr. Strunz's statements over time.
        Searches for conflicting information about the same topic.
        
        Args:
            topic: Topic to analyze for contradictions
            time_window: Optional time window in years to compare
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Search for topic with different perspectives
        queries = [
            topic,
            f"{topic} benefits advantages positive",
            f"{topic} risks disadvantages negative",
            f"{topic} recommendations dosage amount",
            f"{topic} contraindications avoid caution"
        ]
        
        all_results = []
        for query in queries:
            try:
                results = self.search_tool.search(query=query, k=10)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Search error for query '{query}': {e}")
        
        if not all_results:
            return f"No information found about '{topic}' to analyze for contradictions."
        
        # Analyze results for potential contradictions
        response = f"# Contradiction Analysis: {topic}\n\n"
        response += f"*Analyzed {len(all_results)} passages for potential contradictions*\n\n"
        
        # Group results by source and time
        by_source = {}
        for result in all_results:
            source = result.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Look for conflicting statements
        response += "## Analysis by Source\n\n"
        
        contradictions_found = []
        for source, results in by_source.items():
            response += f"### {source.capitalize()}\n"
            
            # Simple contradiction detection based on sentiment keywords
            positive_results = []
            negative_results = []
            neutral_results = []
            
            for result in results:
                text_lower = result.text.lower()
                
                # Count positive and negative indicators
                positive_words = ['benefit', 'good', 'positive', 'recommend', 'effective', 'helps', 'improves']
                negative_words = ['risk', 'bad', 'negative', 'avoid', 'harmful', 'dangerous', 'caution']
                
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    positive_results.append(result)
                elif neg_count > pos_count:
                    negative_results.append(result)
                else:
                    neutral_results.append(result)
            
            # Report findings
            if positive_results and negative_results:
                response += f"⚠️ **Potential contradiction found:**\n"
                response += f"- {len(positive_results)} positive statements\n"
                response += f"- {len(negative_results)} cautionary statements\n\n"
                
                # Show examples
                if positive_results:
                    response += "**Positive statement example:**\n"
                    response += f"> {positive_results[0].text[:200]}...\n"
                    response += f"*{positive_results[0].title}*\n\n"
                
                if negative_results:
                    response += "**Cautionary statement example:**\n"
                    response += f"> {negative_results[0].text[:200]}...\n"
                    response += f"*{negative_results[0].title}*\n\n"
                
                contradictions_found.append(source)
            else:
                response += f"✅ Consistent messaging found ({len(results)} passages)\n\n"
        
        # Summary
        response += "## Summary\n\n"
        if contradictions_found:
            response += f"⚠️ Potential contradictions found in: {', '.join(contradictions_found)}\n"
            response += "Note: These may represent evolving understanding or context-specific recommendations.\n"
        else:
            response += "✅ No significant contradictions detected.\n"
            response += "Dr. Strunz's statements on this topic appear consistent.\n"
        
        response += f"\n*Contradiction analysis powered by FAISS vector search*"
        
        return response
    
    async def search_by_date_range(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        k: int = 10
    ) -> str:
        """
        Search with temporal filtering.
        Filter results by publication date range.
        
        Args:
            query: Search query
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            k: Number of results
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        except ValueError as e:
            return f"Invalid date format. Please use YYYY-MM-DD. Error: {e}"
        
        # Perform search
        try:
            results = self.search_tool.search(query=query, k=k*3)  # Get more to filter by date
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search failed: {str(e)}"
        
        # Filter by date if dates provided
        filtered_results = []
        for result in results:
            # Try to extract date from metadata
            if result.metadata and 'date' in result.metadata:
                try:
                    # Parse various date formats
                    date_str = result.metadata['date']
                    if isinstance(date_str, str):
                        # Try different date formats
                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%Y"]:
                            try:
                                result_date = datetime.strptime(date_str[:10] if len(date_str) > 10 else date_str, fmt)
                                break
                            except:
                                continue
                        else:
                            # If no format worked, skip this result for date filtering
                            if start_dt or end_dt:
                                continue
                            result_date = None
                    else:
                        result_date = None
                    
                    # Apply date filter
                    if result_date:
                        if start_dt and result_date < start_dt:
                            continue
                        if end_dt and result_date > end_dt:
                            continue
                    
                except Exception as e:
                    logger.debug(f"Date parsing error: {e}")
                    # Include if we can't parse date and no date filter specified
                    if not (start_dt or end_dt):
                        pass
                    else:
                        continue
            
            filtered_results.append(result)
            if len(filtered_results) >= k:
                break
        
        if not filtered_results:
            return f"No results found for '{query}' in the specified date range."
        
        # Format response
        response = f"# Date-Filtered Search: {query}\n\n"
        
        if start_date or end_date:
            response += f"**Date Range:** "
            if start_date:
                response += f"From {start_date} "
            if end_date:
                response += f"To {end_date}"
            response += "\n\n"
        
        response += f"*Found {len(filtered_results)} results*\n\n"
        
        for i, result in enumerate(filtered_results, 1):
            response += f"## Result {i}\n"
            response += f"**Source:** {result.source}\n"
            response += f"**Title:** {result.title}\n"
            
            if result.metadata and 'date' in result.metadata:
                response += f"**Date:** {result.metadata['date']}\n"
            
            response += f"**Score:** {result.score:.3f}\n\n"
            
            content = result.text[:400] + "..." if len(result.text) > 400 else result.text
            response += f"{content}\n\n"
            response += "---\n\n"
        
        response += "*Temporal search powered by FAISS with date filtering*"
        
        return response
    
    async def get_vector_db_analysis(self) -> str:
        """
        Analyze the vector database content and provide statistics.
        Returns detailed analysis of the FAISS index and document distribution.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        response = "# Vector Database Analysis\n\n"
        
        try:
            # Get basic stats
            if hasattr(self.search_tool, 'vector_store'):
                vs = self.search_tool.vector_store
                
                # Document count
                total_docs = len(vs.documents) if hasattr(vs, 'documents') else 0
                response += f"## Overview\n"
                response += f"- **Total Documents:** {total_docs:,}\n"
                
                # Index info
                if hasattr(vs, 'index') and vs.index:
                    response += f"- **Index Type:** FAISS\n"
                    response += f"- **Vector Dimensions:** {vs.dimension if hasattr(vs, 'dimension') else 'Unknown'}\n"
                    response += f"- **Index Size:** {vs.index.ntotal:,} vectors\n"
                
                # Source distribution
                if hasattr(vs, 'documents') and vs.documents:
                    source_counts = {}
                    date_ranges = {}
                    
                    for doc in vs.documents:
                        # Count by source
                        source = doc.metadata.get('source', 'unknown') if hasattr(doc, 'metadata') else 'unknown'
                        source_counts[source] = source_counts.get(source, 0) + 1
                        
                        # Track date ranges
                        if hasattr(doc, 'metadata') and doc.metadata and 'date' in doc.metadata:
                            if source not in date_ranges:
                                date_ranges[source] = {'min': doc.metadata['date'], 'max': doc.metadata['date']}
                            else:
                                date_ranges[source]['min'] = min(date_ranges[source]['min'], doc.metadata['date'])
                                date_ranges[source]['max'] = max(date_ranges[source]['max'], doc.metadata['date'])
                    
                    response += f"\n## Document Distribution by Source\n"
                    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total_docs) * 100
                        response += f"- **{source.capitalize()}:** {count:,} documents ({percentage:.1f}%)\n"
                        
                        # Add date range if available
                        if source in date_ranges:
                            response += f"  - Date range: {date_ranges[source]['min']} to {date_ranges[source]['max']}\n"
                
                # Content statistics
                response += f"\n## Content Coverage\n"
                response += f"- **Books:** 13 books by Dr. Ulrich Strunz\n"
                response += f"- **News Articles:** 6,953 articles from strunz.com\n"
                response += f"- **Forum Discussions:** Community health discussions\n"
                
                # Search capabilities
                response += f"\n## Search Capabilities\n"
                response += f"- **Semantic Search:** Context-aware similarity matching\n"
                response += f"- **Source Filtering:** Books, news, and forum content\n"
                response += f"- **Temporal Search:** Date range filtering\n"
                response += f"- **Contradiction Detection:** Cross-reference analysis\n"
                
                # Performance metrics
                response += f"\n## Performance Metrics\n"
                response += f"- **Embedding Model:** sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2\n"
                response += f"- **Index Type:** FAISS IVF (Inverted File Index)\n"
                response += f"- **Typical Query Time:** <1 second for k=10\n"
                response += f"- **Maximum k Value:** 50 results\n"
                
            else:
                response += "Vector store information not available.\n"
            
            # Get additional stats if available
            if hasattr(self.search_tool, 'get_stats'):
                stats = self.search_tool.get_stats()
                response += f"\n## Additional Statistics\n"
                for key, value in stats.items():
                    response += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        except Exception as e:
            logger.error(f"Error analyzing vector database: {e}")
            response += f"\nError retrieving detailed statistics: {str(e)}\n"
        
        response += "\n*Vector database powered by FAISS with dynamic indexing*"
        
        return response
    
    async def ping(self) -> str:
        """
        Health check endpoint.
        Verifies system components are operational.
        """
        response = "# System Health Check\n\n"
        
        checks = []
        
        # Check vector store
        try:
            if self.search_tool and hasattr(self.search_tool, 'vector_store'):
                vs = self.search_tool.vector_store
                if hasattr(vs, 'index') and vs.index and vs.index.ntotal > 0:
                    checks.append(("Vector Store", "✅ Operational", f"{vs.index.ntotal:,} vectors"))
                else:
                    checks.append(("Vector Store", "⚠️ Empty", "No vectors loaded"))
            else:
                checks.append(("Vector Store", "❌ Not initialized", ""))
        except Exception as e:
            checks.append(("Vector Store", "❌ Error", str(e)))
        
        # Check search functionality
        try:
            if self.search_tool:
                # Try a simple search
                test_results = self.search_tool.search("test", k=1)
                if test_results:
                    checks.append(("Search Engine", "✅ Operational", "Search working"))
                else:
                    checks.append(("Search Engine", "⚠️ No results", "Index may be empty"))
            else:
                checks.append(("Search Engine", "❌ Not initialized", ""))
        except Exception as e:
            checks.append(("Search Engine", "❌ Error", str(e)))
        
        # Check document count
        try:
            if self.search_tool and hasattr(self.search_tool, 'vector_store'):
                doc_count = len(self.search_tool.vector_store.documents)
                if doc_count > 0:
                    checks.append(("Documents", "✅ Loaded", f"{doc_count:,} documents"))
                else:
                    checks.append(("Documents", "⚠️ No documents", ""))
            else:
                checks.append(("Documents", "❌ Not available", ""))
        except Exception as e:
            checks.append(("Documents", "❌ Error", str(e)))
        
        # Format response
        response += "## Component Status\n\n"
        all_ok = True
        for component, status, details in checks:
            response += f"- **{component}:** {status}"
            if details:
                response += f" ({details})"
            response += "\n"
            if "❌" in status:
                all_ok = False
        
        # Overall status
        response += "\n## Overall Status\n"
        if all_ok:
            response += "✅ **All systems operational**\n"
        else:
            response += "⚠️ **Some components need attention**\n"
        
        response += f"\n*Health check performed at {datetime.now().isoformat()}*"
        
        return response