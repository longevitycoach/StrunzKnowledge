#!/usr/bin/env python3
"""
Cleanup old FAISS index files to save storage space
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexCleaner:
    def __init__(self, keep_last=3):
        self.data_dir = Path("data")
        self.indices_dir = self.data_dir / "faiss_indices"
        self.keep_last = keep_last
        
    def group_indices_by_type(self):
        """Group index files by their type and sort by timestamp."""
        grouped = {}
        
        # Pattern to extract timestamp from filename
        timestamp_pattern = r'(\d{8}_\d{6})'
        
        for index_file in self.indices_dir.rglob("*.faiss"):
            # Skip combined index
            if index_file.name == "combined_index.faiss":
                continue
            
            # Extract type and timestamp
            match = re.search(timestamp_pattern, index_file.name)
            if match:
                timestamp = match.group(1)
                
                # Determine type from path or filename
                if 'news' in str(index_file):
                    index_type = 'news'
                elif 'forum' in str(index_file):
                    index_type = 'forum'
                elif 'books' in str(index_file):
                    index_type = 'books'
                else:
                    index_type = 'other'
                
                if index_type not in grouped:
                    grouped[index_type] = []
                
                grouped[index_type].append({
                    'file': index_file,
                    'timestamp': timestamp,
                    'metadata': index_file.with_suffix('.json')
                })
        
        # Sort each group by timestamp (newest first)
        for index_type in grouped:
            grouped[index_type].sort(key=lambda x: x['timestamp'], reverse=True)
        
        return grouped
    
    def cleanup_old_indices(self):
        """Remove old index files, keeping only the most recent ones."""
        grouped = self.group_indices_by_type()
        
        total_removed = 0
        total_size_saved = 0
        
        for index_type, indices in grouped.items():
            logger.info(f"\nProcessing {index_type} indices:")
            logger.info(f"  Found {len(indices)} index files")
            
            if len(indices) <= self.keep_last:
                logger.info(f"  Keeping all {len(indices)} files (≤ {self.keep_last})")
                continue
            
            # Keep the most recent ones, remove the rest
            to_keep = indices[:self.keep_last]
            to_remove = indices[self.keep_last:]
            
            logger.info(f"  Keeping {len(to_keep)} most recent files")
            logger.info(f"  Removing {len(to_remove)} old files")
            
            for item in to_remove:
                index_file = item['file']
                metadata_file = item['metadata']
                
                # Calculate size before removal
                size = 0
                if index_file.exists():
                    size += index_file.stat().st_size
                if metadata_file.exists():
                    size += metadata_file.stat().st_size
                
                # Remove files
                try:
                    if index_file.exists():
                        index_file.unlink()
                        logger.info(f"    Removed: {index_file.name}")
                    
                    if metadata_file.exists():
                        metadata_file.unlink()
                        logger.info(f"    Removed: {metadata_file.name}")
                    
                    total_removed += 1
                    total_size_saved += size
                    
                except Exception as e:
                    logger.error(f"    Error removing {index_file.name}: {e}")
        
        logger.info(f"\n✅ Cleanup complete:")
        logger.info(f"   Files removed: {total_removed * 2}")  # *2 for index + metadata
        logger.info(f"   Space saved: {total_size_saved / (1024*1024):.1f} MB")
        
        return total_removed > 0
    
    def list_indices(self):
        """List all current indices."""
        grouped = self.group_indices_by_type()
        
        print("\n📁 Current FAISS Indices:")
        
        for index_type, indices in grouped.items():
            print(f"\n{index_type.upper()}:")
            for i, item in enumerate(indices):
                marker = "🔸" if i < self.keep_last else "🗑️"
                size_mb = item['file'].stat().st_size / (1024*1024) if item['file'].exists() else 0
                print(f"  {marker} {item['file'].name} ({size_mb:.1f} MB)")
        
        # Show combined index
        combined = self.indices_dir / "combined_index.faiss"
        if combined.exists():
            size_mb = combined.stat().st_size / (1024*1024)
            print(f"\nCOMBINED:")
            print(f"  🔸 {combined.name} ({size_mb:.1f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Cleanup old FAISS index files")
    parser.add_argument("--keep-last", type=int, default=3,
                        help="Number of recent index files to keep per type (default: 3)")
    parser.add_argument("--list-only", action="store_true",
                        help="Only list current indices, don't remove anything")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be removed without actually removing")
    
    args = parser.parse_args()
    
    cleaner = IndexCleaner(keep_last=args.keep_last)
    
    if args.list_only:
        cleaner.list_indices()
    elif args.dry_run:
        logger.info("DRY RUN - No files will be removed")
        cleaner.list_indices()
        # TODO: Add dry run logic
    else:
        if cleaner.cleanup_old_indices():
            exit(0)  # Changes made
        else:
            exit(0)  # No changes needed

if __name__ == "__main__":
    main()