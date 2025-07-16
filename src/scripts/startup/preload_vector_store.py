#!/usr/bin/env python3
"""
Pre-load vector store singleton to improve first-request performance
"""
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preload_vector_store():
    """Pre-load the vector store singleton for better performance."""
    logger.info("Starting vector store preload...")
    start_time = time.time()
    
    try:
        # Check if FAISS indices exist
        faiss_dir = Path("data/faiss_indices")
        if not faiss_dir.exists():
            logger.warning("FAISS indices directory not found - skipping preload")
            return False
        
        # Import and create singleton
        from src.rag.search import get_vector_store_singleton, is_vector_store_loaded
        
        # Create singleton instance (will load on first access)
        vector_store = get_vector_store_singleton()
        
        if is_vector_store_loaded():
            load_time = time.time() - start_time
            logger.info(f"Vector store preloaded successfully in {load_time:.2f}s")
            logger.info(f"Documents loaded: {len(vector_store.documents) if hasattr(vector_store, 'documents') else 'unknown'}")
            return True
        else:
            logger.warning("Vector store preload failed - no index loaded")
            return False
            
    except Exception as e:
        load_time = time.time() - start_time
        logger.error(f"Vector store preload failed after {load_time:.2f}s: {e}")
        return False

if __name__ == "__main__":
    preload_vector_store()