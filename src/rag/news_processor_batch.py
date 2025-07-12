#!/usr/bin/env python3
"""
Process news HTML files in batches to avoid timeouts
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
import sys

from news_processor import NewsProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_in_batches(batch_size=500):
    """Process news files in smaller batches."""
    processor = NewsProcessor()
    
    # Get all news files
    news_files = sorted(list(processor.raw_news_dir.glob("*.html")))
    total_files = len(news_files)
    
    logging.info(f"Found {total_files} news files to process")
    
    # Track progress
    progress_file = processor.processed_dir / "progress.json"
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        start_index = progress.get('last_processed_index', 0) + 1
        all_documents = progress.get('all_documents', [])
        logging.info(f"Resuming from file index {start_index}")
    else:
        start_index = 0
        all_documents = []
    
    # Process in batches
    batch_num = start_index // batch_size + 1
    
    for i in range(start_index, total_files, batch_size):
        batch_end = min(i + batch_size, total_files)
        batch_files = news_files[i:batch_end]
        
        logging.info(f"\n=== Processing batch {batch_num} ({i+1}-{batch_end}/{total_files}) ===")
        
        processed_count = 0
        error_count = 0
        
        for j, html_file in enumerate(batch_files):
            if (i + j) % 100 == 0:
                logging.info(f"Processing file {i+j+1}/{total_files}")
            
            # Extract content
            result = processor.extract_news_content(html_file)
            
            if result and result['content']:
                # Create chunks
                chunks = processor.create_chunks(result['content'], result['metadata'])
                
                for chunk in chunks:
                    # Add chunk-specific metadata
                    import hashlib
                    chunk['metadata']['chunk_id'] = hashlib.md5(
                        chunk['text'].encode()
                    ).hexdigest()
                    chunk['title'] = result['title']
                    
                    all_documents.append(chunk)
                
                processed_count += 1
            else:
                error_count += 1
        
        # Save progress after each batch
        progress = {
            'last_processed_index': batch_end - 1,
            'total_files': total_files,
            'total_documents': len(all_documents),
            'all_documents': all_documents,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False)
        
        logging.info(f"Batch {batch_num} complete: {processed_count} processed, {error_count} errors")
        logging.info(f"Total documents so far: {len(all_documents)}")
        
        batch_num += 1
    
    # Save final results
    output_file = processor.processed_dir / f"news_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_documents, f, ensure_ascii=False, indent=2)
    
    logging.info(f"\n✅ All batches complete!")
    logging.info(f"Total documents: {len(all_documents)}")
    logging.info(f"Saved to: {output_file}")
    
    return {
        'total_documents': len(all_documents),
        'output_file': str(output_file)
    }

def build_index_from_saved():
    """Build FAISS index from saved documents."""
    processor = NewsProcessor()
    
    # Find the latest saved documents file
    doc_files = sorted(processor.processed_dir.glob("news_documents_*.json"))
    if not doc_files:
        logging.error("No saved document files found!")
        return
    
    latest_file = doc_files[-1]
    logging.info(f"Loading documents from {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    logging.info(f"Loaded {len(documents)} documents")
    
    # Build FAISS index
    index_file = processor.build_faiss_index(documents)
    
    # Update combined index
    processor.update_combined_index(index_file)
    
    logging.info("✅ Indexing complete!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--build-index':
        # Just build index from saved documents
        build_index_from_saved()
    else:
        # Process documents first
        result = process_in_batches(batch_size=500)
        
        # Then build index
        if result['total_documents'] > 0:
            build_index_from_saved()

if __name__ == "__main__":
    main()