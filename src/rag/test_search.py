#!/usr/bin/env python3
"""
Test Search Functionality - Test the FAISS vector search with sample queries
"""

import logging
import sys
from pathlib import Path
from vector_store import FAISSVectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_search_functionality():
    """Test the search functionality with various queries."""
    
    print("=== FAISS Vector Search Test ===")
    print("Loading vector store...")
    
    try:
        # Initialize vector store
        vector_store = FAISSVectorStore(
            index_path="data/processed/faiss_index",
            embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            dimension=384
        )
        
        # Check if index exists and is loaded
        stats = vector_store.get_stats()
        print(f"Vector store stats: {stats}")
        
        if stats['total_documents'] == 0:
            print("❌ No documents in vector store!")
            print("Please run the index builder first: python src/rag/build_index.py")
            return
        
        print(f"✅ Loaded vector store with {stats['total_documents']} documents")
        print()
        
        # Test queries in German (Dr. Strunz content)
        test_queries = [
            "Vitamin D Dosierung",
            "Omega 3 Fettsäuren Wirkung",
            "Immunsystem stärken",
            "Bluttuning Laborwerte",
            "Ernährung für Sportler",
            "Magnesium Mangel Symptome",
            "Corona Virus Behandlung",
            "Eiweiß Protein Bedarf",
            "Keto Diät ketogen",
            "Fitness Training Muskelaufbau"
        ]
        
        print("Testing search with sample queries...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"--- Test {i}: '{query}' ---")
            
            try:
                # Search with default parameters
                results = vector_store.search(query, k=3)
                
                if results:
                    for j, (doc, score) in enumerate(results, 1):
                        print(f"Result {j} (score: {score:.3f}):")
                        print(f"  Category: {doc.metadata.get('category', 'Unknown')}")
                        print(f"  Source: {doc.metadata.get('source_type', doc.metadata.get('source_file', 'Unknown'))}")
                        
                        # Show content preview
                        content_preview = doc.content[:150].replace('\n', ' ')
                        print(f"  Content: {content_preview}...")
                        
                        # Show metadata if available
                        if 'url' in doc.metadata:
                            print(f"  URL: {doc.metadata['url']}")
                        
                        print()
                else:
                    print("  ❌ No results found")
                    
            except Exception as e:
                print(f"  ❌ Search error: {e}")
            
            print("-" * 60)
            print()
        
        # Test category filtering
        print("=== Testing Category Filtering ===")
        
        category_tests = [
            ("Vitamin D", {"category": "news"}),
            ("Forum Diskussion", {"category": "forum"}),
            ("Ernährung", {"source_type": "news"}),
        ]
        
        for query, filter_metadata in category_tests:
            print(f"Query: '{query}' with filter: {filter_metadata}")
            
            try:
                results = vector_store.search(query, k=2, filter_metadata=filter_metadata)
                
                if results:
                    for j, (doc, score) in enumerate(results, 1):
                        print(f"  Result {j}: {doc.metadata.get('category', 'Unknown')} - {score:.3f}")
                        print(f"    {doc.content[:100].replace(chr(10), ' ')}...")
                else:
                    print(f"  No results with filter {filter_metadata}")
                    
            except Exception as e:
                print(f"  Filter search error: {e}")
            
            print()
        
        print("✅ Search testing completed!")
        
    except Exception as e:
        logger.error(f"Error in search testing: {e}")
        print(f"❌ Search test failed: {e}")


def interactive_search():
    """Interactive search mode."""
    
    print("\n=== Interactive Search Mode ===")
    print("Enter your search queries (or 'quit' to exit)")
    
    try:
        vector_store = FAISSVectorStore(
            index_path="data/processed/faiss_index",
            embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            dimension=384
        )
        
        stats = vector_store.get_stats()
        print(f"Ready to search {stats['total_documents']} documents")
        print()
        
        while True:
            query = input("🔍 Search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            try:
                results = vector_store.search(query, k=5)
                
                if results:
                    print(f"\n📄 Found {len(results)} results:")
                    for i, (doc, score) in enumerate(results, 1):
                        print(f"\n{i}. Score: {score:.3f}")
                        print(f"   Category: {doc.metadata.get('category', 'Unknown')}")
                        print(f"   Content: {doc.content[:200].replace(chr(10), ' ')}...")
                        
                        if 'url' in doc.metadata:
                            print(f"   URL: {doc.metadata['url']}")
                else:
                    print("❌ No results found")
                    
            except Exception as e:
                print(f"❌ Search error: {e}")
            
            print()
    
    except Exception as e:
        print(f"❌ Interactive search failed: {e}")


def main():
    """Main function."""
    
    # Check if vector store exists
    index_path = Path("data/processed/faiss_index")
    if not index_path.exists():
        print("❌ Vector store not found!")
        print("Please run the index builder first:")
        print("  python src/rag/build_index.py")
        return
    
    # Run automated tests
    test_search_functionality()
    
    # Ask for interactive mode
    response = input("\nStart interactive search mode? (y/n): ")
    if response.lower() == 'y':
        interactive_search()
    
    print("\n👋 Search testing completed!")


if __name__ == "__main__":
    main()