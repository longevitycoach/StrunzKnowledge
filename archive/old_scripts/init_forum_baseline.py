#!/usr/bin/env python3
"""
Initialize forum baseline - Records current state as initial download
"""

from forum_update_tracker import ForumUpdateTracker
from datetime import datetime

def main():
    print("Initializing forum baseline...")
    
    tracker = ForumUpdateTracker()
    
    # Record a "completed" initial run
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Scan current files
    current_files = tracker.scan_current_files()
    
    # Create initial run record
    run_info = {
        "id": run_id,
        "start_time": "2025-07-11T19:17:00",  # Approximate start time from logs
        "end_time": "2025-07-11T19:30:00",    # Approximate end time
        "type": "initial_download",
        "status": "completed",
        "changes": {
            "new_files": len(current_files),
            "modified_files": 0,
            "deleted_files": 0,
            "total_files": len(current_files)
        }
    }
    
    # Update metadata
    tracker.metadata["last_run"] = run_info["end_time"]
    tracker.metadata["file_hashes"] = current_files
    tracker.metadata["run_history"].append(run_info)
    
    # Save
    tracker._save_metadata()
    
    print(f"Baseline initialized with {len(current_files)} files")
    print(f"Metadata saved to: {tracker.metadata_file}")
    
    # Show category breakdown
    categories = {}
    for file_info in current_files.values():
        cat = file_info["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nFiles per category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count} files")


if __name__ == "__main__":
    main()