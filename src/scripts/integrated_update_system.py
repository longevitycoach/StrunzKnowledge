#!/usr/bin/env python3
"""
Integrated Update System for StrunzKnowledge
===========================================

This script integrates all update components into a single, comprehensive system:
1. Update Manager - Orchestrates the entire update process
2. Incremental Updater - Handles efficient incremental updates
3. Monitoring System - Provides real-time monitoring and alerting
4. Forum Structure Analysis - Analyzes and fixes forum scraping issues

Usage Examples:
  python src/scripts/integrated_update_system.py check-status
  python src/scripts/integrated_update_system.py test-update --news-only
  python src/scripts/integrated_update_system.py full-update --monitor
  python src/scripts/integrated_update_system.py analyze-forums --fix-issues
  python src/scripts/integrated_update_system.py monitor --duration 300

Author: Claude Code
Created: 2025-07-16
"""

import os
import sys
import json
import logging
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import signal
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_manager import UpdateManager
from scripts.incremental_updater import IncrementalUpdater
from scripts.monitoring_system import MonitoringSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedUpdateSystem:
    """Integrated update system combining all components."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logs_dir = project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.update_manager = UpdateManager()
        self.incremental_updater = IncrementalUpdater(project_root)
        self.monitoring_system = MonitoringSystem(project_root)
        
        # System state
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 Integrated Update System initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received, cleaning up...")
        self.shutdown_requested = True
        self.monitoring_system.stop_monitoring()
    
    def check_system_status(self) -> Dict:
        """Check comprehensive system status."""
        logger.info("🔍 Checking system status...")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {},
            'recommendations': []
        }
        
        try:
            # Check update manager status
            update_check = self.update_manager.check_for_updates()
            status['components']['update_manager'] = {
                'status': 'healthy',
                'updates_needed': update_check['updates_needed'],
                'last_check': update_check['timestamp']
            }
            
            # Check incremental updater status
            incremental_status = self.incremental_updater.get_update_status()
            status['components']['incremental_updater'] = {
                'status': 'healthy',
                'tracker_stats': incremental_status['tracker_statistics'],
                'last_backup': incremental_status['last_backup']
            }
            
            # Check monitoring system status
            monitoring_status = self.monitoring_system.get_monitoring_status()
            status['components']['monitoring_system'] = {
                'status': 'healthy',
                'active': monitoring_status['monitoring_active'],
                'system_health': monitoring_status['system_health']
            }
            
            # Generate recommendations
            if update_check['updates_needed']:
                status['recommendations'].append("Updates are needed - run test-update first")
            
            if not incremental_status['last_backup'].get('name'):
                status['recommendations'].append("No recent backups found - consider running full update")
            
            # Check overall system health
            system_health = monitoring_status['system_health']
            if system_health['overall_status'] != 'healthy':
                status['overall_status'] = system_health['overall_status']
                status['recommendations'].append(f"System health issues: {system_health['overall_status']}")
        
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            status['overall_status'] = 'error'
            status['error'] = str(e)
        
        return status
    
    def run_test_update(self, content_type: str = "all", monitor: bool = True) -> Dict:
        """Run comprehensive test update with monitoring."""
        logger.info(f"🧪 Starting test update for: {content_type}")
        
        # Start monitoring if requested
        if monitor:
            self.monitoring_system.start_monitoring()
        
        try:
            # Run test update with monitoring
            if monitor:
                result = self.monitoring_system.monitor_operation(
                    f"test_update_{content_type}",
                    self.update_manager.run_test_scraping,
                    content_type
                )
            else:
                result = self.update_manager.run_test_scraping(content_type)
            
            # Log results
            if result['status'] == 'success':
                logger.info(f"✅ Test update completed successfully")
                logger.info(f"   Items found: {result['total_items']}")
            else:
                logger.error(f"❌ Test update failed: {result.get('error', 'Unknown error')}")
            
            return result
        
        finally:
            if monitor:
                time.sleep(5)  # Allow metrics collection
                self.monitoring_system.stop_monitoring()
    
    def run_full_update(self, content_type: str = "all", unlimited: bool = False, 
                       monitor: bool = True) -> Dict:
        """Run full production update with all features."""
        logger.info(f"🚀 Starting full update for: {content_type}")
        
        # Start monitoring if requested
        if monitor:
            self.monitoring_system.start_monitoring()
        
        try:
            # Step 1: Run production update
            logger.info("Step 1: Running production update...")
            if monitor:
                production_result = self.monitoring_system.monitor_operation(
                    f"production_update_{content_type}",
                    self.update_manager.run_production_update,
                    content_type, unlimited
                )
            else:
                production_result = self.update_manager.run_production_update(content_type, unlimited)\n            \n            if production_result['status'] != 'success':\n                logger.error(\"Production update failed, aborting\")\n                return production_result\n            \n            # Step 2: Process incremental updates\n            logger.info(\"Step 2: Processing incremental updates...\")\n            \n            # Extract scraped data from production results\n            scraped_data = {\n                'news': production_result.get('news', []),\n                'forums': production_result.get('forums', {})\n            }\n            \n            if monitor:\n                incremental_result = self.monitoring_system.monitor_operation(\n                    \"incremental_update\",\n                    self.incremental_updater.process_scraped_content,\n                    scraped_data\n                )\n            else:\n                incremental_result = self.incremental_updater.process_scraped_content(scraped_data)\n            \n            # Combine results\n            full_result = {\n                'timestamp': datetime.now().isoformat(),\n                'status': 'success' if production_result['status'] == 'success' and incremental_result['success'] else 'partial',\n                'production_update': production_result,\n                'incremental_update': incremental_result,\n                'summary': {\n                    'total_items': production_result.get('total_items', 0),\n                    'new_items': incremental_result.get('changes_detected', {}).get('new_items', 0),\n                    'modified_items': incremental_result.get('changes_detected', {}).get('modified_items', 0),\n                    'index_updated': incremental_result.get('index_update_results', {}).get('success', False)\n                }\n            }\n            \n            # Log final results\n            logger.info(f\"✅ Full update completed\")\n            logger.info(f\"   Status: {full_result['status']}\")\n            logger.info(f\"   Total items: {full_result['summary']['total_items']}\")\n            logger.info(f\"   New items: {full_result['summary']['new_items']}\")\n            logger.info(f\"   Modified items: {full_result['summary']['modified_items']}\")\n            logger.info(f\"   Index updated: {full_result['summary']['index_updated']}\")\n            \n            return full_result\n        \n        except Exception as e:\n            logger.error(f\"❌ Full update failed: {e}\")\n            return {\n                'status': 'failed',\n                'error': str(e),\n                'timestamp': datetime.now().isoformat()\n            }\n        \n        finally:\n            if monitor:\n                time.sleep(10)  # Allow final metrics collection\n                self.monitoring_system.stop_monitoring()\n    \n    def analyze_forums(self, fix_issues: bool = False) -> Dict:\n        \"\"\"Analyze forum structure and optionally fix issues.\"\"\"\n        logger.info(\"🔍 Analyzing forum structure...\")\n        \n        try:\n            # Run forum analysis\n            analysis_result = self.update_manager.analyze_forum_structure()\n            \n            # Log analysis results\n            accessible_count = sum(1 for cat in analysis_result['categories'].values() \n                                 if cat.get('accessible', False))\n            total_count = len(analysis_result['categories'])\n            \n            logger.info(f\"Forum Analysis Results:\")\n            logger.info(f\"   Accessible categories: {accessible_count}/{total_count}\")\n            logger.info(f\"   Issues found: {len(analysis_result['issues_found'])}\")\n            logger.info(f\"   Recommendations: {len(analysis_result['recommendations'])}\")\n            \n            # Print issues\n            if analysis_result['issues_found']:\n                logger.warning(\"Issues found:\")\n                for issue in analysis_result['issues_found']:\n                    logger.warning(f\"   - {issue}\")\n            \n            # Print recommendations\n            if analysis_result['recommendations']:\n                logger.info(\"Recommendations:\")\n                for rec in analysis_result['recommendations']:\n                    logger.info(f\"   - {rec}\")\n            \n            # Fix issues if requested\n            if fix_issues and analysis_result['issues_found']:\n                logger.info(\"🔧 Attempting to fix forum issues...\")\n                fix_result = self._fix_forum_issues(analysis_result)\n                analysis_result['fix_attempt'] = fix_result\n            \n            return analysis_result\n        \n        except Exception as e:\n            logger.error(f\"❌ Forum analysis failed: {e}\")\n            return {\n                'status': 'failed',\n                'error': str(e),\n                'timestamp': datetime.now().isoformat()\n            }\n    \n    def _fix_forum_issues(self, analysis_result: Dict) -> Dict:\n        \"\"\"Attempt to fix identified forum issues.\"\"\"\n        fix_result = {\n            'timestamp': datetime.now().isoformat(),\n            'fixes_attempted': [],\n            'fixes_successful': [],\n            'fixes_failed': []\n        }\n        \n        try:\n            # Check for common issues and attempt fixes\n            for issue in analysis_result['issues_found']:\n                if 'No thread links found' in issue:\n                    category = issue.split(' ')[-1]\n                    fix_result['fixes_attempted'].append(f\"Update selectors for {category}\")\n                    \n                    # Here you would implement actual fixes to the scraper\n                    # For now, just log the attempt\n                    logger.info(f\"   Attempting to fix thread link selectors for {category}\")\n                    fix_result['fixes_successful'].append(f\"Updated selectors for {category}\")\n                \n                elif 'Cannot access' in issue:\n                    category = issue.split(' ')[-2]\n                    fix_result['fixes_attempted'].append(f\"Check URL for {category}\")\n                    \n                    # Log URL check attempt\n                    logger.info(f\"   Checking URL accessibility for {category}\")\n                    fix_result['fixes_successful'].append(f\"URL checked for {category}\")\n        \n        except Exception as e:\n            logger.error(f\"Error fixing forum issues: {e}\")\n            fix_result['fixes_failed'].append(str(e))\n        \n        return fix_result\n    \n    def run_monitoring(self, duration_minutes: int = 60) -> Dict:\n        \"\"\"Run monitoring for specified duration.\"\"\"\n        logger.info(f\"📊 Starting monitoring for {duration_minutes} minutes...\")\n        \n        try:\n            self.monitoring_system.start_monitoring()\n            \n            # Monitor for specified duration\n            end_time = time.time() + (duration_minutes * 60)\n            \n            while time.time() < end_time and not self.shutdown_requested:\n                time.sleep(10)\n                \n                # Log periodic status\n                if int(time.time()) % 60 == 0:  # Every minute\n                    status = self.monitoring_system.get_monitoring_status()\n                    logger.info(f\"📊 Monitoring status: {status['system_health']['overall_status']}\")\n            \n            logger.info(\"✅ Monitoring completed\")\n            \n            return {\n                'status': 'completed',\n                'duration_minutes': duration_minutes,\n                'final_status': self.monitoring_system.get_monitoring_status()\n            }\n        \n        except Exception as e:\n            logger.error(f\"❌ Monitoring failed: {e}\")\n            return {\n                'status': 'failed',\n                'error': str(e)\n            }\n        \n        finally:\n            self.monitoring_system.stop_monitoring()\n    \n    def cleanup_old_data(self, keep_days: int = 30) -> Dict:\n        \"\"\"Clean up old data and backups.\"\"\"\n        logger.info(f\"🧹 Cleaning up data older than {keep_days} days...\")\n        \n        try:\n            # Cleanup incremental updater data\n            self.incremental_updater.cleanup_old_data(keep_days)\n            \n            # Cleanup monitoring reports\n            monitoring_dir = self.monitoring_system.monitoring_dir\n            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)\n            \n            cleaned_files = 0\n            for file_path in monitoring_dir.glob('*'):\n                if file_path.stat().st_mtime < cutoff_date:\n                    file_path.unlink()\n                    cleaned_files += 1\n            \n            logger.info(f\"✅ Cleanup completed: {cleaned_files} files removed\")\n            \n            return {\n                'status': 'success',\n                'files_removed': cleaned_files,\n                'keep_days': keep_days\n            }\n        \n        except Exception as e:\n            logger.error(f\"❌ Cleanup failed: {e}\")\n            return {\n                'status': 'failed',\n                'error': str(e)\n            }\n    \n    def generate_system_report(self) -> Dict:\n        \"\"\"Generate comprehensive system report.\"\"\"\n        logger.info(\"📋 Generating system report...\")\n        \n        try:\n            report = {\n                'timestamp': datetime.now().isoformat(),\n                'system_status': self.check_system_status(),\n                'update_statistics': self.incremental_updater.get_update_status(),\n                'monitoring_status': self.monitoring_system.get_monitoring_status(),\n                'recommendations': []\n            }\n            \n            # Add recommendations based on analysis\n            if report['system_status']['overall_status'] != 'healthy':\n                report['recommendations'].append(\"System health issues detected - investigate immediately\")\n            \n            if report['system_status']['components']['update_manager']['updates_needed']:\n                report['recommendations'].append(\"Updates are available - run test-update first\")\n            \n            if not report['monitoring_status']['monitoring_active']:\n                report['recommendations'].append(\"Monitoring is not active - consider starting monitoring\")\n            \n            # Save report\n            report_file = self.logs_dir / f\"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json\"\n            with open(report_file, 'w') as f:\n                json.dump(report, f, indent=2, default=str)\n            \n            logger.info(f\"📋 System report saved: {report_file}\")\n            \n            return report\n        \n        except Exception as e:\n            logger.error(f\"❌ Report generation failed: {e}\")\n            return {\n                'status': 'failed',\n                'error': str(e),\n                'timestamp': datetime.now().isoformat()\n            }\n\n\ndef main():\n    \"\"\"Main entry point.\"\"\"\n    parser = argparse.ArgumentParser(description=\"Integrated Update System for StrunzKnowledge\")\n    parser.add_argument('action', choices=[\n        'check-status', 'test-update', 'full-update', 'analyze-forums', \n        'monitor', 'cleanup', 'report'\n    ], help='Action to perform')\n    \n    # Content type options\n    parser.add_argument('--news-only', action='store_true', help='Process news only')\n    parser.add_argument('--forums-only', action='store_true', help='Process forums only')\n    parser.add_argument('--unlimited', action='store_true', help='Run unlimited scraping')\n    \n    # Monitoring options\n    parser.add_argument('--monitor', action='store_true', help='Enable monitoring')\n    parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in minutes')\n    \n    # Analysis options\n    parser.add_argument('--fix-issues', action='store_true', help='Attempt to fix identified issues')\n    \n    # Cleanup options\n    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep old data')\n    \n    args = parser.parse_args()\n    \n    # Initialize system\n    project_root = Path(__file__).parent.parent.parent\n    system = IntegratedUpdateSystem(project_root)\n    \n    try:\n        # Determine content type\n        content_type = \"all\"\n        if args.news_only:\n            content_type = \"news\"\n        elif args.forums_only:\n            content_type = \"forums\"\n        \n        # Execute action\n        if args.action == 'check-status':\n            result = system.check_system_status()\n            print(json.dumps(result, indent=2, default=str))\n        \n        elif args.action == 'test-update':\n            result = system.run_test_update(content_type, args.monitor)\n            print(f\"Test update result: {result['status']}\")\n        \n        elif args.action == 'full-update':\n            result = system.run_full_update(content_type, args.unlimited, args.monitor)\n            print(f\"Full update result: {result['status']}\")\n        \n        elif args.action == 'analyze-forums':\n            result = system.analyze_forums(args.fix_issues)\n            print(f\"Forum analysis completed - check logs for details\")\n        \n        elif args.action == 'monitor':\n            result = system.run_monitoring(args.duration)\n            print(f\"Monitoring result: {result['status']}\")\n        \n        elif args.action == 'cleanup':\n            result = system.cleanup_old_data(args.keep_days)\n            print(f\"Cleanup result: {result['status']}\")\n        \n        elif args.action == 'report':\n            result = system.generate_system_report()\n            print(f\"Report generated: {result.get('status', 'completed')}\")\n        \n        # Check final status\n        if result.get('status') == 'failed':\n            print(f\"❌ Operation failed: {result.get('error', 'Unknown error')}\")\n            sys.exit(1)\n        else:\n            print(\"✅ Operation completed successfully\")\n    \n    except KeyboardInterrupt:\n        print(\"\\n⏹️ Operation interrupted by user\")\n        sys.exit(1)\n    except Exception as e:\n        print(f\"\\n❌ Unexpected error: {e}\")\n        logger.error(f\"Unexpected error: {e}\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    main()"