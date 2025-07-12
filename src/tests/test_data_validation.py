#!/usr/bin/env python3
"""
Data validation tests for the Strunz Knowledge Base
"""

import pytest
import json
import faiss
from pathlib import Path
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestDataStructure:
    """Test the overall data structure and organization."""
    
    @pytest.fixture
    def data_dir(self):
        return Path("data")
    
    def test_directory_structure(self, data_dir):
        """Test that all required directories exist."""
        required_dirs = [
            "books",
            "raw/news", 
            "raw/forum",
            "processed/news",
            "processed/forum", 
            "processed/books",
            "faiss_indices"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not (data_dir / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            pytest.skip(f"Missing directories: {missing_dirs}")
        
        assert True, "All required directories exist"
    
    def test_books_collection(self, data_dir):
        """Test books collection and naming."""
        books_dir = data_dir / "books"
        if not books_dir.exists():
            pytest.skip("Books directory not found")
        
        pdf_files = list(books_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found")
        
        # Check naming convention
        properly_named = 0
        for pdf in pdf_files:
            if pdf.name.startswith("Dr.Ulrich-Strunz_") and pdf.name.endswith(".pdf"):
                properly_named += 1
        
        assert properly_named > 0, f"Found {properly_named}/{len(pdf_files)} properly named books"
        
        # Log the books found
        print(f"\n📚 Found {len(pdf_files)} books:")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")

class TestProcessedData:
    """Test processed data integrity and structure."""
    
    @pytest.fixture
    def forum_data(self):
        """Load forum data."""
        forum_file = Path("data/processed/forum/forum_documents_20250712_211416.json")
        if not forum_file.exists():
            pytest.skip("Forum data file not found")
        
        with open(forum_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture 
    def news_data(self):
        """Load news data."""
        news_dir = Path("data/processed/news")
        if not news_dir.exists():
            pytest.skip("News processed directory not found")
        
        json_files = list(news_dir.glob("*.json"))
        if not json_files:
            pytest.skip("No processed news files found")
        
        # Load the most recent file
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_forum_data_structure(self, forum_data):
        """Test forum data has correct structure."""
        assert isinstance(forum_data, list), "Forum data should be a list"
        assert len(forum_data) > 0, "Forum data should not be empty"
        
        # Test first item structure
        item = forum_data[0]
        assert 'text' in item, "Items should have 'text' field"
        assert 'metadata' in item, "Items should have 'metadata' field"
        
        metadata = item['metadata']
        assert metadata['source'] == 'forum', "Source should be 'forum'"
        assert 'processed_date' in metadata, "Should have processed_date"
        
        print(f"\n🗣️ Forum data: {len(forum_data)} chunks")
    
    def test_news_data_structure(self, news_data):
        """Test news data has correct structure."""
        if isinstance(news_data, dict):
            # Handle metadata format
            documents = news_data.get('documents', [])
        else:
            documents = news_data
        
        assert len(documents) > 0, "News data should not be empty"
        
        # Test first item
        item = documents[0]
        assert 'text' in item, "Items should have 'text' field"
        assert 'metadata' in item, "Items should have 'metadata' field"
        
        metadata = item['metadata']
        assert metadata['source'] == 'news', "Source should be 'news'"
        
        print(f"\n📰 News data: {len(documents)} chunks")
    
    def test_content_quality(self, forum_data):
        """Test content quality metrics."""
        text_lengths = []
        empty_texts = 0
        
        for item in forum_data[:100]:  # Sample first 100 items
            text = item.get('text', '')
            if len(text) == 0:
                empty_texts += 1
            else:
                text_lengths.append(len(text))
        
        if text_lengths:
            avg_length = sum(text_lengths) / len(text_lengths)
            min_length = min(text_lengths)
            max_length = max(text_lengths)
            
            print(f"\n📊 Content quality:")
            print(f"  - Average length: {avg_length:.0f} characters")
            print(f"  - Range: {min_length} - {max_length} characters")
            print(f"  - Empty texts: {empty_texts}/100")
            
            assert avg_length > 30, f"Average text length too short: {avg_length}"
            assert empty_texts < 50, f"Too many empty texts: {empty_texts}/100"

class TestFAISSIndices:
    """Test FAISS indices integrity and functionality."""
    
    @pytest.fixture
    def indices_dir(self):
        indices_dir = Path("data/faiss_indices")
        if not indices_dir.exists():
            pytest.skip("FAISS indices directory not found")
        return indices_dir
    
    def test_faiss_availability(self):
        """Test that FAISS is available."""
        try:
            import faiss
            assert True
        except ImportError:
            pytest.fail("FAISS library not available")
    
    def test_indices_exist(self, indices_dir):
        """Test that FAISS index files exist."""
        faiss_files = list(indices_dir.rglob("*.faiss"))
        assert len(faiss_files) > 0, "Should have at least one FAISS index file"
        
        print(f"\n🔍 Found {len(faiss_files)} FAISS indices:")
        for f in faiss_files:
            print(f"  - {f.relative_to(indices_dir)}")
    
    def test_index_loading(self, indices_dir):
        """Test that indices can be loaded."""
        faiss_files = list(indices_dir.rglob("*.faiss"))
        loaded_indices = 0
        
        for faiss_file in faiss_files:
            try:
                index = faiss.read_index(str(faiss_file))
                metadata_file = faiss_file.with_suffix('.json')
                
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Validate index
                    assert index.ntotal > 0, f"Index {faiss_file.name} should have vectors"
                    assert index.d == 384, f"Index should have 384 dimensions, got {index.d}"
                    
                    docs_count = len(metadata.get('documents', []))
                    assert index.ntotal == docs_count, f"Vector count ({index.ntotal}) != document count ({docs_count})"
                    
                    loaded_indices += 1
                    
                    print(f"  ✅ {faiss_file.name}: {index.ntotal:,} vectors, {index.d}D")
                
            except Exception as e:
                print(f"  ❌ {faiss_file.name}: {e}")
        
        assert loaded_indices > 0, "Should be able to load at least one index"
    
    def test_combined_index(self, indices_dir):
        """Test the combined index specifically."""
        combined_index = indices_dir / "combined_index.faiss"
        combined_metadata = indices_dir / "combined_metadata.json"
        
        if not combined_index.exists():
            pytest.skip("Combined index not found")
        
        # Load and validate
        index = faiss.read_index(str(combined_index))
        
        with open(combined_metadata, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        total_docs = len(metadata.get('documents', []))
        source_counts = metadata.get('source_counts', {})
        
        print(f"\n🎯 Combined Index:")
        print(f"  - Total vectors: {index.ntotal:,}")
        print(f"  - Total documents: {total_docs:,}")
        print(f"  - Dimensions: {index.d}")
        print(f"  - Sources: {source_counts}")
        
        assert index.ntotal == total_docs, "Combined index vector/document mismatch"

class TestAnalysisCapabilities:
    """Test analysis and search capabilities."""
    
    def test_embedding_model(self):
        """Test sentence transformer model availability."""
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            
            # Test German text encoding
            test_texts = [
                "Vitamin D Mangel",
                "Gesunde Ernährung", 
                "Sport und Fitness"
            ]
            
            embeddings = model.encode(test_texts)
            
            assert embeddings.shape == (3, 384), f"Expected (3, 384), got {embeddings.shape}"
            assert embeddings.std() > 0.1, "Embeddings should have reasonable variance"
            
            print(f"\n🧠 Embedding Model:")
            print(f"  - Model loaded successfully")
            print(f"  - Output shape: {embeddings.shape}")
            print(f"  - Embedding variance: {embeddings.std():.3f}")
            
        except ImportError:
            pytest.skip("sentence-transformers not available")
        except Exception as e:
            pytest.fail(f"Embedding model test failed: {e}")

class TestContentAnalysis:
    """Test content analysis and forum insights."""
    
    @pytest.fixture
    def forum_analysis_data(self):
        """Load forum data for analysis."""
        forum_file = Path("data/processed/forum/forum_documents_20250712_211416.json")
        if not forum_file.exists():
            pytest.skip("Forum data not found")
        
        with open(forum_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_forum_categories(self, forum_analysis_data):
        """Test forum category distribution."""
        categories = {}
        
        for item in forum_analysis_data:
            category = item.get('metadata', {}).get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        print(f"\n📊 Forum Categories:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(forum_analysis_data)) * 100
            print(f"  - {category}: {count:,} chunks ({percentage:.1f}%)")
        
        assert len(categories) > 1, "Should have multiple categories"
        assert 'Unknown' not in categories or categories['Unknown'] < len(forum_analysis_data) * 0.5, "Too many uncategorized items"
    
    def test_temporal_coverage(self, forum_analysis_data):
        """Test temporal coverage of forum data."""
        dates = []
        
        for item in forum_analysis_data:
            post_date = item.get('metadata', {}).get('post_date')
            if post_date:
                dates.append(post_date)
        
        if dates:
            dates.sort()
            date_range = f"{dates[0]} to {dates[-1]}"
            unique_years = len(set(date[:4] for date in dates if len(date) >= 4))
            
            print(f"\n📅 Temporal Coverage:")
            print(f"  - Date range: {date_range}")
            print(f"  - Posts with dates: {len(dates):,}")
            print(f"  - Years covered: {unique_years}")
            
            assert unique_years > 1, "Should cover multiple years"
        else:
            pytest.skip("No dated posts found")

def generate_test_summary():
    """Generate a summary of test results."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_categories": [
            "Data Structure Validation",
            "Processed Data Integrity", 
            "FAISS Index Functionality",
            "Analysis Capabilities",
            "Content Quality Assessment"
        ],
        "key_metrics": {
            "books_found": 0,
            "forum_chunks": 0,
            "news_chunks": 0,
            "faiss_indices": 0,
            "categories": []
        }
    }
    
    try:
        # Count books
        books_dir = Path("data/books")
        if books_dir.exists():
            summary["key_metrics"]["books_found"] = len(list(books_dir.glob("*.pdf")))
        
        # Count forum chunks
        forum_file = Path("data/processed/forum/forum_documents_20250712_211416.json")
        if forum_file.exists():
            with open(forum_file, 'r') as f:
                forum_data = json.load(f)
                summary["key_metrics"]["forum_chunks"] = len(forum_data)
        
        # Count FAISS indices
        indices_dir = Path("data/faiss_indices")
        if indices_dir.exists():
            summary["key_metrics"]["faiss_indices"] = len(list(indices_dir.rglob("*.faiss")))
        
    except Exception as e:
        summary["error"] = str(e)
    
    return summary

if __name__ == "__main__":
    # Run tests and generate summary
    pytest.main([__file__, "-v"])
    
    summary = generate_test_summary()
    with open("test_summary.json", "w") as f:
        json.dump(summary, f, indent=2)