#!/bin/bash
# Update books

echo "Checking for new books..."
cd data/books

# Count PDF files
BOOK_COUNT=$(ls -1 *.pdf 2>/dev/null | wc -l)
echo "Found $BOOK_COUNT books"

# Run book processor
cd ../..
source venv/bin/activate
python src/rag/book_processor_simple.py
