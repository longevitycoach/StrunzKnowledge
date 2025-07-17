#!/usr/bin/env python3
"""
Comprehensive Monitoring and Logging System for StrunzKnowledge
==============================================================

This system provides:
- Real-time monitoring of scraping operations
- Detailed logging and reporting
- Performance metrics tracking
- Error detection and alerting
- Health checks and status reporting

Author: Claude Code
Created: 2025-07-16
"""

import os
import json
import logging
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import signal
import sys


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_threads: int
    open_files: int
    network_connections: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ScrapingMetrics:
    """Metrics specific to scraping operations."""
    timestamp: datetime
    operation_type: str
    items_processed: int
    items_per_second: float
    errors_count: int
    success_rate: float
    avg_response_time: float
    categories_completed: int
    categories_failed: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MetricsCollector:
    """Collect and store performance metrics."""
    
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.performance_metrics = deque(maxlen=max_metrics)
        self.scraping_metrics = deque(maxlen=max_metrics)
        self.error_log = deque(maxlen=max_metrics)
        self.lock = threading.Lock()
        self.collection_active = False
        self.collection_thread = None
        self.collection_interval = 5.0  # seconds
    
    def start_collection(self):
        """Start automatic metrics collection."""
        if not self.collection_active:
            self.collection_active = True
            self.collection_thread = threading.Thread(target=self._collect_metrics_loop)
            self.collection_thread.daemon = True
            self.collection_thread.start()
            logging.info("📊 Metrics collection started")
    
    def stop_collection(self):
        """Stop automatic metrics collection."""
        self.collection_active = False
        if self.collection_thread:
            self.collection_thread.join(timeout=1.0)
        logging.info("📊 Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Background thread for metrics collection."""
        while self.collection_active:
            try:
                self.collect_performance_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logging.warning(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval)
    
    def collect_performance_metrics(self):
        """Collect current performance metrics."""
        try:
            process = psutil.Process()
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process metrics
            process_memory = process.memory_info()
            open_files = len(process.open_files())
            threads = process.num_threads()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=process_memory.rss / (1024 * 1024),
                disk_usage_percent=disk.percent,
                active_threads=threads,
                open_files=open_files
            )
            
            with self.lock:
                self.performance_metrics.append(metrics)
        
        except Exception as e:
            logging.warning(f"Error collecting performance metrics: {e}")
    
    def record_scraping_metrics(self, operation_type: str, items_processed: int, 
                              duration_seconds: float, errors_count: int, 
                              categories_completed: int = 0, categories_failed: int = 0):
        """Record scraping operation metrics."""
        try:
            items_per_second = items_processed / duration_seconds if duration_seconds > 0 else 0
            success_rate = (items_processed - errors_count) / items_processed if items_processed > 0 else 0
            
            metrics = ScrapingMetrics(
                timestamp=datetime.now(),
                operation_type=operation_type,
                items_processed=items_processed,
                items_per_second=items_per_second,
                errors_count=errors_count,
                success_rate=success_rate,
                avg_response_time=duration_seconds / items_processed if items_processed > 0 else 0,
                categories_completed=categories_completed,
                categories_failed=categories_failed
            )
            
            with self.lock:
                self.scraping_metrics.append(metrics)
        
        except Exception as e:
            logging.warning(f"Error recording scraping metrics: {e}")
    
    def record_error(self, error_type: str, error_message: str, context: Dict = None):
        """Record error information."""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        with self.lock:
            self.error_log.append(error_info)
    
    def get_recent_metrics(self, minutes: int = 10) -> Dict:
        """Get metrics from the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_performance = [m for m in self.performance_metrics if m.timestamp >= cutoff_time]
            recent_scraping = [m for m in self.scraping_metrics if m.timestamp >= cutoff_time]
            recent_errors = [e for e in self.error_log if datetime.fromisoformat(e['timestamp']) >= cutoff_time]
        
        return {
            'time_window_minutes': minutes,
            'performance_metrics': [m.to_dict() for m in recent_performance],
            'scraping_metrics': [m.to_dict() for m in recent_scraping],
            'errors': recent_errors
        }
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics."""
        with self.lock:
            perf_metrics = list(self.performance_metrics)
            scraping_metrics = list(self.scraping_metrics)
            errors = list(self.error_log)
        
        summary = {
            'data_points': {
                'performance_metrics': len(perf_metrics),
                'scraping_metrics': len(scraping_metrics),
                'errors': len(errors)
            },
            'time_range': {},
            'performance_summary': {},
            'scraping_summary': {},
            'error_summary': {}
        }
        
        if perf_metrics:
            summary['time_range'] = {
                'start': perf_metrics[0].timestamp.isoformat(),
                'end': perf_metrics[-1].timestamp.isoformat()
            }
            
            # Performance statistics
            cpu_values = [m.cpu_percent for m in perf_metrics]
            memory_values = [m.memory_used_mb for m in perf_metrics]
            
            summary['performance_summary'] = {
                'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                'max_cpu_percent': max(cpu_values),
                'avg_memory_mb': sum(memory_values) / len(memory_values),
                'max_memory_mb': max(memory_values),
                'avg_threads': sum(m.active_threads for m in perf_metrics) / len(perf_metrics)
            }
        
        if scraping_metrics:
            # Scraping statistics
            total_items = sum(m.items_processed for m in scraping_metrics)
            total_errors = sum(m.errors_count for m in scraping_metrics)
            
            summary['scraping_summary'] = {
                'total_items_processed': total_items,
                'total_errors': total_errors,
                'avg_items_per_second': sum(m.items_per_second for m in scraping_metrics) / len(scraping_metrics),
                'avg_success_rate': sum(m.success_rate for m in scraping_metrics) / len(scraping_metrics),
                'operations_count': len(scraping_metrics)
            }
        
        if errors:
            # Error statistics
            error_types = defaultdict(int)
            for error in errors:
                error_types[error['error_type']] += 1
            
            summary['error_summary'] = {
                'total_errors': len(errors),
                'error_types': dict(error_types),
                'recent_errors': len([e for e in errors if 
                                   (datetime.now() - datetime.fromisoformat(e['timestamp'])).hours < 1])
            }
        
        return summary


