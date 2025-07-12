# Forum Update Tracker

The Forum Update Tracker manages incremental downloads and tracks changes for the FAISS vector database updates.

## Features

- **Baseline Tracking**: Records initial state of all downloaded forum files
- **Change Detection**: Identifies new, modified, and deleted files since last run
- **Delta Packages**: Creates packages of changed files for incremental FAISS updates
- **Run History**: Maintains history of download runs with timestamps and statistics
- **File Hashing**: Uses SHA256 to detect content changes

## Usage

### Check Current Status
```bash
python src/tools/forum_update_tracker.py status
```
Shows:
- Last run information
- Changes since last run
- File counts by type (new/modified/deleted)

### Run Forum Update
```bash
# Update all categories
python src/tools/forum_update_tracker.py update

# Update specific categories
python src/tools/forum_update_tracker.py update --categories fitness mental
```
This will:
- Run wget with `--timestamping` flag (only downloads newer files)
- Track all changes
- Create delta package if changes detected
- Update metadata

### Create Delta Package
```bash
python src/tools/forum_update_tracker.py delta
```
Creates a timestamped package in `data/delta/` containing:
- All new and modified files
- Delta metadata JSON
- Change statistics

### View History
```bash
python src/tools/forum_update_tracker.py history
```
Shows last 5 download runs with statistics.

## Metadata Structure

The tracker maintains metadata in `data/update_metadata.json`:

```json
{
  "last_run": "2025-07-11T19:30:00",
  "file_hashes": {
    "fitness/thread1.html": {
      "category": "fitness",
      "size": 12345,
      "modified": "2025-07-11T19:20:00",
      "hash": "sha256..."
    }
  },
  "run_history": [
    {
      "id": "20250711_193000",
      "start_time": "2025-07-11T19:17:00",
      "end_time": "2025-07-11T19:30:00",
      "type": "initial_download",
      "status": "completed",
      "changes": {
        "new_files": 2988,
        "modified_files": 0,
        "deleted_files": 0,
        "total_files": 2988
      }
    }
  ]
}
```

## Integration with FAISS

When processing delta packages for FAISS updates:

1. Load delta package from `data/delta/delta_TIMESTAMP/`
2. Process only files listed in `delta_metadata.json`
3. Update FAISS index incrementally
4. Remove deleted files from index

## Automation

For automated daily updates, add to cron:
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/StrunzKnowledge && python src/tools/forum_update_tracker.py update
```

## Current State

- **Initial Download**: July 11, 2025 at 19:30
- **Total Files**: 2,988 HTML files
- **Categories**: 6 (fitness, ernährung, gesundheit, bluttuning, mental, infektion-und-praevention)
- **Next Step**: Run `update` command to check for new forum content