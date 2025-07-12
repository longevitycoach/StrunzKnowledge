#!/usr/bin/env python3
"""
HTML Processor - Extracts content from raw HTML files focusing on div id="contentarea"
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re
import hashlib

logger = logging.getLogger(__name__)


class HTMLProcessor:
    """Process raw HTML files and extract content from div id='contentarea' only."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_all_html_files(self, 
                              raw_dir: str = "data/raw",
                              output_dir: str = "data/processed") -> Dict:
        """Process all HTML files and extract content from contentarea div only."""
        stats = {
            'total_files': 0,
            'total_chunks': 0,
            'processed_files': 0,
            'failed_files': 0,
            'categories': {}
        }
        
        raw_path = Path(raw_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process forum HTML files
        forum_dir = raw_path / "forum"
        if forum_dir.exists():
            logger.info("Processing forum HTML files...")
            forum_stats = self._process_directory(forum_dir, output_path, "forum")
            self._merge_stats(stats, forum_stats)
        
        # Process news HTML files
        news_dir = raw_path / "news"
        if news_dir.exists():
            logger.info("Processing news HTML files...")
            news_stats = self._process_directory(news_dir, output_path, "news")
            self._merge_stats(stats, news_stats)
        
        # Process delta HTML files
        delta_dir = raw_path / "delta"
        if delta_dir.exists():
            logger.info("Processing delta HTML files...")
            delta_stats = self._process_directory(delta_dir, output_path, "forum")
            self._merge_stats(stats, delta_stats)
        
        logger.info(f"Processing complete. Stats: {stats}")
        return stats
    
    def _process_directory(self, input_dir: Path, output_dir: Path, category: str) -> Dict:
        """Process all HTML files in a directory."""
        stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'categories': {category: 0}
        }
        
        # Find all HTML files recursively
        html_files = list(input_dir.rglob("*.html"))
        stats['total_files'] = len(html_files)
        
        logger.info(f"Found {len(html_files)} HTML files in {input_dir}")
        
        # Process each file
        processed_docs = []
        
        for i, html_file in enumerate(html_files, 1):
            if i % 100 == 0:
                logger.info(f"Processing {i}/{len(html_files)} files...")
            
            try:
                doc = self._process_single_html_file(html_file, category)
                if doc:
                    processed_docs.append(doc)
                    stats['processed_files'] += 1
                    stats['total_chunks'] += len(doc['chunks'])
                    stats['categories'][category] += len(doc['chunks'])
                else:
                    stats['failed_files'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {html_file}: {e}")
                stats['failed_files'] += 1
        
        # Save processed documents
        if processed_docs:
            output_file = output_dir / f"{category}_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_docs, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(processed_docs)} processed documents to {output_file}")
        
        return stats
    
    def _process_single_html_file(self, html_file: Path, category: str) -> Optional[Dict]:
        """Process a single HTML file and extract content from main content areas."""
        try:
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract content based on category-specific selectors
            content_div = None
            
            if category == "forum":
                # Try forum-specific selectors
                content_div = soup.find('div', class_='forum-content-container')
                if not content_div:
                    content_div = soup.find('div', class_='post-content-wrapper')
            elif category == "news":
                # Try news-specific selectors
                content_div = soup.find('div', class_='post-content')
                if not content_div:
                    content_div = soup.find('div', class_='post-description')
            
            # Fallback to main content area
            if not content_div:
                content_div = soup.find('main', id='maincontent')
            
            if not content_div:
                logger.debug(f"No content area found in {html_file}")
                return None
            
            # Extract text content
            text_content = self._extract_text_from_element(content_div)
            
            if not text_content or len(text_content.strip()) < 50:
                logger.debug(f"Insufficient content in {html_file}")
                return None
            
            # Extract metadata
            metadata = self._extract_metadata(soup, html_file, category)
            
            # Create chunks
            chunks = self._create_chunks(text_content, metadata)
            
            if not chunks:
                return None
            
            return {
                'filename': str(html_file.relative_to(html_file.parents[3])),  # Relative to project root
                'category': category,
                'url': self._extract_url(html_file),
                'processed_at': datetime.now().isoformat(),
                'original_length': len(html_content),
                'extracted_length': len(text_content),
                'metadata': metadata,
                'chunks': chunks
            }
            
        except Exception as e:
            logger.error(f"Error processing {html_file}: {e}")
            return None
    
    def _extract_text_from_element(self, element) -> str:
        """Extract clean text from a BeautifulSoup element."""
        # Remove script and style elements
        for script in element(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = element.get_text()
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, html_file: Path, category: str) -> Dict:
        """Extract metadata from HTML."""
        metadata = {
            'source_file': html_file.name,
            'category': category,
            'source_path': str(html_file)
        }
        
        # Extract title
        title_elem = soup.find('title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract meta description
        desc_elem = soup.find('meta', attrs={'name': 'description'})
        if desc_elem:
            metadata['description'] = desc_elem.get('content', '').strip()
        
        # Try to extract date from various locations
        date_patterns = [
            r'(\d{1,2}\.\d{1,2}\.\d{4})',  # German date format
            r'(\d{4}-\d{2}-\d{2})',       # ISO date format
        ]
        
        for pattern in date_patterns:
            # Check in title
            if 'title' in metadata:
                match = re.search(pattern, metadata['title'])
                if match:
                    metadata['date'] = match.group(1)
                    break
            
            # Check in content
            content_div = soup.find('div', id='contentarea')
            if content_div:
                content_text = content_div.get_text()[:500]  # First 500 chars
                match = re.search(pattern, content_text)
                if match:
                    metadata['date'] = match.group(1)
                    break
        
        # Extract URL from filename if it contains URL-like structure
        metadata['url'] = self._extract_url(html_file)
        
        return metadata
    
    def _extract_url(self, html_file: Path) -> str:
        """Extract or reconstruct URL from file path."""
        path_str = str(html_file)
        
        # Try to reconstruct URL from file path
        if '/forum/' in path_str:
            # Forum URL
            category = html_file.parent.name
            filename = html_file.stem
            
            # Remove query parameters for clean URL
            clean_filename = re.sub(r'\?.*$', '', filename)
            
            return f"https://www.strunz.com/forum/{category}/{clean_filename}"
        
        elif '/news/' in path_str:
            # News URL
            filename = html_file.stem
            return f"https://www.strunz.com/news/{filename}.html"
        
        return f"https://www.strunz.com/{html_file.name}"
    
    def _create_chunks(self, text: str, base_metadata: Dict) -> List[Dict]:
        """Create text chunks with overlap."""
        chunks = []
        
        if not text or len(text.strip()) < 50:
            return chunks
        
        # Split into sentences for better chunking
        sentences = self._split_sentences(text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunk_id = self._generate_chunk_id(chunk_text)
                
                chunks.append({
                    'id': chunk_id,
                    'content': chunk_text,
                    'metadata': {
                        **base_metadata,
                        'chunk_index': len(chunks),
                        'chunk_length': len(chunk_text)
                    }
                })
                
                # Keep overlap
                overlap_size = 0
                overlap_chunks = []
                for chunk in reversed(current_chunk):
                    overlap_size += len(chunk)
                    overlap_chunks.insert(0, chunk)
                    if overlap_size >= self.chunk_overlap:
                        break
                
                current_chunk = overlap_chunks
                current_length = overlap_size
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_id = self._generate_chunk_id(chunk_text)
            
            chunks.append({
                'id': chunk_id,
                'content': chunk_text,
                'metadata': {
                    **base_metadata,
                    'chunk_index': len(chunks),
                    'chunk_length': len(chunk_text)
                }
            })
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, optimized for German."""
        # German sentence splitter
        sentence_endings = r'[.!?]\s+'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate unique ID for a chunk."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def _merge_stats(self, main_stats: Dict, new_stats: Dict):
        """Merge statistics from directory processing."""
        main_stats['total_files'] += new_stats['total_files']
        main_stats['processed_files'] += new_stats['processed_files']
        main_stats['failed_files'] += new_stats['failed_files']
        main_stats['total_chunks'] += new_stats['total_chunks']
        
        for category, count in new_stats['categories'].items():
            main_stats['categories'][category] = main_stats['categories'].get(category, 0) + count


def main():
    """Test the HTML processor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    processor = HTMLProcessor()
    
    print("=== HTML Content Processor ===")
    print("Extracts content from div id='contentarea' ONLY")
    print("Processing forum and news HTML files...")
    
    stats = processor.process_all_html_files()
    
    print(f"\n✅ Processing complete!")
    print(f"Total files: {stats['total_files']}")
    print(f"Processed: {stats['processed_files']}")
    print(f"Failed: {stats['failed_files']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Categories: {stats['categories']}")


if __name__ == "__main__":
    main()