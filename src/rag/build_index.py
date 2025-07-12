#!/usr/bin/env python3
"""
Build FAISS Vector Index - Creates vector index from processed HTML content
"""

import logging
import json
from pathlib import Path
from typing import List, Dict
from vector_store import FAISSVectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_processed_documents(processed_dir: str = "data/processed") -> List[Dict]:
    """Load all processed documents from JSON files."""
    processed_path = Path(processed_dir)
    all_documents = []
    
    # Load forum documents
    forum_file = processed_path / "forum_processed.json"
    if forum_file.exists():
        logger.info(f"Loading forum documents from {forum_file}")
        with open(forum_file, 'r', encoding='utf-8') as f:
            forum_data = json.load(f)
        
        # Extract chunks from forum documents
        for doc in forum_data:
            for chunk in doc.get('chunks', []):
                all_documents.append({
                    'id': chunk['id'],
                    'content': chunk['content'],
                    'metadata': {
                        **chunk['metadata'],
                        'source_type': 'forum',
                        'filename': doc['filename'],
                        'url': doc.get('url', ''),
                        'processed_at': doc['processed_at']
                    }
                })
        
        logger.info(f"Loaded {len([d for d in all_documents if d['metadata']['source_type'] == 'forum'])} forum chunks")
    
    # Load news documents
    news_file = processed_path / "news_processed.json"
    if news_file.exists():
        logger.info(f"Loading news documents from {news_file}")
        with open(news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # Extract chunks from news documents
        for doc in news_data:
            for chunk in doc.get('chunks', []):
                all_documents.append({
                    'id': chunk['id'],
                    'content': chunk['content'],
                    'metadata': {
                        **chunk['metadata'],
                        'source_type': 'news',
                        'filename': doc['filename'],
                        'url': doc.get('url', ''),
                        'processed_at': doc['processed_at']
                    }
                })
        
        logger.info(f"Loaded {len([d for d in all_documents if d['metadata']['source_type'] == 'news'])} news chunks")
    
    logger.info(f"Total documents loaded: {len(all_documents)}")
    return all_documents


def build_vector_index(documents: List[Dict], clear_existing: bool = False) -> FAISSVectorStore:
    """Build the FAISS vector index from documents."""
    logger.info("Initializing FAISS vector store...")
    
    # Initialize vector store
    vector_store = FAISSVectorStore(
        index_path="data/processed/faiss_index",
        embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        dimension=384
    )
    
    # Clear existing index if requested
    if clear_existing:
        logger.info("Clearing existing index...")
        vector_store.clear()
    
    # Check if we already have documents
    existing_stats = vector_store.get_stats()
    if existing_stats['total_documents'] > 0:
        logger.info(f"Found existing index with {existing_stats['total_documents']} documents")
        
        # Ask user if they want to rebuild or add to existing
        response = input("Existing index found. (r)ebuild from scratch or (a)dd new documents? [r/a]: ")
        if response.lower() == 'r':
            logger.info("Rebuilding index from scratch...")
            vector_store.clear()
        elif response.lower() == 'a':
            logger.info("Adding to existing index...")
        else:
            logger.info("Cancelled.")
            return vector_store
    
    # Add documents in batches
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    logger.info(f"Adding {len(documents)} documents in {total_batches} batches...")
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
        
        try:
            added_count = vector_store.add_documents(batch)
            logger.info(f"Added {added_count} documents from batch {batch_num}")
        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {e}")
            continue
    
    # Final statistics
    final_stats = vector_store.get_stats()
    logger.info(f"Vector index build complete!")
    logger.info(f"Final stats: {final_stats}")
    
    return vector_store


def test_search(vector_store: FAISSVectorStore):
    """Test the search functionality."""
    logger.info("Testing search functionality...")
    
    test_queries = [
        "Vitamin D Dosierung",
        "Omega 3 Fettsäuren",
        "Immunsystem stärken",
        "Bluttuning Werte",
        "Ernährung Sport"
    ]
    
    for query in test_queries:
        logger.info(f"\n--- Testing query: '{query}' ---")
        
        try:
            results = vector_store.search(query, k=3)
            
            if results:
                for i, (doc, score) in enumerate(results, 1):
                    logger.info(f"Result {i} (score: {score:.3f}):")
                    logger.info(f"  Category: {doc.metadata.get('category', 'Unknown')}")
                    logger.info(f"  Source: {doc.metadata.get('source_type', 'Unknown')}")
                    logger.info(f"  Content: {doc.content[:200]}...")
                    if 'url' in doc.metadata:
                        logger.info(f"  URL: {doc.metadata['url']}")
            else:
                logger.warning(f"No results found for query: {query}")
                
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")


def main():
    """Main function."""
    print("=== FAISS Vector Index Builder ===")
    print("Building vector index from processed HTML content...")
    print()
    
    try:
        # Load processed documents
        documents = load_processed_documents()
        
        if not documents:
            logger.error("No processed documents found!")
            logger.info("Please run the HTML processor first: python src/rag/html_processor.py")
            return
        
        # Build index
        vector_store = build_vector_index(documents)
        
        # Test search functionality
        if vector_store.get_stats()['total_documents'] > 0:
            test_search(vector_store)
        
        print(f"\n✅ Vector index built successfully!")
        print(f"Index location: data/processed/faiss_index/")
        print(f"Total documents: {vector_store.get_stats()['total_documents']}")
        
    except Exception as e:
        logger.error(f"Error building index: {e}")
        print("\n❌ Failed to build vector index")


if __name__ == "__main__":
    main()