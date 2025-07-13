"""
Resource monitoring for MCP server
Tracks memory, CPU, and performance metrics
"""
import psutil
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Prometheus metrics
cpu_usage_gauge = Gauge('mcp_cpu_usage_percent', 'CPU usage percentage')
memory_usage_gauge = Gauge('mcp_memory_usage_mb', 'Memory usage in MB')
memory_percent_gauge = Gauge('mcp_memory_usage_percent', 'Memory usage percentage')
request_count = Counter('mcp_requests_total', 'Total number of requests', ['endpoint', 'method'])
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration', ['endpoint'])
active_connections = Gauge('mcp_active_connections', 'Number of active connections')
faiss_search_duration = Histogram('mcp_faiss_search_seconds', 'FAISS search duration')
embedding_generation_duration = Histogram('mcp_embedding_generation_seconds', 'Embedding generation duration')

class ResourceMonitor:
    """Monitor system resources and application metrics"""
    
    def __init__(self, 
                 alert_memory_threshold_mb: int = 400,
                 alert_cpu_threshold_percent: int = 80,
                 log_interval_seconds: int = 60):
        """
        Initialize resource monitor
        
        Args:
            alert_memory_threshold_mb: Memory threshold for alerts
            alert_cpu_threshold_percent: CPU threshold for alerts
            log_interval_seconds: Interval for logging metrics
        """
        self.process = psutil.Process()
        self.alert_memory_threshold_mb = alert_memory_threshold_mb
        self.alert_cpu_threshold_percent = alert_cpu_threshold_percent
        self.log_interval_seconds = log_interval_seconds
        self.start_time = time.time()
        self.metrics_history: List[Dict] = []
        self.max_history_size = 1000
        
    def get_current_metrics(self) -> Dict:
        """Get current resource metrics"""
        # CPU metrics
        cpu_percent = self.process.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = self.process.memory_percent()
        
        # System metrics
        system_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        # Network connections
        try:
            connections = len(self.process.connections())
        except:
            connections = 0
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "per_core": cpu_percent / cpu_count if cpu_count > 0 else 0
            },
            "memory": {
                "used_mb": memory_mb,
                "percent": memory_percent,
                "available_mb": system_memory.available / 1024 / 1024,
                "total_mb": system_memory.total / 1024 / 1024
            },
            "disk": {
                "used_percent": disk_usage.percent,
                "free_gb": disk_usage.free / 1024 / 1024 / 1024
            },
            "connections": connections,
            "alerts": []
        }
        
        # Check for alerts
        if memory_mb > self.alert_memory_threshold_mb:
            metrics["alerts"].append({
                "type": "memory",
                "message": f"Memory usage ({memory_mb:.1f}MB) exceeds threshold ({self.alert_memory_threshold_mb}MB)",
                "severity": "warning"
            })
            
        if cpu_percent > self.alert_cpu_threshold_percent:
            metrics["alerts"].append({
                "type": "cpu",
                "message": f"CPU usage ({cpu_percent:.1f}%) exceeds threshold ({self.alert_cpu_threshold_percent}%)",
                "severity": "warning"
            })
            
        # Update Prometheus metrics
        cpu_usage_gauge.set(cpu_percent)
        memory_usage_gauge.set(memory_mb)
        memory_percent_gauge.set(memory_percent)
        active_connections.set(connections)
        
        return metrics
    
    async def start_monitoring(self):
        """Start background monitoring task"""
        while True:
            try:
                metrics = self.get_current_metrics()
                
                # Log metrics
                if metrics["alerts"]:
                    for alert in metrics["alerts"]:
                        logger.warning(f"Resource Alert: {alert['message']}")
                else:
                    logger.info(f"Resources OK - CPU: {metrics['cpu']['percent']:.1f}%, "
                              f"Memory: {metrics['memory']['used_mb']:.1f}MB")
                
                # Store in history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # Save snapshot for debugging
                self._save_metrics_snapshot(metrics)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                
            await asyncio.sleep(self.log_interval_seconds)
    
    def _save_metrics_snapshot(self, metrics: Dict):
        """Save metrics snapshot to file"""
        snapshot_dir = Path("logs/metrics")
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Keep only last 24 hours of snapshots
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = snapshot_dir / f"metrics_{timestamp}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(metrics, f, indent=2)
            
        # Clean old snapshots
        self._clean_old_snapshots(snapshot_dir)
    
    def _clean_old_snapshots(self, snapshot_dir: Path, keep_hours: int = 24):
        """Clean snapshots older than keep_hours"""
        cutoff_time = time.time() - (keep_hours * 3600)
        
        for file in snapshot_dir.glob("metrics_*.json"):
            if file.stat().st_mtime < cutoff_time:
                file.unlink()
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of metrics history"""
        if not self.metrics_history:
            return {}
            
        cpu_values = [m["cpu"]["percent"] for m in self.metrics_history]
        memory_values = [m["memory"]["used_mb"] for m in self.metrics_history]
        
        return {
            "period_minutes": len(self.metrics_history) * self.log_interval_seconds / 60,
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg_mb": sum(memory_values) / len(memory_values),
                "max_mb": max(memory_values),
                "min_mb": min(memory_values)
            },
            "alert_count": sum(len(m["alerts"]) for m in self.metrics_history)
        }
    
    def export_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        return generate_latest()


# Middleware for request tracking
class MetricsMiddleware:
    """FastAPI middleware for tracking request metrics"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Track request
            path = scope["path"]
            method = scope["method"]
            request_count.labels(endpoint=path, method=method).inc()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Record duration
                    duration = time.time() - start_time
                    request_duration.labels(endpoint=path).observe(duration)
                await send(message)
                
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


# Context manager for timing operations
class TimedOperation:
    """Context manager for timing operations"""
    
    def __init__(self, metric: Histogram, labels: Dict = None):
        self.metric = metric
        self.labels = labels or {}
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if self.labels:
            self.metric.labels(**self.labels).observe(duration)
        else:
            self.metric.observe(duration)