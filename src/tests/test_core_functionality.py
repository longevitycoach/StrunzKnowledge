#!/usr/bin/env python3
"""
Core functionality tests without external dependencies
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import os

class TestDataStructure:
    """Test the data structure and file organization."""
    
    @pytest.fixture
    def data_dir(self):
        return Path("data")
    
    def test_directory_structure(self, data_dir):
        """Test that core directories exist."""
        assert data_dir.exists(), "Data directory should exist"
        
        # Check for main subdirectories
        dirs_to_check = ["books", "raw", "processed", "faiss_indices"]
        existing_dirs = []
        
        for dir_name in dirs_to_check:
            dir_path = data_dir / dir_name
            if dir_path.exists():
                existing_dirs.append(dir_name)
        
        print(f"\n📁 Directory structure:")
        for dir_name in dirs_to_check:
            status = "✅" if dir_name in existing_dirs else "❌"
            print(f"  {status} {dir_name}/")
        
        assert len(existing_dirs) >= 2, f"Should have at least 2 core directories, found: {existing_dirs}"
    
    def test_books_collection(self, data_dir):
        """Test books collection."""
        books_dir = data_dir / "books"
        if not books_dir.exists():
            pytest.skip("Books directory not found")
        
        pdf_files = list(books_dir.glob("*.pdf"))
        
        print(f"\n📚 Books collection:")
        print(f"  - Total PDF files: {len(pdf_files)}")
        
        if pdf_files:
            # Check naming convention
            properly_named = 0
            for pdf in pdf_files:
                if pdf.name.startswith("Dr.Ulrich-Strunz_"):
                    properly_named += 1
                print(f"    - {pdf.name}")
            
            print(f"  - Properly named: {properly_named}/{len(pdf_files)}")
            assert properly_named > 0, "Should have at least one properly named book"
        else:
            pytest.skip("No PDF files found in books directory")
    
    def test_processed_data_files(self, data_dir):
        """Test processed data files exist."""
        processed_dir = data_dir / "processed"
        if not processed_dir.exists():
            pytest.skip("Processed directory not found")
        
        # Check subdirectories
        subdirs = ["news", "forum", "books"]
        found_data = {}
        
        for subdir in subdirs:
            subdir_path = processed_dir / subdir
            if subdir_path.exists():
                json_files = list(subdir_path.glob("*.json"))
                found_data[subdir] = len(json_files)
        
        print(f"\n📊 Processed data:")
        for subdir, count in found_data.items():
            print(f"  - {subdir}: {count} JSON files")
        
        assert len(found_data) > 0, "Should have at least one type of processed data"
    
    def test_faiss_indices(self, data_dir):
        """Test FAISS indices directory."""
        indices_dir = data_dir / "faiss_indices"
        if not indices_dir.exists():
            pytest.skip("FAISS indices directory not found")
        
        faiss_files = list(indices_dir.rglob("*.faiss"))
        json_files = list(indices_dir.rglob("*.json"))
        
        print(f"\n🔍 FAISS indices:")
        print(f"  - Index files (.faiss): {len(faiss_files)}")
        print(f"  - Metadata files (.json): {len(json_files)}")
        
        for faiss_file in faiss_files:
            size_mb = faiss_file.stat().st_size / (1024 * 1024)
            print(f"    - {faiss_file.relative_to(indices_dir)} ({size_mb:.1f} MB)")
        
        if faiss_files:
            assert len(json_files) > 0, "Should have metadata files for indices"

class TestDataIntegrity:
    """Test data integrity and content quality."""
    
    @pytest.fixture
    def forum_data_file(self):
        """Get forum data file."""
        forum_file = Path("data/processed/forum/forum_documents_20250712_211416.json")
        if not forum_file.exists():
            pytest.skip("Forum data file not found")
        return forum_file
    
    def test_forum_data_structure(self, forum_data_file):
        """Test forum data structure."""
        with open(forum_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list), "Forum data should be a list"
        assert len(data) > 0, "Forum data should not be empty"
        
        # Test structure of first few items
        for i, item in enumerate(data[:5]):
            assert 'text' in item, f"Item {i} should have 'text' field"
            assert 'metadata' in item, f"Item {i} should have 'metadata' field"
            
            metadata = item['metadata']
            assert 'source' in metadata, f"Item {i} metadata should have 'source'"
            assert metadata['source'] == 'forum', f"Item {i} source should be 'forum'"
        
        print(f"\n🗣️ Forum data structure:")
        print(f"  - Total chunks: {len(data):,}")
        print(f"  - Structure validation: ✅ Passed")
    
    def test_content_quality_metrics(self, forum_data_file):
        """Test content quality metrics."""
        with open(forum_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Analyze first 1000 items for performance
        sample_size = min(1000, len(data))
        sample_data = data[:sample_size]
        
        text_lengths = []
        empty_count = 0
        has_metadata_count = 0
        categories = set()
        
        for item in sample_data:
            text = item.get('text', '')
            metadata = item.get('metadata', {})
            
            if len(text) == 0:
                empty_count += 1
            else:
                text_lengths.append(len(text))
            
            if metadata:
                has_metadata_count += 1
                category = metadata.get('category')
                if category:
                    categories.add(category)
        
        # Calculate metrics
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        min_length = min(text_lengths) if text_lengths else 0
        max_length = max(text_lengths) if text_lengths else 0
        
        print(f"\n📈 Content quality metrics (sample of {sample_size}):")
        print(f"  - Average text length: {avg_length:.0f} chars")
        print(f"  - Length range: {min_length} - {max_length} chars")
        print(f"  - Empty texts: {empty_count}/{sample_size} ({empty_count/sample_size*100:.1f}%)")
        print(f"  - Items with metadata: {has_metadata_count}/{sample_size} ({has_metadata_count/sample_size*100:.1f}%)")
        print(f"  - Unique categories: {len(categories)}")
        
        # Quality assertions
        assert avg_length > 20, f"Average text length too short: {avg_length}"
        assert empty_count < sample_size * 0.5, f"Too many empty texts: {empty_count}/{sample_size}"
        assert has_metadata_count > sample_size * 0.8, f"Too few items with metadata: {has_metadata_count}/{sample_size}"
    
    def test_forum_categories(self, forum_data_file):
        """Test forum category distribution."""
        with open(forum_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = {}
        for item in data:
            category = item.get('metadata', {}).get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        print(f"\n📂 Category distribution:")
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            percentage = (count / len(data)) * 100
            print(f"  - {category}: {count:,} chunks ({percentage:.1f}%)")
        
        assert len(categories) > 1, "Should have multiple categories"
        assert categories.get('Unknown', 0) < len(data) * 0.3, "Too many uncategorized items"

class TestFileSystemMetrics:
    """Test file system metrics and storage usage."""
    
    def test_storage_usage(self):
        """Test storage usage across directories."""
        data_dir = Path("data")
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        storage_stats = {}
        
        for subdir in ["books", "raw", "processed", "faiss_indices"]:
            subdir_path = data_dir / subdir
            if subdir_path.exists():
                total_size = 0
                file_count = 0
                
                for file_path in subdir_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
                
                storage_stats[subdir] = {
                    'size_mb': total_size / (1024 * 1024),
                    'files': file_count
                }
        
        print(f"\n💾 Storage usage:")
        total_size = 0
        total_files = 0
        
        for subdir, stats in storage_stats.items():
            print(f"  - {subdir}: {stats['size_mb']:.1f} MB ({stats['files']} files)")
            total_size += stats['size_mb']
            total_files += stats['files']
        
        print(f"  - Total: {total_size:.1f} MB ({total_files} files)")
        
        assert total_size > 0, "Should have some data stored"
        assert total_files > 0, "Should have some files"

class TestProjectConfiguration:
    """Test project configuration and setup."""
    
    def test_required_files(self):
        """Test that required project files exist."""
        required_files = [
            "README.md",
            "requirements.txt",
            "Dockerfile",
            "railway.toml",
            ".github/workflows/update-index.yml"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        print(f"\n⚙️ Project configuration:")
        for file_path in required_files:
            status = "✅" if file_path in existing_files else "❌"
            print(f"  {status} {file_path}")
        
        assert len(existing_files) >= len(required_files) * 0.8, f"Missing critical files: {missing_files}"
    
    def test_python_modules(self):
        """Test that Python modules can be imported."""
        modules_to_test = [
            ("json", True),
            ("pathlib", True),
            ("datetime", True),
            ("collections", True),
            ("re", True),
            ("logging", True),
            ("sentence_transformers", False),  # Optional
            ("faiss", False),  # Optional
            ("fastmcp", False),  # Optional
        ]
        
        import_results = {}
        
        for module_name, required in modules_to_test:
            try:
                __import__(module_name)
                import_results[module_name] = "✅ Available"
            except ImportError:
                if required:
                    import_results[module_name] = "❌ Missing (Required)"
                else:
                    import_results[module_name] = "⚠️ Missing (Optional)"
        
        print(f"\n🐍 Python modules:")
        for module, status in import_results.items():
            print(f"  {status}: {module}")
        
        # Check that all required modules are available
        missing_required = [
            module for module, required in modules_to_test 
            if required and "❌" in import_results[module]
        ]
        
        assert len(missing_required) == 0, f"Missing required modules: {missing_required}"

def generate_comprehensive_report():
    """Generate a comprehensive test report."""
    report = {
        "test_execution": {
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name
        },
        "data_metrics": {},
        "system_health": "unknown"
    }
    
    try:
        # Collect data metrics
        data_dir = Path("data")
        if data_dir.exists():
            # Books
            books_dir = data_dir / "books"
            if books_dir.exists():
                pdf_files = list(books_dir.glob("*.pdf"))
                report["data_metrics"]["books"] = len(pdf_files)
            
            # Forum data
            forum_file = data_dir / "processed" / "forum" / "forum_documents_20250712_211416.json"
            if forum_file.exists():
                with open(forum_file, 'r') as f:
                    forum_data = json.load(f)
                report["data_metrics"]["forum_chunks"] = len(forum_data)
            
            # FAISS indices
            indices_dir = data_dir / "faiss_indices"
            if indices_dir.exists():
                faiss_files = list(indices_dir.rglob("*.faiss"))
                report["data_metrics"]["faiss_indices"] = len(faiss_files)
        
        report["system_health"] = "operational"
        
    except Exception as e:
        report["error"] = str(e)
        report["system_health"] = "degraded"
    
    return report

if __name__ == "__main__":
    # Generate report
    report = generate_comprehensive_report()
    
    # Save report
    with open("test_execution_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test execution report saved to test_execution_report.json")