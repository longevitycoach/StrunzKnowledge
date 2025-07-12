#!/usr/bin/env python3
"""
Forum Update Tracker - Tracks wget download runs and manages delta updates
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
import hashlib
import shutil

class ForumUpdateTracker:
    def __init__(self, data_dir: str = "data/raw/forum", metadata_file: str = "data/update_metadata.json"):
        self.data_dir = Path(data_dir)
        self.metadata_file = Path(metadata_file)
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load or initialize metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            "last_run": None,
            "file_hashes": {},
            "run_history": [],
            "categories": {}
        }
    
    def _save_metadata(self):
        """Save metadata to file"""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def scan_current_files(self) -> Dict[str, Dict]:
        """Scan all current HTML files and calculate hashes"""
        current_files = {}
        
        for category_dir in self.data_dir.glob("*"):
            if category_dir.is_dir():
                category = category_dir.name
                for html_file in category_dir.glob("**/*.html"):
                    rel_path = str(html_file.relative_to(self.data_dir))
                    file_stat = html_file.stat()
                    current_files[rel_path] = {
                        "category": category,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "hash": self._calculate_file_hash(html_file)
                    }
        
        return current_files
    
    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect new, modified, and deleted files since last run"""
        current_files = self.scan_current_files()
        old_hashes = self.metadata.get("file_hashes", {})
        
        changes = {
            "new": [],
            "modified": [],
            "deleted": [],
            "unchanged": []
        }
        
        # Check for new and modified files
        for file_path, file_info in current_files.items():
            if file_path not in old_hashes:
                changes["new"].append(file_path)
            elif file_info["hash"] != old_hashes[file_path]["hash"]:
                changes["modified"].append(file_path)
            else:
                changes["unchanged"].append(file_path)
        
        # Check for deleted files
        for file_path in old_hashes:
            if file_path not in current_files:
                changes["deleted"].append(file_path)
        
        return changes
    
    def record_run_start(self, run_type: str = "full"):
        """Record the start of a wget run"""
        run_info = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "type": run_type,
            "status": "running"
        }
        
        self.metadata["current_run"] = run_info
        self._save_metadata()
        
        return run_info["id"]
    
    def record_run_complete(self, run_id: str):
        """Record completion of a wget run and update file hashes"""
        if "current_run" not in self.metadata:
            raise ValueError("No run in progress")
        
        # Scan current files
        current_files = self.scan_current_files()
        changes = self.detect_changes()
        
        # Update run info
        run_info = self.metadata["current_run"]
        run_info["end_time"] = datetime.now().isoformat()
        run_info["status"] = "completed"
        run_info["changes"] = {
            "new_files": len(changes["new"]),
            "modified_files": len(changes["modified"]),
            "deleted_files": len(changes["deleted"]),
            "total_files": len(current_files)
        }
        
        # Update metadata
        self.metadata["last_run"] = run_info["end_time"]
        self.metadata["file_hashes"] = current_files
        self.metadata["run_history"].append(run_info)
        del self.metadata["current_run"]
        
        # Keep only last 10 runs in history
        if len(self.metadata["run_history"]) > 10:
            self.metadata["run_history"] = self.metadata["run_history"][-10:]
        
        self._save_metadata()
        
        return changes
    
    def create_delta_package(self, changes: Dict[str, List[str]], output_dir: str = "data/raw/delta"):
        """Create a package of changed files for FAISS update"""
        output_path = Path(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        delta_dir = output_path / f"delta_{timestamp}"
        delta_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy new and modified files
        for file_path in changes["new"] + changes["modified"]:
            src_file = self.data_dir / file_path
            dst_file = delta_dir / "files" / file_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
        
        # Save delta metadata
        delta_metadata = {
            "timestamp": timestamp,
            "created": datetime.now().isoformat(),
            "changes": changes,
            "file_count": len(changes["new"]) + len(changes["modified"])
        }
        
        with open(delta_dir / "delta_metadata.json", 'w') as f:
            json.dump(delta_metadata, f, indent=2)
        
        print(f"Delta package created: {delta_dir}")
        print(f"  - New files: {len(changes['new'])}")
        print(f"  - Modified files: {len(changes['modified'])}")
        print(f"  - Deleted files: {len(changes['deleted'])}")
        
        return delta_dir
    
    def get_last_run_info(self) -> Optional[Dict]:
        """Get information about the last run"""
        if self.metadata["run_history"]:
            return self.metadata["run_history"][-1]
        return None
    
    def run_forum_update(self, categories: List[str] = None):
        """Run wget update for specified categories"""
        if categories is None:
            categories = ["fitness", "ernaehrung", "gesundheit", "bluttuning", "mental", "infektion-und-praevention"]
        
        run_id = self.record_run_start("update")
        
        print(f"Starting forum update run: {run_id}")
        print(f"Categories: {', '.join(categories)}")
        
        # Run wget for each category
        for category in categories:
            print(f"\nUpdating category: {category}")
            
            # Build wget command
            cmd = [
                "wget",
                "--recursive",
                "--level=5",
                "--directory-prefix=data/raw/forum",
                "--no-host-directories",
                "--cut-dirs=1",
                "--page-requisites",
                "--html-extension",
                "--convert-links",
                f"--domains=strunz.com,www.strunz.com",
                "--no-parent",
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "--wait=1",
                "--random-wait",
                f"--accept-regex=.*{category}.*",
                "--reject-regex=.*\\.(jpg|jpeg|png|gif|ico|css|js|exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$",
                "--timestamping",  # Only download newer files
                f"https://www.strunz.com/forum/{category}"
            ]
            
            # Run wget
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"  ✓ {category} updated successfully")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Error updating {category}: {e}")
        
        # Record completion and get changes
        changes = self.record_run_complete(run_id)
        
        # Create delta package if there are changes
        if changes["new"] or changes["modified"]:
            self.create_delta_package(changes)
        else:
            print("\nNo changes detected in this update run")
        
        return changes


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Forum Update Tracker")
    parser.add_argument("command", choices=["status", "update", "delta", "history"], 
                       help="Command to run")
    parser.add_argument("--categories", nargs="+", 
                       help="Categories to update (for update command)")
    
    args = parser.parse_args()
    
    tracker = ForumUpdateTracker()
    
    if args.command == "status":
        last_run = tracker.get_last_run_info()
        if last_run:
            print(f"Last run: {last_run['end_time']}")
            print(f"Type: {last_run['type']}")
            print(f"Changes: {last_run['changes']}")
        else:
            print("No previous runs found")
        
        changes = tracker.detect_changes()
        print(f"\nChanges since last run:")
        print(f"  - New files: {len(changes['new'])}")
        print(f"  - Modified files: {len(changes['modified'])}")
        print(f"  - Deleted files: {len(changes['deleted'])}")
    
    elif args.command == "update":
        tracker.run_forum_update(args.categories)
    
    elif args.command == "delta":
        changes = tracker.detect_changes()
        if changes["new"] or changes["modified"]:
            tracker.create_delta_package(changes)
        else:
            print("No changes to create delta package")
    
    elif args.command == "history":
        history = tracker.metadata.get("run_history", [])
        for run in history[-5:]:  # Show last 5 runs
            print(f"\nRun ID: {run['id']}")
            print(f"  Time: {run['start_time']} - {run.get('end_time', 'In progress')}")
            print(f"  Type: {run['type']}")
            print(f"  Changes: {run.get('changes', 'N/A')}")


if __name__ == "__main__":
    main()