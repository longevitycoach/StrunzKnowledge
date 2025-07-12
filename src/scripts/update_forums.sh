#!/bin/bash

# Forum Update Script - Run periodically to update forum content
# This script tracks changes for incremental FAISS updates

echo "=== Forum Update Script ==="
echo "Started at: $(date)"
echo

# Change to project directory
cd "$(dirname "$0")/../.."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the update
echo "Running forum update..."
python src/tools/forum_update_tracker.py update

# Check exit status
if [ $? -eq 0 ]; then
    echo
    echo "Update completed successfully!"
    
    # Show current status
    echo
    echo "Current status:"
    python src/tools/forum_update_tracker.py status
else
    echo
    echo "Update failed! Check logs for details."
    exit 1
fi

echo
echo "Finished at: $(date)"
echo "=== Update Complete ==="