class AlertSystem:
    """Alert system for monitoring thresholds."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'error_rate': 0.1,  # 10%
            'items_per_second_min': 0.5
        }
        self.alert_cooldowns = {}  # Prevent spam alerts
        self.cooldown_period = 300  # 5 minutes
    
    def check_alerts(self) -> List[Dict]:
        """Check for alert conditions."""
        alerts = []
        current_time = datetime.now()
        
        try:
            # Get recent metrics
            recent_metrics = self.metrics_collector.get_recent_metrics(minutes=5)
            
            # Check performance alerts
            if recent_metrics['performance_metrics']:
                latest_perf = recent_metrics['performance_metrics'][-1]
                
                # CPU alert
                if latest_perf['cpu_percent'] > self.alert_thresholds['cpu_percent']:
                    alert = self._create_alert('high_cpu', f"CPU usage: {latest_perf['cpu_percent']:.1f}%")
                    if alert:
                        alerts.append(alert)
                
                # Memory alert
                if latest_perf['memory_percent'] > self.alert_thresholds['memory_percent']:
                    alert = self._create_alert('high_memory', f"Memory usage: {latest_perf['memory_percent']:.1f}%")
                    if alert:
                        alerts.append(alert)
                
                # Disk alert
                if latest_perf['disk_usage_percent'] > self.alert_thresholds['disk_usage_percent']:
                    alert = self._create_alert('high_disk', f"Disk usage: {latest_perf['disk_usage_percent']:.1f}%")
                    if alert:
                        alerts.append(alert)
            
            # Check scraping alerts
            if recent_metrics['scraping_metrics']:
                latest_scraping = recent_metrics['scraping_metrics'][-1]
                
                # Low performance alert
                if latest_scraping['items_per_second'] < self.alert_thresholds['items_per_second_min']:
                    alert = self._create_alert('low_performance', 
                                             f"Items/sec: {latest_scraping['items_per_second']:.2f}")
                    if alert:
                        alerts.append(alert)
                
                # High error rate alert
                if latest_scraping['success_rate'] < (1 - self.alert_thresholds['error_rate']):
                    alert = self._create_alert('high_error_rate', 
                                             f"Success rate: {latest_scraping['success_rate']:.2f}")
                    if alert:
                        alerts.append(alert)
            
            # Check error alerts
            if len(recent_metrics['errors']) > 5:  # More than 5 errors in 5 minutes
                alert = self._create_alert('high_error_count', 
                                         f"Errors in 5 min: {len(recent_metrics['errors'])}")
                if alert:
                    alerts.append(alert)
        
        except Exception as e:
            logging.warning(f"Error checking alerts: {e}")
        
        return alerts
    
    def _create_alert(self, alert_type: str, message: str) -> Optional[Dict]:
        """Create alert if not in cooldown."""
        current_time = datetime.now()
        
        # Check cooldown
        if alert_type in self.alert_cooldowns:
            last_alert = self.alert_cooldowns[alert_type]
            if (current_time - last_alert).seconds < self.cooldown_period:
                return None
        
        # Create alert
        alert = {
            'timestamp': current_time.isoformat(),
            'alert_type': alert_type,
            'message': message,
            'severity': self._get_alert_severity(alert_type)
        }
        
        # Update cooldown
        self.alert_cooldowns[alert_type] = current_time
        
        return alert
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level."""
        severity_map = {
            'high_cpu': 'warning',
            'high_memory': 'warning',
            'high_disk': 'critical',
            'low_performance': 'warning',
            'high_error_rate': 'critical',
            'high_error_count': 'warning'
        }
        return severity_map.get(alert_type, 'info')


