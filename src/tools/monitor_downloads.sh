#!/bin/bash
#
# Monitor Forum Downloads Progress
# ================================
#

echo "📊 FORUM DOWNLOAD MONITORING"
echo "============================"
echo ""

while true; do
    clear
    echo "📊 FORUM DOWNLOAD PROGRESS - $(date)"
    echo "========================================"
    echo ""
    
    # Check each category
    for category in fitness ernaehrung gesundheit bluttuning mental infektion-und-praevention; do
        count=$(find data/raw/forum -name "*${category}*.html" 2>/dev/null | wc -l | tr -d ' ')
        echo "📁 ${category}: ${count} files"
    done
    
    echo ""
    echo "📈 TOTAL STATISTICS:"
    echo "--------------------"
    total_files=$(find data/raw/forum -name "*.html" | wc -l | tr -d ' ')
    total_size=$(du -sh data/raw/forum 2>/dev/null | cut -f1)
    echo "   Total HTML files: ${total_files}"
    echo "   Total size: ${total_size}"
    
    echo ""
    echo "🔄 ACTIVE DOWNLOADS:"
    echo "--------------------"
    ps aux | grep wget | grep -v grep | wc -l | xargs echo "   Active wget processes:"
    
    echo ""
    echo "📜 RECENT DOWNLOADS:"
    echo "--------------------"
    find data/raw/forum -name "*.html" -mmin -1 2>/dev/null | tail -5 | while read file; do
        basename "$file" | xargs echo "   "
    done
    
    echo ""
    echo "Press Ctrl+C to stop monitoring..."
    echo "Refreshing in 10 seconds..."
    
    sleep 10
done