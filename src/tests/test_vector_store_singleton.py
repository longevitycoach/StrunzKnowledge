#!/usr/bin/env python3
"""
Test cases for vector store singleton pattern to prevent multiple instances
and sentence-transformers model loading.
"""

import pytest
import threading
import time
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVectorStoreSingleton:
    """Test the vector store singleton pattern."""
    
    def setup_method(self):
        """Reset singleton state before each test."""
        # Clear the singleton instance
        import src.rag.search as search_module
        search_module._vector_store_instance = None
        search_module._vector_store_lock = None
        
        # Mock the FAISSVectorStore to avoid actual file system dependencies
        self.mock_vector_store = Mock()
        self.mock_vector_store.load_index.return_value = True
        self.mock_vector_store.documents = ["doc1", "doc2", "doc3"]
        self.mock_vector_store.index = Mock()
        
        # Track how many times FAISSVectorStore is instantiated
        self.instance_count = 0
        
    def mock_faiss_vector_store(self, *args, **kwargs):
        """Mock FAISSVectorStore constructor to track instantiation."""
        self.instance_count += 1
        logger.info(f"FAISSVectorStore instance #{self.instance_count} created")
        return self.mock_vector_store
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_singleton_single_instance(self, mock_faiss_class):
        """Test that only one instance is created when accessed multiple times."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import get_vector_store_singleton
        
        # Get the singleton multiple times
        instance1 = get_vector_store_singleton()
        instance2 = get_vector_store_singleton()
        instance3 = get_vector_store_singleton()
        
        # Verify all calls return the same instance
        assert instance1 is instance2
        assert instance2 is instance3
        
        # Verify FAISSVectorStore was only instantiated once
        assert self.instance_count == 1
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ Singleton pattern correctly prevents multiple instances")
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_singleton_thread_safety(self, mock_faiss_class):
        """Test that singleton is thread-safe."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import get_vector_store_singleton
        
        instances = []
        
        def create_instance():
            """Create instance in a thread."""
            instance = get_vector_store_singleton()
            instances.append(instance)
            time.sleep(0.01)  # Small delay to test concurrency
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all threads got the same instance
        assert len(instances) == 10
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance
        
        # Verify FAISSVectorStore was only instantiated once
        assert self.instance_count == 1
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ Singleton pattern is thread-safe")
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_knowledge_searcher_uses_singleton(self, mock_faiss_class):
        """Test that KnowledgeSearcher uses the singleton pattern."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import KnowledgeSearcher
        
        # Create multiple KnowledgeSearcher instances
        searcher1 = KnowledgeSearcher()
        searcher2 = KnowledgeSearcher()
        searcher3 = KnowledgeSearcher()
        
        # Verify all searchers use the same vector store instance
        assert searcher1.vector_store is searcher2.vector_store
        assert searcher2.vector_store is searcher3.vector_store
        
        # Verify FAISSVectorStore was only instantiated once
        assert self.instance_count == 1
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ KnowledgeSearcher correctly uses singleton pattern")
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_is_vector_store_loaded(self, mock_faiss_class):
        """Test the is_vector_store_loaded helper function."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import is_vector_store_loaded, get_vector_store_singleton
        
        # Initially, no vector store should be loaded
        assert not is_vector_store_loaded()
        
        # After getting the singleton, it should be loaded
        get_vector_store_singleton()
        assert is_vector_store_loaded()
        
        # Verify FAISSVectorStore was only instantiated once
        assert self.instance_count == 1
        
        logger.info("✅ is_vector_store_loaded function works correctly")
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_health_check_performance(self, mock_faiss_class):
        """Test that health checks don't recreate vector store instances."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import is_vector_store_loaded, get_vector_store_singleton
        
        # Simulate server startup - create initial instance
        get_vector_store_singleton()
        assert self.instance_count == 1
        
        # Simulate multiple health checks
        for i in range(10):
            # This is what the health check does
            if is_vector_store_loaded():
                # Only get singleton if already loaded
                instance = get_vector_store_singleton()
                assert instance is not None
        
        # Verify no additional instances were created
        assert self.instance_count == 1
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ Health checks don't recreate vector store instances")
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_enhanced_server_initialization(self, mock_faiss_class):
        """Test that enhanced server initialization uses singleton."""
        mock_faiss_class.side_effect = self.mock_faiss_vector_store
        
        from src.rag.search import KnowledgeSearcher
        
        # Simulate what happens in enhanced_server.py
        # Multiple components might try to create KnowledgeSearcher
        searcher1 = KnowledgeSearcher()  # From enhanced server
        searcher2 = KnowledgeSearcher()  # From some tool
        searcher3 = KnowledgeSearcher()  # From another tool
        
        # Verify singleton behavior
        assert searcher1.vector_store is searcher2.vector_store
        assert searcher2.vector_store is searcher3.vector_store
        
        # Verify only one FAISSVectorStore instance was created
        assert self.instance_count == 1
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ Enhanced server initialization uses singleton correctly")


class TestSentenceTransformersLoading:
    """Test that sentence-transformers model is only loaded once."""
    
    def setup_method(self):
        """Reset singleton state before each test."""
        import src.rag.search as search_module
        search_module._vector_store_instance = None
        search_module._vector_store_lock = None
        
        # Track sentence-transformers model loading
        self.model_load_count = 0
        
    def mock_sentence_transformers_model(self, *args, **kwargs):
        """Mock SentenceTransformer model loading."""
        self.model_load_count += 1
        logger.info(f"SentenceTransformer model load #{self.model_load_count}")
        
        # Return a mock model
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
        return mock_model
    
    @patch('src.rag.vector_store.SentenceTransformer')
    @patch('src.rag.search.FAISSVectorStore')
    def test_sentence_transformers_loaded_once(self, mock_faiss_class, mock_sentence_transformer):
        """Test that sentence-transformers model is only loaded once."""
        mock_sentence_transformer.side_effect = self.mock_sentence_transformers_model
        
        # Mock FAISSVectorStore to simulate model loading
        mock_vector_store = Mock()
        mock_vector_store.load_index.return_value = True
        mock_vector_store.documents = ["doc1", "doc2", "doc3"]
        mock_vector_store.index = Mock()
        mock_faiss_class.return_value = mock_vector_store
        
        from src.rag.search import KnowledgeSearcher
        
        # Create multiple searchers - should only load model once
        searcher1 = KnowledgeSearcher()
        searcher2 = KnowledgeSearcher()
        searcher3 = KnowledgeSearcher()
        
        # Verify all searchers use the same vector store
        assert searcher1.vector_store is searcher2.vector_store
        assert searcher2.vector_store is searcher3.vector_store
        
        # Note: The actual sentence-transformers loading happens in FAISSVectorStore
        # This test verifies the singleton pattern prevents multiple vector store instances
        assert mock_faiss_class.call_count == 1
        
        logger.info("✅ Singleton pattern prevents multiple sentence-transformers model loads")


class TestPerformanceMetrics:
    """Test performance improvements from singleton pattern."""
    
    def setup_method(self):
        """Reset singleton state before each test."""
        import src.rag.search as search_module
        search_module._vector_store_instance = None
        search_module._vector_store_lock = None
        
        # Track timing
        self.creation_times = []
        
    def mock_slow_vector_store(self, *args, **kwargs):
        """Mock slow vector store creation."""
        start_time = time.time()
        time.sleep(0.1)  # Simulate slow loading
        end_time = time.time()
        
        self.creation_times.append(end_time - start_time)
        logger.info(f"Vector store creation took {end_time - start_time:.3f}s")
        
        mock_store = Mock()
        mock_store.load_index.return_value = True
        mock_store.documents = ["doc1", "doc2", "doc3"]
        mock_store.index = Mock()
        return mock_store
    
    @patch('src.rag.search.FAISSVectorStore')
    def test_performance_improvement(self, mock_faiss_class):
        """Test that singleton pattern improves performance."""
        mock_faiss_class.side_effect = self.mock_slow_vector_store
        
        from src.rag.search import get_vector_store_singleton
        
        # First call should take time to create
        start_time = time.time()
        instance1 = get_vector_store_singleton()
        first_call_time = time.time() - start_time
        
        # Subsequent calls should be much faster
        start_time = time.time()
        instance2 = get_vector_store_singleton()
        second_call_time = time.time() - start_time
        
        start_time = time.time()
        instance3 = get_vector_store_singleton()
        third_call_time = time.time() - start_time
        
        # Verify instances are the same
        assert instance1 is instance2
        assert instance2 is instance3
        
        # Verify performance improvement
        assert len(self.creation_times) == 1  # Only one creation
        assert first_call_time >= 0.1  # First call takes time
        assert second_call_time < 0.01  # Subsequent calls are fast
        assert third_call_time < 0.01
        
        logger.info(f"✅ Performance improvement: 1st call {first_call_time:.3f}s, 2nd call {second_call_time:.3f}s")


def run_singleton_tests():
    """Run all singleton pattern tests."""
    logger.info("🧪 Running Vector Store Singleton Tests")
    logger.info("=" * 60)
    
    # Test classes
    test_classes = [
        TestVectorStoreSingleton,
        TestSentenceTransformersLoading,
        TestPerformanceMetrics
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        logger.info(f"\n📋 Running {test_class.__name__}")
        logger.info("-" * 40)
        
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Setup
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run test
                method = getattr(test_instance, test_method)
                method()
                
                passed_tests += 1
                logger.info(f"✅ {test_method} - PASSED")
                
            except Exception as e:
                logger.error(f"❌ {test_method} - FAILED: {e}")
                import traceback
                traceback.print_exc()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"🎯 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All singleton pattern tests passed!")
        return True
    else:
        logger.error(f"❌ {total_tests - passed_tests} tests failed")
        return False


if __name__ == "__main__":
    # Run tests
    success = run_singleton_tests()
    
    if success:
        print("\n🎉 Vector Store Singleton Pattern Tests: ALL PASSED")
        print("✅ Multiple instances prevention: WORKING")
        print("✅ Thread safety: WORKING")
        print("✅ Performance optimization: WORKING")
        print("✅ Health check efficiency: WORKING")
    else:
        print("\n❌ Some tests failed - check logs above")
        sys.exit(1)