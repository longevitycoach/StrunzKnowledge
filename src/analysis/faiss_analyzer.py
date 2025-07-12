#!/usr/bin/env python3
"""
Analyze FAISS index to understand content distribution and characteristics
"""

import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FAISSAnalyzer:
    def __init__(self):
        self.data_dir = Path("data")
        self.index_dir = self.data_dir / "faiss_indices"
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
    def load_index_and_metadata(self):
        """Load the combined FAISS index and metadata."""
        combined_index_file = self.index_dir / "combined_index.faiss"
        combined_metadata_file = self.index_dir / "combined_metadata.json"
        
        if not combined_index_file.exists():
            logging.error("Combined index not found!")
            return None, None
            
        # Load index
        index = faiss.read_index(str(combined_index_file))
        
        # Load metadata
        with open(combined_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        return index, metadata
    
    def analyze_content_distribution(self, metadata):
        """Analyze distribution of content across sources."""
        documents = metadata['documents']
        
        # Count by source
        source_counts = Counter()
        source_chunk_lengths = defaultdict(list)
        
        for doc in documents:
            source = doc['metadata'].get('source', 'unknown')
            source_counts[source] += 1
            source_chunk_lengths[source].append(len(doc['text']))
        
        print("\n=== CONTENT DISTRIBUTION ===")
        print(f"Total documents: {len(documents)}")
        print("\nDocuments by source:")
        for source, count in source_counts.most_common():
            percentage = (count / len(documents)) * 100
            print(f"  - {source}: {count:,} ({percentage:.1f}%)")
        
        print("\nAverage chunk length by source:")
        for source, lengths in source_chunk_lengths.items():
            avg_length = sum(lengths) / len(lengths)
            print(f"  - {source}: {avg_length:.0f} characters")
        
        return source_counts, source_chunk_lengths
    
    def analyze_temporal_distribution(self, metadata):
        """Analyze temporal distribution of content."""
        documents = metadata['documents']
        
        # Extract dates by source
        dates_by_source = defaultdict(list)
        
        for doc in documents:
            source = doc['metadata'].get('source', 'unknown')
            
            # Try different date fields
            date = None
            if 'date' in doc['metadata']:
                date = doc['metadata']['date']
            elif 'year' in doc['metadata']:
                date = doc['metadata']['year']
            elif 'processed_date' in doc['metadata']:
                date = doc['metadata']['processed_date'][:10]
            
            if date:
                dates_by_source[source].append(date)
        
        print("\n=== TEMPORAL DISTRIBUTION ===")
        for source, dates in dates_by_source.items():
            if dates:
                # Extract years
                years = []
                for date in dates:
                    try:
                        if len(date) == 4:  # Just year
                            years.append(int(date))
                        else:  # Full date
                            years.append(int(date[:4]))
                    except:
                        continue
                
                if years:
                    year_counts = Counter(years)
                    print(f"\n{source.upper()} content by year:")
                    for year, count in sorted(year_counts.items()):
                        print(f"  - {year}: {count}")
                    print(f"  Date range: {min(years)} - {max(years)}")
    
    def analyze_authors(self, metadata):
        """Analyze author distribution."""
        documents = metadata['documents']
        
        author_counts = Counter()
        for doc in documents:
            author = doc['metadata'].get('author', 'Unknown')
            author_counts[author] += 1
        
        print("\n=== AUTHOR DISTRIBUTION ===")
        for author, count in author_counts.most_common(10):
            percentage = (count / len(documents)) * 100
            print(f"  - {author}: {count:,} ({percentage:.1f}%)")
    
    def analyze_topics(self, metadata):
        """Analyze topics and titles."""
        documents = metadata['documents']
        
        # Analyze titles by source
        titles_by_source = defaultdict(set)
        tags_counter = Counter()
        
        for doc in documents:
            source = doc['metadata'].get('source', 'unknown')
            
            # Collect unique titles
            if 'title' in doc:
                titles_by_source[source].add(doc['title'])
            elif 'title' in doc['metadata']:
                titles_by_source[source].add(doc['metadata']['title'])
            
            # Collect tags
            if 'tags' in doc['metadata']:
                tags = doc['metadata']['tags']
                if isinstance(tags, list):
                    tags_counter.update(tags)
        
        print("\n=== CONTENT TOPICS ===")
        
        # Print unique titles/topics by source
        for source, titles in titles_by_source.items():
            print(f"\n{source.upper()} - Unique titles/topics: {len(titles)}")
            if source == 'book':
                print("Books:")
                for title in sorted(titles):
                    print(f"  - {title}")
        
        # Print top tags
        if tags_counter:
            print("\nTop 20 tags:")
            for tag, count in tags_counter.most_common(20):
                print(f"  - {tag}: {count}")
    
    def analyze_index_structure(self, index, metadata):
        """Analyze FAISS index structure and statistics."""
        print("\n=== INDEX STRUCTURE ===")
        print(f"Index type: {type(index).__name__}")
        print(f"Number of vectors: {index.ntotal}")
        print(f"Vector dimension: {index.d}")
        print(f"Index trained: {index.is_trained}")
        
        # Calculate approximate index size
        # For IndexFlatL2, size = num_vectors * dimension * 4 bytes (float32)
        index_size_mb = (index.ntotal * index.d * 4) / (1024 * 1024)
        print(f"Approximate index size: {index_size_mb:.2f} MB")
        
        # Sample some vectors to analyze
        if index.ntotal > 0:
            sample_size = min(1000, index.ntotal)
            sample_vectors = index.reconstruct_n(0, sample_size)
            
            # Calculate statistics
            norms = np.linalg.norm(sample_vectors, axis=1)
            print(f"\nVector statistics (sample of {sample_size}):")
            print(f"  - Mean norm: {np.mean(norms):.4f}")
            print(f"  - Std norm: {np.std(norms):.4f}")
            print(f"  - Min norm: {np.min(norms):.4f}")
            print(f"  - Max norm: {np.max(norms):.4f}")
    
    def test_search_functionality(self, index, metadata):
        """Test search functionality with sample queries."""
        print("\n=== SEARCH FUNCTIONALITY TEST ===")
        
        test_queries = [
            "Vitamin D Mangel",
            "Low Carb Ernährung",
            "Stress reduzieren",
            "Aminosäuren",
            "Bewegung und Sport"
        ]
        
        documents = metadata['documents']
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            # Encode query
            query_vector = self.model.encode([query])
            
            # Search
            k = 5
            distances, indices = index.search(query_vector.astype('float32'), k)
            
            print("Top results:")
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(documents):
                    doc = documents[idx]
                    source = doc['metadata'].get('source', 'unknown')
                    title = doc.get('title', doc['metadata'].get('title', 'No title'))
                    text_preview = doc['text'][:100] + "..."
                    
                    print(f"  {i+1}. [{source}] {title}")
                    print(f"     Distance: {dist:.4f}")
                    print(f"     Preview: {text_preview}")
    
    def generate_summary_report(self, metadata):
        """Generate a summary report."""
        documents = metadata['documents']
        
        print("\n" + "="*60)
        print("FAISS INDEX ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nCreated: {metadata.get('created_date', 'Unknown')}")
        print(f"Last updated: {metadata.get('last_updated', 'Unknown')}")
        print(f"Embedding model: {metadata.get('embedding_model', 'Unknown')}")
        print(f"Total documents: {len(documents):,}")
        
        # Calculate total text size
        total_chars = sum(len(doc['text']) for doc in documents)
        total_mb = total_chars / (1024 * 1024)
        print(f"Total text size: {total_mb:.1f} MB ({total_chars:,} characters)")
        
        # Sources summary
        sources = metadata.get('sources', [])
        print(f"\nContent sources: {', '.join(sources)}")
        
        # Processing dates
        proc_dates = set()
        for doc in documents:
            if 'processed_date' in doc['metadata']:
                proc_dates.add(doc['metadata']['processed_date'][:10])
        
        if proc_dates:
            print(f"\nProcessing dates: {min(proc_dates)} to {max(proc_dates)}")

def main():
    analyzer = FAISSAnalyzer()
    
    # Load index and metadata
    index, metadata = analyzer.load_index_and_metadata()
    
    if index is None or metadata is None:
        return
    
    # Run analyses
    analyzer.generate_summary_report(metadata)
    source_counts, source_lengths = analyzer.analyze_content_distribution(metadata)
    analyzer.analyze_temporal_distribution(metadata)
    analyzer.analyze_authors(metadata)
    analyzer.analyze_topics(metadata)
    analyzer.analyze_index_structure(index, metadata)
    analyzer.test_search_functionality(index, metadata)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()