"""
Knowledge searcher module for the MCP server
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from .vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with metadata."""
    text: str
    score: float
    source: str
    title: str
    metadata: Dict


class KnowledgeSearcher:
    """Search interface for the knowledge base."""
    
    def __init__(self, index_path: str = "data/faiss_indices/combined"):
        """Initialize the searcher with the vector store."""
        self.vector_store = FAISSVectorStore(index_path=index_path)
        
        # Try to load existing index
        if self.vector_store.load_index():
            logger.info(f"Loaded index with {len(self.vector_store.documents)} documents")
        else:
            logger.warning("No existing index found - search capabilities will be limited")
    
    def search(self, query: str, k: int = 10, sources: Optional[List[str]] = None) -> List[SearchResult]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            k: Number of results to return
            sources: Filter by source types (books, news, forum)
            
        Returns:
            List of search results
        """
        if not self.vector_store.index:
            logger.warning("No vector index available")
            return []
        
        # Build metadata filter
        filter_metadata = {}
        if sources:
            # For now, we'll filter results after retrieval
            pass
        
        # Search
        results = self.vector_store.search(query, k=k*2 if sources else k)  # Get more if filtering
        
        # Convert to SearchResult objects
        search_results = []
        for doc, score in results:
            # Extract source from metadata
            source = doc.metadata.get('source', 'unknown')
            
            # Filter by source if requested
            if sources and source not in sources:
                continue
            
            result = SearchResult(
                text=doc.content,
                score=score,
                source=source,
                title=doc.metadata.get('title', 'Untitled'),
                metadata=doc.metadata
            )
            search_results.append(result)
            
            if len(search_results) >= k:
                break
        
        return search_results
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        if not self.vector_store.index:
            return {"status": "No index loaded", "documents": 0}
        
        return {
            "status": "Ready",
            "documents": len(self.vector_store.documents),
            "index_size": self.vector_store.index.ntotal,
            "dimension": self.vector_store.dimension
        }