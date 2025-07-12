#!/usr/bin/env python3
"""
Enhanced HTML Processor - Extracts content with comprehensive metadata including dates, authors, and forum responses
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


class EnhancedHTMLProcessor:
    """Enhanced HTML processor with comprehensive metadata extraction."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_all_html_files(self, 
                              raw_dir: str = "data/raw",
                              output_dir: str = "data/processed") -> Dict:
        """Process all HTML files with enhanced metadata extraction."""
        stats = {
            'total_files': 0,
            'total_chunks': 0,
            'processed_files': 0,
            'failed_files': 0,
            'categories': {},
            'dates_extracted': 0,
            'authors_extracted': 0,
            'forum_responses_found': 0
        }
        
        raw_path = Path(raw_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process forum HTML files
        forum_dir = raw_path / "forum"
        if forum_dir.exists():
            logger.info("Processing forum HTML files with enhanced metadata...")
            forum_stats = self._process_directory(forum_dir, output_path, "forum")
            self._merge_stats(stats, forum_stats)
        
        # Process news HTML files
        news_dir = raw_path / "news"
        if news_dir.exists():
            logger.info("Processing news HTML files with enhanced metadata...")
            news_stats = self._process_directory(news_dir, output_path, "news")
            self._merge_stats(stats, news_stats)
        
        # Process delta HTML files
        delta_dir = raw_path / "delta"
        if delta_dir.exists():
            logger.info("Processing delta HTML files with enhanced metadata...")
            delta_stats = self._process_directory(delta_dir, output_path, "forum")
            self._merge_stats(stats, delta_stats)
        
        logger.info(f"Enhanced processing complete. Stats: {stats}")
        return stats
    
    def _process_directory(self, input_dir: Path, output_dir: Path, category: str) -> Dict:
        """Process all HTML files in a directory with enhanced metadata."""
        stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'categories': {category: 0},
            'dates_extracted': 0,
            'authors_extracted': 0,
            'forum_responses_found': 0
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
                    
                    # Track metadata extraction
                    if doc['metadata'].get('date'):
                        stats['dates_extracted'] += 1
                    if doc['metadata'].get('author'):
                        stats['authors_extracted'] += 1
                    if doc['metadata'].get('forum_responses', 0) > 0:
                        stats['forum_responses_found'] += doc['metadata']['forum_responses']
                else:
                    stats['failed_files'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {html_file}: {e}")
                stats['failed_files'] += 1
        
        # Save processed documents
        if processed_docs:
            output_file = output_dir / f"{category}_enhanced_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_docs, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(processed_docs)} enhanced documents to {output_file}")
        
        return stats
    
    def _process_single_html_file(self, html_file: Path, category: str) -> Optional[Dict]:
        """Process a single HTML file with enhanced metadata extraction."""
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
            
            # Enhanced metadata extraction
            metadata = self._extract_enhanced_metadata(soup, html_file, category, content_div)
            
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
    
    def _extract_enhanced_metadata(self, soup: BeautifulSoup, html_file: Path, category: str, content_div) -> Dict:
        """Extract comprehensive metadata including dates, authors, and forum responses."""
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
        
        # Enhanced date extraction
        date_info = self._extract_dates(soup, content_div, metadata.get('title', ''))
        if date_info:
            metadata.update(date_info)
        
        # Enhanced author extraction
        author_info = self._extract_authors(soup, content_div, category)
        if author_info:
            metadata.update(author_info)
        
        # Forum-specific metadata
        if category == "forum":
            forum_info = self._extract_forum_metadata(soup, content_div)
            metadata.update(forum_info)
        
        # News-specific metadata
        elif category == "news":
            news_info = self._extract_news_metadata(soup, content_div)
            metadata.update(news_info)
        
        # Extract URL
        metadata['url'] = self._extract_url(html_file)
        
        return metadata
    
    def _extract_dates(self, soup: BeautifulSoup, content_div, title: str) -> Dict:
        """Extract dates from various locations in the HTML."""
        date_info = {}
        
        # Date patterns to look for
        date_patterns = [
            r'(\d{1,2}\.\d{1,2}\.\d{4})',  # German format: 31.12.2023
            r'(\d{4}-\d{2}-\d{2})',       # ISO format: 2023-12-31
            r'(\d{1,2}/\d{1,2}/\d{4})',   # US format: 12/31/2023
            r'(\d{1,2}\.\d{1,2}\.\d{2})',  # Short German: 31.12.23
        ]
        
        # Search in title
        if title:
            for pattern in date_patterns:
                match = re.search(pattern, title)
                if match:
                    date_info['date'] = match.group(1)
                    date_info['date_source'] = 'title'
                    break
        
        # Search in content (first 1000 characters)
        if not date_info.get('date') and content_div:
            content_text = content_div.get_text()[:1000]
            for pattern in date_patterns:
                matches = re.findall(pattern, content_text)
                if matches:
                    # Take the first valid date found
                    date_info['date'] = matches[0]
                    date_info['date_source'] = 'content'
                    break
        
        # Search for specific date elements in forum posts
        if not date_info.get('date'):
            # Look for forum post dates
            date_elements = content_div.find_all(['span', 'div', 'time'], string=re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
            if date_elements:
                date_text = date_elements[0].get_text()
                match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', date_text)
                if match:
                    date_info['date'] = match.group(1)
                    date_info['date_source'] = 'post_element'
        
        return date_info
    
    def _extract_authors(self, soup: BeautifulSoup, content_div, category: str) -> Dict:
        """Extract author information."""
        author_info = {}
        
        if category == "forum":
            # Look for forum usernames/authors
            # Common patterns: "Angemeldet am:", user names before comments
            author_patterns = [
                r'([A-Za-z][A-Za-z0-9_\s]{2,30})\s+\d+\s+Kommentare',  # Username + comment count
                r'Angemeldet am.*?([A-Za-z][A-Za-z0-9_\s]{2,30})',      # After registration date
            ]
            
            content_text = content_div.get_text()
            authors = set()
            
            for pattern in author_patterns:
                matches = re.findall(pattern, content_text)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    clean_author = match.strip()
                    if len(clean_author) > 2 and clean_author not in ['Kommentare', 'Nachricht', 'senden']:
                        authors.add(clean_author)
            
            if authors:
                author_info['authors'] = list(authors)
                author_info['primary_author'] = list(authors)[0]  # First found author
        
        elif category == "news":
            # News articles are typically by Dr. Strunz
            # Look for author bylines
            author_patterns = [
                r'[Vv]on\s+([A-Za-z][A-Za-z\s\.]{3,30})',  # "von Dr. Strunz"
                r'[Aa]utor:?\s*([A-Za-z][A-Za-z\s\.]{3,30})',  # "Autor: Dr. Strunz"
            ]
            
            content_text = content_div.get_text()[:500]  # Check first 500 chars
            
            for pattern in author_patterns:
                match = re.search(pattern, content_text)
                if match:
                    author_info['author'] = match.group(1).strip()
                    break
            
            # Default for news articles
            if not author_info.get('author'):
                author_info['author'] = 'Dr. Ulrich Strunz'
        
        return author_info
    
    def _extract_forum_metadata(self, soup: BeautifulSoup, content_div) -> Dict:
        """Extract forum-specific metadata."""
        forum_info = {
            'content_type': 'forum_discussion',
            'forum_responses': 0,
            'forum_category': 'general'
        }
        
        content_text = content_div.get_text()
        
        # Count forum responses/comments
        comment_matches = re.findall(r'(\d+)\s+Kommentare?', content_text)
        if comment_matches:
            forum_info['forum_responses'] = sum(int(count) for count in comment_matches)
        
        # Extract forum category from URL or title
        # Forum categories: fitness, gesundheit, ernährung, bluttuning, mental, infektion_prävention
        category_patterns = [
            r'fitness',
            r'gesundheit', 
            r'ernährung',
            r'bluttuning',
            r'mental',
            r'infektion',
            r'prävention'
        ]
        
        full_text = soup.get_text().lower()
        for pattern in category_patterns:
            if re.search(pattern, full_text):
                forum_info['forum_category'] = pattern
                break
        
        # Check if this is a forum thread or response page
        if '?p=' in str(soup):
            forum_info['is_paginated'] = True
            page_match = re.search(r'\?p=(\d+)', str(soup))
            if page_match:
                forum_info['page_number'] = int(page_match.group(1))
        
        return forum_info
    
    def _extract_news_metadata(self, soup: BeautifulSoup, content_div) -> Dict:
        """Extract news-specific metadata."""
        news_info = {
            'content_type': 'news_article',
            'article_type': 'health_news'
        }
        
        # Extract news topic/theme
        content_text = content_div.get_text()[:500]
        
        # Health topics
        health_topics = [
            'vitamin', 'mineral', 'ernährung', 'fitness', 'gesundheit',
            'immunsystem', 'omega', 'protein', 'blut', 'herz',
            'brain', 'gehirn', 'sport', 'bewegung', 'stoffwechsel'
        ]
        
        topics_found = []
        for topic in health_topics:
            if re.search(topic, content_text.lower()):
                topics_found.append(topic)
        
        if topics_found:
            news_info['health_topics'] = topics_found
            news_info['primary_topic'] = topics_found[0]
        
        return news_info
    
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
        for key in ['total_files', 'processed_files', 'failed_files', 'total_chunks', 
                   'dates_extracted', 'authors_extracted', 'forum_responses_found']:
            main_stats[key] += new_stats.get(key, 0)
        
        for category, count in new_stats['categories'].items():
            main_stats['categories'][category] = main_stats['categories'].get(category, 0) + count


def main():
    """Test the enhanced HTML processor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    processor = EnhancedHTMLProcessor()
    
    print("=== Enhanced HTML Content Processor ===")
    print("Extracts content with comprehensive metadata: dates, authors, forum responses")
    print("Processing forum, news, and delta HTML files...")
    
    stats = processor.process_all_html_files()
    
    print(f"\n✅ Enhanced processing complete!")
    print(f"Total files: {stats['total_files']}")
    print(f"Processed: {stats['processed_files']}")
    print(f"Failed: {stats['failed_files']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Dates extracted: {stats['dates_extracted']}")
    print(f"Authors extracted: {stats['authors_extracted']}")
    print(f"Forum responses found: {stats['forum_responses_found']}")
    print(f"Categories: {stats['categories']}")


if __name__ == "__main__":
    main()