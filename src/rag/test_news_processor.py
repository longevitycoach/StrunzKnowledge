#!/usr/bin/env python3
"""
Test news processor with a small sample
"""

from news_processor import NewsProcessor
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_single_file():
    """Test processing a single news file."""
    processor = NewsProcessor()
    
    # Get first news file
    news_files = list(processor.raw_news_dir.glob("*.html"))[:1]
    
    if news_files:
        html_file = news_files[0]
        logging.info(f"Testing with file: {html_file.name}")
        
        result = processor.extract_news_content(html_file)
        
        if result:
            logging.info(f"Title: {result.get('title', 'N/A')}")
            logging.info(f"Metadata: {result['metadata']}")
            logging.info(f"Content length: {len(result['content'])} characters")
            logging.info(f"Content preview: {result['content'][:200]}...")
            
            # Test chunking
            chunks = processor.create_chunks(result['content'], result['metadata'])
            logging.info(f"Created {len(chunks)} chunks")
            
            if chunks:
                logging.info(f"First chunk: {chunks[0]['text'][:100]}...")
        else:
            logging.error("Failed to extract content")
    else:
        logging.error("No news files found")

def test_batch_processing():
    """Test processing a small batch of news files."""
    processor = NewsProcessor()
    
    logging.info("Testing batch processing with 10 files...")
    result = processor.process_news_files(limit=10)
    
    logging.info(f"Batch processing result: {result}")

if __name__ == "__main__":
    logging.info("=== Testing News Processor ===")
    
    # Test single file
    test_single_file()
    
    print("\n" + "="*50 + "\n")
    
    # Test batch
    test_batch_processing()