class MonitoringSystem:
    """Main monitoring system coordinator."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logs_dir = project_root / "logs"
        self.monitoring_dir = self.logs_dir / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_system = AlertSystem(self.metrics_collector)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Configure logging
        self._setup_monitoring_logging()
    
    def _setup_monitoring_logging(self):
        """Setup monitoring-specific logging."""
        log_file = self.logs_dir / "monitoring.log"
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        logger = logging.getLogger('monitoring')
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logging.info("Received shutdown signal, stopping monitoring...")
        self.stop_monitoring()
    
    def start_monitoring(self):
        """Start comprehensive monitoring."""
        if self.monitoring_active:
            logging.warning("Monitoring already active")
            return
        
        logging.info("🚀 Starting comprehensive monitoring system")
        
        self.monitoring_active = True
        self.shutdown_event.clear()
        
        # Start metrics collection
        self.metrics_collector.start_collection()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logging.info("✅ Monitoring system started successfully")
    
    def stop_monitoring(self):
        """Stop monitoring system."""
        if not self.monitoring_active:
            return
        
        logging.info("🛑 Stopping monitoring system")
        
        self.monitoring_active = False
        self.shutdown_event.set()
        
        # Stop metrics collection
        self.metrics_collector.stop_collection()
        
        # Wait for monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        # Save final report
        self._save_monitoring_report()
        
        logging.info("✅ Monitoring system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        report_interval = 60  # Generate report every minute
        alert_check_interval = 30  # Check alerts every 30 seconds
        
        last_report = time.time()
        last_alert_check = time.time()
        
        while self.monitoring_active and not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Check alerts
                if current_time - last_alert_check >= alert_check_interval:
                    alerts = self.alert_system.check_alerts()
                    if alerts:
                        self._process_alerts(alerts)
                    last_alert_check = current_time
                
                # Generate report
                if current_time - last_report >= report_interval:
                    self._generate_monitoring_report()
                    last_report = current_time
                
                # Sleep
                self.shutdown_event.wait(10)  # Check every 10 seconds
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                self.shutdown_event.wait(10)
    
    def _process_alerts(self, alerts: List[Dict]):
        """Process triggered alerts."""
        for alert in alerts:
            logger = logging.getLogger('monitoring')
            
            if alert['severity'] == 'critical':
                logger.critical(f"🚨 CRITICAL ALERT: {alert['message']}")
            elif alert['severity'] == 'warning':
                logger.warning(f"⚠️ WARNING: {alert['message']}")
            else:
                logger.info(f"ℹ️ INFO: {alert['message']}")
    
    def _generate_monitoring_report(self):
        """Generate monitoring report."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.monitoring_dir / f"monitoring_report_{timestamp}.json"
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.metrics_collector.get_summary_statistics(),
                'recent_metrics': self.metrics_collector.get_recent_metrics(minutes=10),
                'system_health': self._get_system_health()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Keep only last 100 reports
            reports = list(self.monitoring_dir.glob('monitoring_report_*.json'))
            if len(reports) > 100:
                reports.sort(key=lambda f: f.stat().st_mtime)
                for old_report in reports[:-100]:
                    old_report.unlink()
        
        except Exception as e:
            logging.error(f"Error generating monitoring report: {e}")
    
    def _save_monitoring_report(self):
        """Save final monitoring report."""
        try:
            final_report = {
                'timestamp': datetime.now().isoformat(),
                'session_summary': self.metrics_collector.get_summary_statistics(),
                'final_metrics': self.metrics_collector.get_recent_metrics(minutes=60)
            }
            
            report_file = self.monitoring_dir / f"final_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            logging.info(f"📊 Final monitoring report saved: {report_file}")
        
        except Exception as e:
            logging.error(f"Error saving final monitoring report: {e}")
    
    def _get_system_health(self) -> Dict:
        """Get current system health status."""
        health = {
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health['checks']['cpu'] = {
                'value': cpu_percent,
                'status': 'critical' if cpu_percent > 90 else 'warning' if cpu_percent > 80 else 'healthy'
            }
            
            health['checks']['memory'] = {
                'value': memory.percent,
                'status': 'critical' if memory.percent > 90 else 'warning' if memory.percent > 80 else 'healthy'
            }
            
            health['checks']['disk'] = {
                'value': disk.percent,
                'status': 'critical' if disk.percent > 95 else 'warning' if disk.percent > 90 else 'healthy'
            }
            
            # Check if any critical issues
            critical_checks = [check for check in health['checks'].values() if check['status'] == 'critical']
            if critical_checks:
                health['overall_status'] = 'critical'
            elif any(check['status'] == 'warning' for check in health['checks'].values()):
                health['overall_status'] = 'warning'
            
            # Check data directories
            data_dir = self.project_root / "data"
            if not data_dir.exists():
                health['errors'].append("Data directory missing")
                health['overall_status'] = 'critical'
            
            # Check indices
            indices_dir = data_dir / "faiss_indices"
            if indices_dir.exists():
                index_file = indices_dir / "combined_index.faiss"
                if index_file.exists():
                    health['checks']['faiss_index'] = {'status': 'healthy'}
                else:
                    health['warnings'].append("FAISS index file missing")
                    health['checks']['faiss_index'] = {'status': 'warning'}
            else:
                health['warnings'].append("FAISS indices directory missing")
                health['checks']['faiss_index'] = {'status': 'warning'}
        
        except Exception as e:
            health['errors'].append(f"Error checking system health: {e}")
            health['overall_status'] = 'error'
        
        return health
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            'monitoring_active': self.monitoring_active,
            'metrics_collection_active': self.metrics_collector.collection_active,
            'summary_statistics': self.metrics_collector.get_summary_statistics(),
            'system_health': self._get_system_health()
        }
    
    def monitor_operation(self, operation_name: str, operation_func: Callable, *args, **kwargs):
        """Monitor a specific operation."""
        logger = logging.getLogger('monitoring')
        logger.info(f"🔍 Starting monitoring for operation: {operation_name}")
        
        start_time = time.time()
        items_processed = 0
        errors_count = 0
        
        try:
            # Start metrics collection if not already active
            if not self.metrics_collector.collection_active:
                self.metrics_collector.start_collection()
            
            # Execute operation
            result = operation_func(*args, **kwargs)
            
            # Extract metrics from result if available
            if isinstance(result, dict):
                items_processed = result.get('total_items', 0)
                errors_count = result.get('errors_count', 0)
            
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics_collector.record_scraping_metrics(
                operation_name, items_processed, duration, errors_count
            )
            
            logger.info(f"✅ Operation completed: {operation_name}")
            logger.info(f"   Duration: {duration:.2f}s")
            logger.info(f"   Items processed: {items_processed}")
            logger.info(f"   Errors: {errors_count}")
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            self.metrics_collector.record_error(operation_name, str(e), {
                'duration': duration,
                'items_processed': items_processed
            })
            
            logger.error(f"❌ Operation failed: {operation_name}")
            logger.error(f"   Error: {e}")
            logger.error(f"   Duration: {duration:.2f}s")
            
            raise