#!/usr/bin/env python3
"""
Process news HTML files through Docling and build/update FAISS index
Ensures news content is properly tagged and separated from forum content
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
from bs4 import BeautifulSoup
import re

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NewsProcessor:
    def __init__(self):
        self.data_dir = Path("data")
        self.raw_news_dir = self.data_dir / "raw" / "news"
        self.processed_dir = self.data_dir / "processed" / "news"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Model for embeddings (same as enhanced_html_processor)
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.embedding_dim = 384
        
        # Chunk settings
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def extract_news_content(self, html_file: Path) -> Dict:
        """Extract content from news HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = {
                'source': 'news',  # Important: Mark as news content
                'filename': html_file.name,
                'url': f"https://www.strunz.com/news/{html_file.name}",
                'processed_date': datetime.now().isoformat()
            }
            
            # Extract title
            title = None
            title_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                metadata['title'] = title
            
            # Extract date from various sources
            date = self.extract_date(soup, html_file.name)
            if date:
                metadata['date'] = date
            
            # Extract author (usually Dr. Strunz for news)
            metadata['author'] = "Dr. Ulrich Strunz"
            
            # Extract main content - try multiple selectors
            content_div = None
            
            # Try different content selectors for news pages
            selectors = [
                {'class': 'post-content'},
                {'class': 'news-content'},
                {'class': 'article-content'},
                {'class': 'content'},
                {'id': 'content'},
                {'class': 'entry-content'},
                {'class': 'main-content'}
            ]
            
            for selector in selectors:
                content_div = soup.find('div', selector)
                if content_div:
                    break
            
            # If no specific content div, try article or main tag
            if not content_div:
                content_div = soup.find('article') or soup.find('main')
            
            # Extract text content
            if content_div:
                # Remove script and style elements
                for script in content_div(["script", "style"]):
                    script.decompose()
                
                # Get text
                content = content_div.get_text(separator='\n', strip=True)
                
                # Clean up text
                content = re.sub(r'\n+', '\n', content)
                content = re.sub(r'\s+', ' ', content)
                content = content.strip()
            else:
                # Fallback: get body text
                body = soup.find('body')
                if body:
                    for script in body(["script", "style", "nav", "header", "footer"]):
                        script.decompose()
                    content = body.get_text(separator='\n', strip=True)
                    content = re.sub(r'\n+', '\n', content)
                    content = re.sub(r'\s+', ' ', content)
                    content = content.strip()
                else:
                    content = ""
            
            # Extract any tags or categories
            tags = []
            tag_elements = soup.find_all(['a', 'span'], {'class': re.compile(r'tag|category|label')})
            for tag in tag_elements:
                tag_text = tag.get_text(strip=True)
                if tag_text and len(tag_text) < 50:
                    tags.append(tag_text)
            
            if tags:
                metadata['tags'] = list(set(tags))
            
            return {
                'content': content,
                'metadata': metadata,
                'title': title or html_file.stem
            }
            
        except Exception as e:
            logging.error(f"Error processing {html_file}: {e}")
            return None
    
    def extract_date(self, soup: BeautifulSoup, filename: str) -> Optional[str]:
        """Extract date from various sources."""
        # Try meta tags
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        if date_meta and date_meta.get('content'):
            return date_meta['content'][:10]  # YYYY-MM-DD format
        
        # Try time tags
        time_elem = soup.find('time')
        if time_elem:
            if time_elem.get('datetime'):
                return time_elem['datetime'][:10]
            elif time_elem.get_text(strip=True):
                return self.parse_german_date(time_elem.get_text(strip=True))
        
        # Try to find date in text patterns
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{4}-\d{2}-\d{2}',         # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, str(soup))
            if match:
                date_str = match.group(0)
                if '.' in date_str:
                    # Convert DD.MM.YYYY to YYYY-MM-DD
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                else:
                    return date_str
        
        return None
    
    def parse_german_date(self, date_str: str) -> Optional[str]:
        """Parse German date format."""
        months = {
            'januar': '01', 'februar': '02', 'märz': '03', 'april': '04',
            'mai': '05', 'juni': '06', 'juli': '07', 'august': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'dezember': '12'
        }
        
        date_str = date_str.lower()
        for month_name, month_num in months.items():
            if month_name in date_str:
                # Extract day and year
                match = re.search(r'(\d{1,2})\.\s*' + month_name + r'\s*(\d{4})', date_str)
                if match:
                    day = match.group(1).zfill(2)
                    year = match.group(2)
                    return f"{year}-{month_num}-{day}"
        
        return None
    
    def create_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Create overlapping chunks from text."""
        chunks = []
        
        if not text:
            return chunks
        
        # Split into sentences for better chunking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata.copy()
                })
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + " " + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += " " + sentence
                current_length += sentence_length + 1
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata.copy()
            })
        
        return chunks
    
    def process_news_files(self, limit: Optional[int] = None) -> Dict:
        """Process all news HTML files."""
        news_files = list(self.raw_news_dir.glob("*.html"))
        
        if limit:
            news_files = news_files[:limit]
        
        logging.info(f"Processing {len(news_files)} news files...")
        
        all_documents = []
        processed_count = 0
        error_count = 0
        
        for i, html_file in enumerate(news_files):
            if i % 100 == 0:
                logging.info(f"Processing file {i+1}/{len(news_files)}")
            
            # Extract content
            result = self.extract_news_content(html_file)
            
            if result and result['content']:
                # Create chunks
                chunks = self.create_chunks(result['content'], result['metadata'])
                
                for chunk in chunks:
                    # Add chunk-specific metadata
                    chunk['metadata']['chunk_id'] = hashlib.md5(
                        chunk['text'].encode()
                    ).hexdigest()
                    chunk['title'] = result['title']
                    
                    all_documents.append(chunk)
                
                processed_count += 1
            else:
                error_count += 1
        
        # Save processed documents
        output_file = self.processed_dir / f"news_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_documents, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved {len(all_documents)} chunks to {output_file}")
        
        return {
            'processed_files': processed_count,
            'error_files': error_count,
            'total_chunks': len(all_documents),
            'output_file': str(output_file)
        }
    
    def build_faiss_index(self, documents: List[Dict]) -> str:
        """Build FAISS index from documents."""
        logging.info(f"Building FAISS index for {len(documents)} documents...")
        
        # Generate embeddings
        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save index
        index_dir = self.data_dir / "faiss_indices" / "news"
        index_dir.mkdir(parents=True, exist_ok=True)
        
        index_file = index_dir / f"news_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.faiss"
        faiss.write_index(index, str(index_file))
        
        # Save metadata
        metadata_file = index_file.with_suffix('.json')
        metadata = {
            'documents': documents,
            'total_documents': len(documents),
            'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'embedding_dim': self.embedding_dim,
            'created_date': datetime.now().isoformat(),
            'source': 'news'
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved FAISS index to {index_file}")
        
        return str(index_file)
    
    def update_combined_index(self, news_index_file: str):
        """Update the combined FAISS index with news data."""
        logging.info("Updating combined FAISS index...")
        
        # Load existing combined index if exists
        combined_index_dir = self.data_dir / "faiss_indices"
        combined_index_file = combined_index_dir / "combined_index.faiss"
        combined_metadata_file = combined_index_dir / "combined_metadata.json"
        
        # Load news index and metadata
        news_index = faiss.read_index(news_index_file)
        with open(Path(news_index_file).with_suffix('.json'), 'r') as f:
            news_metadata = json.load(f)
        
        if combined_index_file.exists():
            # Load existing combined index
            combined_index = faiss.read_index(str(combined_index_file))
            with open(combined_metadata_file, 'r') as f:
                combined_metadata = json.load(f)
            
            # Merge indices
            combined_index.add(news_index.reconstruct_n(0, news_index.ntotal))
            
            # Update metadata - mark news documents
            for doc in news_metadata['documents']:
                doc['metadata']['content_type'] = 'news'
            
            combined_metadata['documents'].extend(news_metadata['documents'])
            combined_metadata['total_documents'] = len(combined_metadata['documents'])
            combined_metadata['last_updated'] = datetime.now().isoformat()
            combined_metadata['sources'] = list(set(
                combined_metadata.get('sources', []) + ['news']
            ))
        else:
            # Create new combined index
            combined_index = news_index
            combined_metadata = news_metadata
            combined_metadata['sources'] = ['news']
        
        # Save updated combined index
        faiss.write_index(combined_index, str(combined_index_file))
        with open(combined_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(combined_metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Updated combined index with {news_metadata['total_documents']} news documents")
        logging.info(f"Total documents in combined index: {combined_metadata['total_documents']}")

def main():
    processor = NewsProcessor()
    
    # Process news files
    logging.info("Starting news content processing...")
    result = processor.process_news_files()
    
    logging.info(f"Processing complete:")
    logging.info(f"  - Processed files: {result['processed_files']}")
    logging.info(f"  - Error files: {result['error_files']}")
    logging.info(f"  - Total chunks: {result['total_chunks']}")
    
    # Load processed documents
    with open(result['output_file'], 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # Build FAISS index
    index_file = processor.build_faiss_index(documents)
    
    # Update combined index
    processor.update_combined_index(index_file)
    
    logging.info("✅ News processing and indexing complete!")

if __name__ == "__main__":
    main()