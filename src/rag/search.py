"""
Knowledge searcher module for the MCP server
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from .vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)

# Global singleton instance for vector store
_vector_store_instance = None
_vector_store_lock = None


@dataclass
class SearchResult:
    """Search result with metadata."""
    text: str
    score: float
    source: str
    title: str
    metadata: Dict


def is_vector_store_loaded() -> bool:
    """Check if vector store singleton is already loaded."""
    global _vector_store_instance
    return _vector_store_instance is not None and hasattr(_vector_store_instance, 'index') and _vector_store_instance.index is not None


def get_vector_store_singleton(index_path: str = "data/faiss_indices/combined") -> FAISSVectorStore:
    """Get or create the global vector store singleton."""
    global _vector_store_instance, _vector_store_lock
    
    if _vector_store_instance is None:
        import threading
        
        # Initialize lock if not exists
        if _vector_store_lock is None:
            _vector_store_lock = threading.Lock()
        
        # Double-check locking pattern
        with _vector_store_lock:
            if _vector_store_instance is None:
                logger.info("Creating singleton vector store instance...")
                _vector_store_instance = FAISSVectorStore(index_path=index_path)
                
                # Try to load existing index
                if _vector_store_instance.load_index():
                    logger.info(f"Singleton vector store loaded with {len(_vector_store_instance.documents)} documents")
                else:
                    logger.warning("No existing index found - search capabilities will be limited")
    
    return _vector_store_instance


class KnowledgeSearcher:
    """Search interface for the knowledge base."""
    
    def __init__(self, index_path: str = "data/faiss_indices/combined"):
        """Initialize the searcher with the singleton vector store."""
        self.vector_store = get_vector_store_singleton(index_path)
        logger.info("KnowledgeSearcher initialized with singleton vector store")
    
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