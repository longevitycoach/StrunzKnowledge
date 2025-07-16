#!/usr/bin/env python3
"""
Test singleton pattern logic without FAISS dependencies
"""

import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockVectorStore:
    """Mock vector store for testing singleton pattern."""
    
    def __init__(self, load_time=0.1):
        self.load_time = load_time
        self.index = None
        self.documents = []
        self.load_index()
    
    def load_index(self):
        """Simulate loading index."""
        time.sleep(self.load_time)  # Simulate load time
        self.index = "mock_index"
        self.documents = ["doc1", "doc2", "doc3"]
        return True


class SingletonPattern:
    """Test implementation of singleton pattern."""
    
    def __init__(self):
        self._instance = None
        self._lock = None
        self.creation_count = 0
    
    def reset(self):
        """Reset for testing."""
        self._instance = None
        self._lock = None
        self.creation_count = 0
    
    def get_instance(self):
        """Get or create singleton instance."""
        if self._instance is None:
            if self._lock is None:
                self._lock = threading.Lock()
            
            # Double-check locking
            with self._lock:
                if self._instance is None:
                    self.creation_count += 1
                    logger.info(f"Creating singleton instance #{self.creation_count}")
                    self._instance = MockVectorStore()
        
        return self._instance
    
    def is_loaded(self):
        """Check if instance is loaded."""
        return self._instance is not None and hasattr(self._instance, 'index') and self._instance.index is not None


def test_singleton_prevents_multiple_instances():
    """Test that singleton prevents multiple instances."""
    logger.info("🧪 Test: Singleton prevents multiple instances")
    
    singleton = SingletonPattern()
    
    # Get instance multiple times
    instance1 = singleton.get_instance()
    instance2 = singleton.get_instance()
    instance3 = singleton.get_instance()
    
    # Verify same instance
    assert instance1 is instance2
    assert instance2 is instance3
    
    # Verify only one creation
    assert singleton.creation_count == 1
    
    logger.info("✅ PASSED: Only one instance created")


def test_singleton_thread_safety():
    """Test singleton thread safety."""
    logger.info("🧪 Test: Singleton thread safety")
    
    singleton = SingletonPattern()
    instances = []
    
    def get_instance():
        instance = singleton.get_instance()
        instances.append(instance)
    
    # Create multiple threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=get_instance)
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Verify all instances are the same
    assert len(instances) == 10
    first_instance = instances[0]
    for instance in instances[1:]:
        assert instance is first_instance
    
    # Verify only one creation
    assert singleton.creation_count == 1
    
    logger.info("✅ PASSED: Thread safety verified")


def test_performance_improvement():
    """Test performance improvement from singleton."""
    logger.info("🧪 Test: Performance improvement")
    
    singleton = SingletonPattern()
    
    # First access (should be slow)
    start_time = time.time()
    instance1 = singleton.get_instance()
    first_access_time = time.time() - start_time
    
    # Subsequent accesses (should be fast)
    start_time = time.time()
    instance2 = singleton.get_instance()
    second_access_time = time.time() - start_time
    
    start_time = time.time()
    instance3 = singleton.get_instance()
    third_access_time = time.time() - start_time
    
    # Verify performance improvement
    assert first_access_time >= 0.1  # First access takes time
    assert second_access_time < 0.01  # Subsequent accesses are fast
    assert third_access_time < 0.01
    
    # Verify same instances
    assert instance1 is instance2
    assert instance2 is instance3
    
    logger.info(f"✅ PASSED: Performance improved - 1st: {first_access_time:.3f}s, 2nd: {second_access_time:.3f}s")


def test_health_check_efficiency():
    """Test health check efficiency."""
    logger.info("🧪 Test: Health check efficiency")
    
    singleton = SingletonPattern()
    
    # Create instance first
    singleton.get_instance()
    
    # Simulate health checks
    health_check_times = []
    for i in range(10):
        start_time = time.time()
        is_loaded = singleton.is_loaded()
        end_time = time.time()
        
        health_check_times.append(end_time - start_time)
        assert is_loaded is True
    
    # Verify health checks are fast
    avg_time = sum(health_check_times) / len(health_check_times)
    assert avg_time < 0.001  # Health checks should be very fast
    
    # Verify still only one instance
    assert singleton.creation_count == 1
    
    logger.info(f"✅ PASSED: Health checks are efficient - avg: {avg_time:.6f}s")


def test_concurrent_health_checks():
    """Test concurrent health checks don't create multiple instances."""
    logger.info("🧪 Test: Concurrent health checks")
    
    singleton = SingletonPattern()
    
    # Create initial instance
    singleton.get_instance()
    initial_count = singleton.creation_count
    
    results = []
    
    def health_check():
        is_loaded = singleton.is_loaded()
        results.append(is_loaded)
        
        # Also try to get instance
        instance = singleton.get_instance()
        return instance
    
    # Run concurrent health checks
    threads = []
    for i in range(20):
        thread = threading.Thread(target=health_check)
        threads.append(thread)
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verify no additional instances were created
    assert singleton.creation_count == initial_count
    
    # Verify all health checks returned True
    assert all(results)
    assert len(results) == 20
    
    logger.info("✅ PASSED: Concurrent health checks don't create multiple instances")


def run_all_tests():
    """Run all singleton pattern tests."""
    logger.info("🧪 Running Singleton Pattern Logic Tests")
    logger.info("=" * 60)
    
    tests = [
        test_singleton_prevents_multiple_instances,
        test_singleton_thread_safety,
        test_performance_improvement,
        test_health_check_efficiency,
        test_concurrent_health_checks
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            logger.error(f"❌ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info("=" * 60)
    logger.info(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All singleton pattern logic tests passed!")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🎉 Singleton Pattern Logic Tests: ALL PASSED")
        print("✅ Multiple instances prevention: WORKING")
        print("✅ Thread safety: WORKING")
        print("✅ Performance optimization: WORKING")
        print("✅ Health check efficiency: WORKING")
        print("✅ Concurrent access safety: WORKING")
    else:
        print("\n❌ Some tests failed")
        exit(1)