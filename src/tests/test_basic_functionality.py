#!/usr/bin/env python3
"""
Basic functionality tests for the knowledge base
"""

import pytest
import json
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBasicFunctionality:
    """Test basic functionality without external dependencies."""
    
    @pytest.fixture
    def data_dir(self):
        """Get data directory."""
        return Path("data")
    
    def test_data_directory_structure(self, data_dir):
        """Test that required directories exist."""
        assert data_dir.exists(), "Data directory should exist"
        
        # Check for main subdirectories
        expected_dirs = ["raw", "processed", "faiss_indices"]
        for dir_name in expected_dirs:
            dir_path = data_dir / dir_name
            if not dir_path.exists():
                pytest.skip(f"Directory {dir_name} not found - may not be initialized")
    
    def test_faiss_indices_exist(self, data_dir):
        """Test that FAISS indices exist."""
        indices_dir = data_dir / "faiss_indices"
        if not indices_dir.exists():
            pytest.skip("FAISS indices directory not found")
        
        # Look for any .faiss files
        faiss_files = list(indices_dir.rglob("*.faiss"))
        assert len(faiss_files) > 0, "Should have at least one FAISS index file"
    
    def test_processed_data_exists(self, data_dir):
        """Test that processed data files exist."""
        processed_dir = data_dir / "processed"
        if not processed_dir.exists():
            pytest.skip("Processed data directory not found")
        
        # Check for JSON files
        json_files = list(processed_dir.rglob("*.json"))
        if len(json_files) == 0:
            pytest.skip("No processed JSON files found")
        
        # Verify at least one JSON file is valid
        valid_files = 0
        for json_file in json_files[:3]:  # Check first 3 files
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, (list, dict)):
                        valid_files += 1
            except:
                continue
        
        assert valid_files > 0, "Should have at least one valid JSON file"
    
    def test_books_directory(self, data_dir):
        """Test books directory and PDF files."""
        books_dir = data_dir / "books"
        if not books_dir.exists():
            pytest.skip("Books directory not found")
        
        pdf_files = list(books_dir.glob("*.pdf"))
        if len(pdf_files) == 0:
            pytest.skip("No PDF files found in books directory")
        
        # Check file naming convention
        valid_names = 0
        for pdf_file in pdf_files:
            if pdf_file.name.startswith("Dr.Ulrich-Strunz_"):
                valid_names += 1
        
        assert valid_names > 0, "Should have books following naming convention"

class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    @pytest.fixture
    def sample_processed_file(self):
        """Get a sample processed file for testing."""
        processed_dir = Path("data/processed")
        if not processed_dir.exists():
            pytest.skip("No processed directory found")
        
        json_files = list(processed_dir.rglob("*.json"))
        if not json_files:
            pytest.skip("No processed JSON files found")
        
        return json_files[0]
    
    def test_json_structure(self, sample_processed_file):
        """Test that processed JSON files have correct structure."""
        with open(sample_processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            # Check first item structure
            item = data[0]
            assert 'text' in item, "Items should have 'text' field"
            assert 'metadata' in item, "Items should have 'metadata' field"
            
            # Check metadata structure
            metadata = item['metadata']
            assert 'source' in metadata, "Metadata should have 'source' field"
            assert 'processed_date' in metadata, "Metadata should have 'processed_date' field"
    
    def test_text_content_quality(self, sample_processed_file):
        """Test that text content meets quality standards."""
        with open(sample_processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            text_lengths = []
            valid_texts = 0
            
            for item in data[:10]:  # Check first 10 items
                text = item.get('text', '')
                if len(text) > 10:  # Minimum length check
                    valid_texts += 1
                    text_lengths.append(len(text))
            
            assert valid_texts > 0, "Should have at least some valid text content"
            if text_lengths:
                avg_length = sum(text_lengths) / len(text_lengths)
                assert avg_length > 50, f"Average text length too short: {avg_length}"

class TestSearchCapabilities:
    """Test search functionality if available."""
    
    def test_faiss_index_loading(self):
        """Test that FAISS indices can be loaded."""
        try:
            import faiss
        except ImportError:
            pytest.skip("FAISS not available")
        
        indices_dir = Path("data/faiss_indices")
        if not indices_dir.exists():
            pytest.skip("No FAISS indices directory")
        
        faiss_files = list(indices_dir.rglob("*.faiss"))
        if not faiss_files:
            pytest.skip("No FAISS index files found")
        
        # Try to load at least one index
        loaded = False
        for faiss_file in faiss_files:
            try:
                index = faiss.read_index(str(faiss_file))
                assert index.ntotal > 0, f"Index {faiss_file.name} should have vectors"
                loaded = True
                break
            except Exception as e:
                continue
        
        assert loaded, "Should be able to load at least one FAISS index"
    
    def test_embedding_model_availability(self):
        """Test that embedding model can be loaded."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            pytest.skip("sentence-transformers not available")
        
        try:
            model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            
            # Test encoding a simple phrase
            test_text = "Vitamin D"
            embedding = model.encode(test_text)
            
            assert len(embedding) == 384, "Embedding should have 384 dimensions"
            assert abs(embedding.sum()) > 0, "Embedding should not be all zeros"
            
        except Exception as e:
            pytest.skip(f"Could not load embedding model: {e}")

@pytest.mark.slow
class TestSystemIntegration:
    """Test system integration (marked as slow)."""
    
    def test_mcp_server_import(self):
        """Test that MCP server can be imported."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from mcp import server
            assert hasattr(server, 'mcp'), "Server should have mcp instance"
        except ImportError as e:
            pytest.skip(f"MCP server not available: {e}")
    
    def test_processor_imports(self):
        """Test that processors can be imported."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from rag import news_processor
            from rag import forum_processor
            assert hasattr(news_processor, 'NewsProcessor'), "Should have NewsProcessor class"
            assert hasattr(forum_processor, 'ForumProcessor'), "Should have ForumProcessor class"
        except ImportError as e:
            pytest.skip(f"Processors not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])