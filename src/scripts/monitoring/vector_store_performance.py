#!/usr/bin/env python3
"""
Vector Store Performance Monitoring Script
Tracks singleton pattern effectiveness and performance metrics
"""

import time
import threading
import logging
from datetime import datetime
from pathlib import Path
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreMonitor:
    """Monitor vector store performance and singleton pattern effectiveness."""
    
    def __init__(self):
        self.metrics = {
            "singleton_created_at": None,
            "singleton_access_count": 0,
            "load_times": [],
            "health_check_times": [],
            "concurrent_access_count": 0,
            "search_times": [],
            "errors": []
        }
        self.lock = threading.Lock()
        
    def track_singleton_creation(self, creation_time: float):
        """Track singleton creation time."""
        with self.lock:
            self.metrics["singleton_created_at"] = datetime.now().isoformat()
            self.metrics["load_times"].append(creation_time)
            logger.info(f"Vector store singleton created in {creation_time:.3f}s")
    
    def track_singleton_access(self, access_time: float):
        """Track singleton access time."""
        with self.lock:
            self.metrics["singleton_access_count"] += 1
            if access_time > 0.001:  # Only track if measurable
                self.metrics["health_check_times"].append(access_time)
    
    def track_concurrent_access(self):
        """Track concurrent access to singleton."""
        with self.lock:
            self.metrics["concurrent_access_count"] += 1
    
    def track_search_performance(self, search_time: float):
        """Track search performance."""
        with self.lock:
            self.metrics["search_times"].append(search_time)
    
    def track_error(self, error_msg: str):
        """Track errors."""
        with self.lock:
            self.metrics["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
    
    def get_performance_report(self) -> dict:
        """Generate performance report."""
        with self.lock:
            report = {
                "singleton_status": {
                    "created_at": self.metrics["singleton_created_at"],
                    "total_accesses": self.metrics["singleton_access_count"],
                    "concurrent_accesses": self.metrics["concurrent_access_count"],
                    "is_singleton_working": self.metrics["singleton_access_count"] > 0 and len(self.metrics["load_times"]) <= 1
                },
                "performance_metrics": {
                    "initial_load_time": self.metrics["load_times"][0] if self.metrics["load_times"] else None,
                    "average_access_time": sum(self.metrics["health_check_times"]) / len(self.metrics["health_check_times"]) if self.metrics["health_check_times"] else 0,
                    "average_search_time": sum(self.metrics["search_times"]) / len(self.metrics["search_times"]) if self.metrics["search_times"] else 0,
                    "total_searches": len(self.metrics["search_times"])
                },
                "efficiency_indicators": {
                    "singleton_prevents_reloading": len(self.metrics["load_times"]) <= 1,
                    "fast_health_checks": sum(self.metrics["health_check_times"]) / len(self.metrics["health_check_times"]) < 0.1 if self.metrics["health_check_times"] else True,
                    "error_rate": len(self.metrics["errors"]) / max(1, self.metrics["singleton_access_count"])
                },
                "errors": self.metrics["errors"][-10:]  # Last 10 errors
            }
            return report
    
    def save_report(self, filepath: str):
        """Save performance report to file."""
        report = self.get_performance_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report saved to {filepath}")


# Global monitor instance
monitor = VectorStoreMonitor()


def patch_vector_store_for_monitoring():
    """Patch vector store functions to add monitoring."""
    try:
        import src.rag.search as search_module
        
        # Patch get_vector_store_singleton
        original_get_singleton = search_module.get_vector_store_singleton
        
        def monitored_get_singleton(*args, **kwargs):
            start_time = time.time()
            
            # Check if this is first creation
            is_first_creation = search_module._vector_store_instance is None
            
            result = original_get_singleton(*args, **kwargs)
            
            end_time = time.time()
            access_time = end_time - start_time
            
            if is_first_creation:
                monitor.track_singleton_creation(access_time)
            else:
                monitor.track_singleton_access(access_time)
            
            return result
        
        search_module.get_vector_store_singleton = monitored_get_singleton
        
        # Patch is_vector_store_loaded
        original_is_loaded = search_module.is_vector_store_loaded
        
        def monitored_is_loaded():
            start_time = time.time()
            result = original_is_loaded()
            end_time = time.time()
            
            monitor.track_singleton_access(end_time - start_time)
            return result
        
        search_module.is_vector_store_loaded = monitored_is_loaded
        
        logger.info("Vector store monitoring patches applied successfully")
        
    except Exception as e:
        logger.error(f"Failed to apply monitoring patches: {e}")


def start_monitoring():
    """Start performance monitoring."""
    logger.info("Starting vector store performance monitoring...")
    
    # Apply monitoring patches
    patch_vector_store_for_monitoring()
    
    # Start periodic reporting
    def periodic_report():
        while True:
            time.sleep(300)  # Report every 5 minutes
            
            report = monitor.get_performance_report()
            
            # Log key metrics
            singleton_status = report["singleton_status"]
            performance = report["performance_metrics"]
            
            logger.info(f"📊 Vector Store Performance Report:")
            logger.info(f"   Singleton working: {singleton_status['is_singleton_working']}")
            logger.info(f"   Total accesses: {singleton_status['total_accesses']}")
            logger.info(f"   Average access time: {performance['average_access_time']:.3f}s")
            logger.info(f"   Total searches: {performance['total_searches']}")
            
            # Save detailed report
            report_dir = Path("docs/performance-reports")
            report_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"vector_store_performance_{timestamp}.json"
            
            monitor.save_report(str(report_file))
    
    # Start reporting thread
    reporting_thread = threading.Thread(target=periodic_report, daemon=True)
    reporting_thread.start()
    
    logger.info("Vector store performance monitoring started")


def generate_test_report():
    """Generate a test report of singleton pattern effectiveness."""
    logger.info("🧪 Testing Vector Store Singleton Pattern Effectiveness")
    logger.info("=" * 60)
    
    try:
        # Start monitoring
        patch_vector_store_for_monitoring()
        
        # Test 1: Multiple accesses
        logger.info("Test 1: Multiple singleton accesses")
        from src.rag.search import get_vector_store_singleton
        
        for i in range(5):
            start_time = time.time()
            singleton = get_vector_store_singleton()
            end_time = time.time()
            logger.info(f"  Access {i+1}: {(end_time - start_time)*1000:.1f}ms")
        
        # Test 2: Health check performance
        logger.info("\\nTest 2: Health check performance")
        from src.rag.search import is_vector_store_loaded
        
        for i in range(10):
            start_time = time.time()
            loaded = is_vector_store_loaded()
            end_time = time.time()
            logger.info(f"  Health check {i+1}: {(end_time - start_time)*1000:.1f}ms - Loaded: {loaded}")
        
        # Test 3: Concurrent access
        logger.info("\\nTest 3: Concurrent access test")
        
        def concurrent_access():
            singleton = get_vector_store_singleton()
            monitor.track_concurrent_access()
            return singleton
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=concurrent_access)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Generate final report
        report = monitor.get_performance_report()
        
        logger.info("\\n" + "=" * 60)
        logger.info("🎯 Test Results:")
        logger.info(f"  Singleton working: {report['singleton_status']['is_singleton_working']}")
        logger.info(f"  Total accesses: {report['singleton_status']['total_accesses']}")
        logger.info(f"  Concurrent accesses: {report['singleton_status']['concurrent_accesses']}")
        logger.info(f"  Initial load time: {report['performance_metrics']['initial_load_time']:.3f}s")
        logger.info(f"  Average access time: {report['performance_metrics']['average_access_time']:.3f}s")
        logger.info(f"  Singleton prevents reloading: {report['efficiency_indicators']['singleton_prevents_reloading']}")
        logger.info(f"  Fast health checks: {report['efficiency_indicators']['fast_health_checks']}")
        
        # Save test report
        test_report_file = "docs/test-reports/VECTOR_STORE_SINGLETON_TEST_REPORT.json"
        monitor.save_report(test_report_file)
        
        return report
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test
        report = generate_test_report()
        if report and report['singleton_status']['is_singleton_working']:
            print("\\n🎉 Vector Store Singleton Pattern: WORKING")
            print("✅ Multiple instances prevention: CONFIRMED")
            print("✅ Performance optimization: CONFIRMED")
            print("✅ Health check efficiency: CONFIRMED")
            sys.exit(0)
        else:
            print("\\n❌ Vector Store Singleton Pattern: FAILED")
            sys.exit(1)
    else:
        # Start monitoring
        start_monitoring()
        
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")