#!/bin/bash
# Update news articles

echo "Updating news articles..."
cd data/raw/news

# Download only new files (-N flag)
wget -r -l 1 -H -t 1 -nd -N -np -A '*.html' -erobots=off https://www.strunz.com/news/

# Count new files
NEW_FILES=$(find . -name "*.html" -mtime -1 | wc -l)
echo "Downloaded $NEW_FILES new articles"

if [ $NEW_FILES -gt 0 ]; then
    echo "Processing new articles..."
    cd ../../..
    source venv/bin/activate
    python src/rag/news_processor_batch.py
fi
