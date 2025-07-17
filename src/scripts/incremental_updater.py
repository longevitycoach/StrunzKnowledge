#!/usr/bin/env python3
"""
Incremental Update System for StrunzKnowledge
============================================

This system tracks changes and performs efficient incremental updates
to avoid re-processing unchanged content.

Features:
- Content change detection
- Incremental FAISS index updates
- Efficient diff-based processing
- Rollback capabilities
- Update history tracking

Author: Claude Code
Created: 2025-07-16
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import pickle
import shutil

logger = logging.getLogger(__name__)


class ContentTracker:
    """Track content changes for incremental updates."""
    
    def __init__(self, tracking_dir: Path):
        self.tracking_dir = tracking_dir
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        self.content_hashes_file = self.tracking_dir / "content_hashes.json"
        self.update_history_file = self.tracking_dir / "update_history.json"
        
        self.content_hashes = self._load_content_hashes()
        self.update_history = self._load_update_history()
    
    def _load_content_hashes(self) -> Dict:
        """Load existing content hashes."""
        if self.content_hashes_file.exists():
            try:
                with open(self.content_hashes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading content hashes: {e}")
        return {}
    
    def _save_content_hashes(self):
        """Save content hashes."""
        with open(self.content_hashes_file, 'w') as f:
            json.dump(self.content_hashes, f, indent=2)
    
    def _load_update_history(self) -> List:
        """Load update history."""
        if self.update_history_file.exists():
            try:
                with open(self.update_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading update history: {e}")
        return []
    
    def _save_update_history(self):
        """Save update history."""
        with open(self.update_history_file, 'w') as f:
            json.dump(self.update_history, f, indent=2, default=str)
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash for content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def track_content_changes(self, content_items: List[Dict]) -> Dict:
        """Track changes in content items."""
        changes = {
            'new_items': [],
            'modified_items': [],
            'unchanged_items': [],
            'deleted_items': []
        }
        
        current_urls = set()
        
        for item in content_items:
            url = item.get('source_url', '')
            content = item.get('content', '')
            
            if not url or not content:
                continue
                
            current_urls.add(url)
            content_hash = self._calculate_content_hash(content)
            
            if url not in self.content_hashes:
                # New item
                changes['new_items'].append(item)
                self.content_hashes[url] = {
                    'hash': content_hash,
                    'last_seen': datetime.now().isoformat(),
                    'first_seen': datetime.now().isoformat()
                }
            elif self.content_hashes[url]['hash'] != content_hash:
                # Modified item
                changes['modified_items'].append(item)
                self.content_hashes[url]['hash'] = content_hash
                self.content_hashes[url]['last_seen'] = datetime.now().isoformat()
            else:
                # Unchanged item
                changes['unchanged_items'].append(item)
                self.content_hashes[url]['last_seen'] = datetime.now().isoformat()
        
        # Find deleted items
        for url in list(self.content_hashes.keys()):
            if url not in current_urls:
                # Check if it's been missing for more than 7 days
                last_seen = datetime.fromisoformat(self.content_hashes[url]['last_seen'])
                if (datetime.now() - last_seen).days > 7:
                    changes['deleted_items'].append({'source_url': url})
                    del self.content_hashes[url]
        
        # Save updated hashes
        self._save_content_hashes()
        
        return changes
    
    def record_update(self, update_type: str, changes: Dict, success: bool):
        """Record update in history."""
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'update_type': update_type,
            'success': success,
            'changes_summary': {
                'new_items': len(changes.get('new_items', [])),
                'modified_items': len(changes.get('modified_items', [])),
                'unchanged_items': len(changes.get('unchanged_items', [])),
                'deleted_items': len(changes.get('deleted_items', []))
            }
        }
        
        self.update_history.append(update_record)
        
        # Keep only last 100 records
        if len(self.update_history) > 100:
            self.update_history = self.update_history[-100:]
        
        self._save_update_history()
    
    def get_update_statistics(self) -> Dict:
        """Get update statistics."""
        if not self.update_history:
            return {'no_history': True}
        
        recent_updates = [u for u in self.update_history if 
                         (datetime.now() - datetime.fromisoformat(u['timestamp'])).days <= 30]
        
        return {
            'total_updates': len(self.update_history),
            'recent_updates': len(recent_updates),
            'success_rate': sum(1 for u in self.update_history if u['success']) / len(self.update_history),
            'last_update': self.update_history[-1]['timestamp'],
            'tracked_urls': len(self.content_hashes)
        }


class IncrementalFAISSUpdater:
    """Perform incremental FAISS index updates."""
    
    def __init__(self, indices_dir: Path):
        self.indices_dir = indices_dir
        self.backup_dir = indices_dir / "incremental_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> str:
        """Create backup of current indices."""
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        
        if self.indices_dir.exists():
            shutil.copytree(self.indices_dir, backup_path, ignore=shutil.ignore_patterns('incremental_backups'))
            logger.info(f"Created backup: {backup_path}")
            return backup_name
        
        return ""
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore from backup."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        try:
            # Remove current indices
            if self.indices_dir.exists():
                shutil.rmtree(self.indices_dir)
            
            # Restore from backup
            shutil.copytree(backup_path, self.indices_dir)
            logger.info(f"Restored from backup: {backup_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def update_index_incrementally(self, new_items: List[Dict], modified_items: List[Dict], 
                                 deleted_items: List[Dict]) -> Dict:
        """Update FAISS index incrementally."""
        update_results = {
            'success': False,
            'backup_created': '',
            'items_added': 0,
            'items_modified': 0,
            'items_deleted': 0,
            'errors': []
        }
        
        try:
            # Create backup first
            backup_name = self.create_backup()
            update_results['backup_created'] = backup_name
            
            # Import vector store
            from src.rag.vector_store import FAISSVectorStore
            
            # Load existing vector store
            vector_store = FAISSVectorStore(index_path=str(self.indices_dir))
            
            # Process new items
            if new_items:
                logger.info(f"Adding {len(new_items)} new items to index")
                self._add_items_to_index(vector_store, new_items)
                update_results['items_added'] = len(new_items)
            
            # Process modified items
            if modified_items:
                logger.info(f"Updating {len(modified_items)} modified items in index")
                self._update_items_in_index(vector_store, modified_items)
                update_results['items_modified'] = len(modified_items)
            
            # Process deleted items
            if deleted_items:
                logger.info(f"Removing {len(deleted_items)} deleted items from index")
                self._remove_items_from_index(vector_store, deleted_items)
                update_results['items_deleted'] = len(deleted_items)
            
            # Save updated index
            vector_store.save_index()
            
            update_results['success'] = True
            logger.info("✅ Incremental index update completed successfully")
        
        except Exception as e:
            logger.error(f"❌ Error in incremental update: {e}")
            update_results['errors'].append(str(e))
            
            # Attempt to restore backup
            if backup_name:
                logger.info("Attempting to restore from backup...")
                if self.restore_backup(backup_name):
                    logger.info("Successfully restored from backup")
                else:
                    logger.error("Failed to restore from backup")
        
        return update_results
    
    def _add_items_to_index(self, vector_store, items: List[Dict]):
        """Add new items to the index."""
        for item in items:
            try:
                # Extract text content
                text = self._extract_text_from_item(item)
                if text:
                    vector_store.add_document(text, item)
            except Exception as e:
                logger.warning(f"Error adding item to index: {e}")
    
    def _update_items_in_index(self, vector_store, items: List[Dict]):
        """Update existing items in the index."""
        for item in items:
            try:
                # For now, treat updates as delete + add
                url = item.get('source_url', '')
                if url:
                    self._remove_items_from_index(vector_store, [item])
                    self._add_items_to_index(vector_store, [item])
            except Exception as e:
                logger.warning(f"Error updating item in index: {e}")
    
    def _remove_items_from_index(self, vector_store, items: List[Dict]):
        """Remove items from the index."""
        for item in items:
            try:
                url = item.get('source_url', '')
                if url and hasattr(vector_store, 'remove_document'):
                    vector_store.remove_document(url)
            except Exception as e:
                logger.warning(f"Error removing item from index: {e}")
    
    def _extract_text_from_item(self, item: Dict) -> str:
        """Extract text content from item."""
        parts = []
        
        if item.get('title'):
            parts.append(item['title'])
        
        if item.get('content'):
            parts.append(item['content'])
        
        return '\n\n'.join(parts)
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up old backups."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                try:
                    # Extract date from backup name
                    date_str = backup_dir.name.split('_')[1] + '_' + backup_dir.name.split('_')[2]
                    backup_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                    
                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_dir)
                        logger.info(f"Removed old backup: {backup_dir}")
                
                except Exception as e:
                    logger.warning(f"Error processing backup {backup_dir}: {e}")


class IncrementalUpdater:
    """Main incremental update coordinator."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.tracking_dir = self.data_dir / "tracking"
        self.indices_dir = self.data_dir / "faiss_indices"
        
        # Initialize components
        self.content_tracker = ContentTracker(self.tracking_dir)
        self.faiss_updater = IncrementalFAISSUpdater(self.indices_dir)
    
    def process_scraped_content(self, scraped_results: Dict) -> Dict:
        """Process scraped content and perform incremental updates."""
        logger.info("🔄 Starting incremental update process")
        
        update_results = {
            'timestamp': datetime.now().isoformat(),
            'total_items_processed': 0,
            'changes_detected': {},
            'index_update_results': {},
            'success': False
        }
        
        try:
            # Combine all content items
            all_items = []
            
            # Add news items
            news_items = scraped_results.get('news', [])
            all_items.extend(news_items)
            
            # Add forum items
            for category, posts in scraped_results.get('forums', {}).items():
                all_items.extend(posts)
            
            update_results['total_items_processed'] = len(all_items)
            
            # Track changes
            logger.info(f"Tracking changes for {len(all_items)} items")
            changes = self.content_tracker.track_content_changes(all_items)
            update_results['changes_detected'] = {
                'new_items': len(changes['new_items']),
                'modified_items': len(changes['modified_items']),
                'unchanged_items': len(changes['unchanged_items']),
                'deleted_items': len(changes['deleted_items'])
            }
            
            # Log changes
            logger.info(f"Changes detected:")
            logger.info(f"  New items: {len(changes['new_items'])}")
            logger.info(f"  Modified items: {len(changes['modified_items'])}")
            logger.info(f"  Unchanged items: {len(changes['unchanged_items'])}")
            logger.info(f"  Deleted items: {len(changes['deleted_items'])}")
            
            # Perform incremental FAISS update if there are changes
            if changes['new_items'] or changes['modified_items'] or changes['deleted_items']:
                logger.info("Performing incremental FAISS update")
                
                index_results = self.faiss_updater.update_index_incrementally(
                    changes['new_items'],
                    changes['modified_items'],
                    changes['deleted_items']
                )
                
                update_results['index_update_results'] = index_results
                
                if index_results['success']:
                    logger.info("✅ Incremental FAISS update completed successfully")
                    update_results['success'] = True
                else:
                    logger.error("❌ Incremental FAISS update failed")
                    update_results['success'] = False
            else:
                logger.info("No changes detected - skipping index update")
                update_results['success'] = True
                update_results['index_update_results'] = {'skipped': True}
            
            # Record update in history
            self.content_tracker.record_update('incremental', changes, update_results['success'])
            
        except Exception as e:
            logger.error(f"❌ Error in incremental update: {e}")
            update_results['success'] = False
            update_results['error'] = str(e)
        
        return update_results
    
    def get_update_status(self) -> Dict:
        """Get current update status."""
        return {
            'tracker_statistics': self.content_tracker.get_update_statistics(),
            'last_backup': self._get_last_backup_info(),
            'index_health': self._check_index_health()
        }
    
    def _get_last_backup_info(self) -> Dict:
        """Get information about the last backup."""
        try:
            backups = list(self.faiss_updater.backup_dir.glob('backup_*'))
            if backups:
                latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
                return {
                    'name': latest_backup.name,
                    'created': datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat(),
                    'size_mb': sum(f.stat().st_size for f in latest_backup.rglob('*') if f.is_file()) / (1024 * 1024)
                }
        except Exception as e:
            logger.warning(f"Error getting backup info: {e}")
        
        return {'no_backups': True}
    
    def _check_index_health(self) -> Dict:
        """Check health of current indices."""
        try:
            index_file = self.indices_dir / "combined_index.faiss"
            metadata_file = self.indices_dir / "combined_metadata.json"
            
            return {
                'index_exists': index_file.exists(),
                'metadata_exists': metadata_file.exists(),
                'index_size_mb': index_file.stat().st_size / (1024 * 1024) if index_file.exists() else 0,
                'last_modified': datetime.fromtimestamp(index_file.stat().st_mtime).isoformat() if index_file.exists() else None
            }
        except Exception as e:
            logger.warning(f"Error checking index health: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, keep_days: int = 30):
        """Clean up old tracking data and backups."""
        logger.info(f"Cleaning up data older than {keep_days} days")
        
        # Cleanup backups
        self.faiss_updater.cleanup_old_backups(keep_days)
        
        # TODO: Add cleanup for old tracking data if needed
        logger.info("✅ Cleanup completed")