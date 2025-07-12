#!/usr/bin/env python3
"""
Process forum HTML files and build/update FAISS index with comprehensive metadata extraction
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
import hashlib
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ForumProcessor:
    def __init__(self):
        self.data_dir = Path("data")
        self.raw_forum_dir = self.data_dir / "raw" / "forum"
        self.processed_dir = self.data_dir / "processed" / "forum"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Model for embeddings
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.embedding_dim = 384
        
        # Chunk settings
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        # Forum categories
        self.categories = {
            'fitness': 'Fitness',
            'gesundheit': 'Gesundheit',
            'ernaehrung': 'Ernährung', 
            'bluttuning': 'Bluttuning',
            'mental': 'Mental',
            'infektion-praevention': 'Infektion & Prävention'
        }
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
        
    def extract_category_from_path(self, file_path: Path) -> str:
        """Extract category from file path."""
        path_str = str(file_path).lower()
        
        for cat_key, cat_name in self.categories.items():
            if f"/{cat_key}/" in path_str or f"/{cat_key}." in path_str:
                return cat_name
        
        # Check if it's a main category page
        if file_path.name.replace('.html', '') in self.categories:
            return self.categories[file_path.name.replace('.html', '')]
            
        return "Allgemein"  # General/uncategorized
    
    def parse_german_date(self, date_str: str) -> Optional[str]:
        """Parse German date format (DD.MM.YYYY) to ISO format."""
        try:
            # Remove any extra whitespace
            date_str = date_str.strip()
            
            # Handle different formats
            if '.' in date_str:
                # DD.MM.YYYY format
                parts = date_str.split('.')
                if len(parts) == 3:
                    day, month, year = parts
                    # Handle 2-digit years
                    if len(year) == 2:
                        year = '20' + year if int(year) < 50 else '19' + year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            return None
        except:
            return None
    
    def extract_forum_thread(self, soup: BeautifulSoup, file_path: Path) -> Optional[Dict]:
        """Extract forum thread information."""
        try:
            # Extract thread title
            title_elem = soup.find('h1', class_='page-title') or soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            if not title:
                # Try meta title
                meta_title = soup.find('meta', {'property': 'og:title'})
                if meta_title:
                    title = meta_title.get('content', '').strip()
            
            # Extract URL
            canonical = soup.find('link', {'rel': 'canonical'})
            url = canonical.get('href') if canonical else None
            
            if not url:
                # Construct from path
                relative_path = file_path.relative_to(self.raw_forum_dir)
                url = f"https://www.strunz.com/forum/{relative_path}"
                url = url.replace('.html', '')  # Clean up
            
            # Extract posts
            posts = []
            post_elements = soup.find_all('div', class_='forum-post-wrapper')
            
            for post in post_elements:
                post_data = self.extract_post_data(post)
                if post_data:
                    posts.append(post_data)
            
            # Extract thread metadata
            thread_info = soup.find('div', class_='thread-info')
            thread_date = None
            thread_author = None
            
            if thread_info:
                # Look for author
                author_link = thread_info.find('a', href=re.compile(r'/forum/profile/'))
                if author_link:
                    thread_author = author_link.get_text(strip=True)
                
                # Look for date
                date_text = thread_info.get_text()
                date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', date_text)
                if date_match:
                    thread_date = self.parse_german_date(date_match.group())
            
            # Category
            category = self.extract_category_from_path(file_path)
            
            return {
                'type': 'thread',
                'title': title or file_path.stem,
                'url': url,
                'category': category,
                'author': thread_author,
                'date': thread_date,
                'posts': posts,
                'post_count': len(posts),
                'file_path': str(file_path)
            }
            
        except Exception as e:
            logging.error(f"Error extracting thread from {file_path}: {e}")
            return None
    
    def extract_post_data(self, post_elem) -> Optional[Dict]:
        """Extract individual post/comment data."""
        try:
            # Author
            author_elem = post_elem.find('span', class_='forum-user-nickname')
            if author_elem:
                author_link = author_elem.find('a')
                author = author_link.get_text(strip=True) if author_link else "Anonymous"
            else:
                author = "Anonymous"
            
            # User stats
            total_posts = 0
            posts_elem = post_elem.find('span', class_='forum-user-total-posts')
            if posts_elem:
                posts_match = re.search(r'(\d+)\s*Kommentar', posts_elem.get_text())
                if posts_match:
                    total_posts = int(posts_match.group(1))
            
            # User registration date
            reg_date = None
            reg_elem = post_elem.find('span', class_='forum-user-joined')
            if reg_elem:
                reg_text = reg_elem.get_text()
                reg_match = re.search(r'Angemeldet am:\s*(\d{2}\.\d{2}\.\d{4})', reg_text)
                if reg_match:
                    reg_date = self.parse_german_date(reg_match.group(1))
            
            # Post date
            post_date = None
            date_elem = post_elem.find('div', class_='post-date')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', date_text)
                if date_match:
                    post_date = self.parse_german_date(date_match.group())
            
            # Content
            content_elem = post_elem.find('div', class_='post-content')
            content = ""
            if content_elem:
                # Remove the date div if present
                date_div = content_elem.find('div', class_='post-date')
                if date_div:
                    date_div.decompose()
                
                # Remove script and style elements
                for elem in content_elem.find_all(['script', 'style']):
                    elem.decompose()
                
                content = content_elem.get_text(separator=' ', strip=True)
            
            # Likes
            likes = 0
            like_elem = post_elem.find('span', class_='post-action')
            if like_elem:
                like_text = like_elem.get_text()
                like_match = re.search(r'(\d+)\s*Person', like_text)
                if like_match:
                    likes = int(like_match.group(1))
            
            return {
                'author': author,
                'date': post_date,
                'content': content,
                'likes': likes,
                'user_registration_date': reg_date,
                'user_total_posts': total_posts
            }
            
        except Exception as e:
            logging.debug(f"Error extracting post data: {e}")
            return None
    
    def extract_category_page(self, soup: BeautifulSoup, file_path: Path) -> Optional[Dict]:
        """Extract category overview page."""
        try:
            category_name = self.extract_category_from_path(file_path)
            
            # Extract thread list
            threads = []
            thread_elements = soup.find_all('div', class_='thread-item') or \
                            soup.find_all('article', class_='forum-post')
            
            for thread in thread_elements:
                # Title
                title_elem = thread.find('h2') or thread.find('h3') or thread.find('a')
                title = title_elem.get_text(strip=True) if title_elem else None
                
                # URL
                link_elem = thread.find('a', href=True)
                thread_url = link_elem.get('href') if link_elem else None
                if thread_url and not thread_url.startswith('http'):
                    thread_url = urljoin('https://www.strunz.com/', thread_url)
                
                # Author
                author_elem = thread.find('a', href=re.compile(r'/profile/'))
                author = author_elem.get_text(strip=True) if author_elem else None
                
                # Stats
                reply_count = 0
                reply_elem = thread.find(text=re.compile(r'\d+\s*(Antwort|Kommentar)'))
                if reply_elem:
                    reply_match = re.search(r'(\d+)', str(reply_elem))
                    if reply_match:
                        reply_count = int(reply_match.group(1))
                
                if title:
                    threads.append({
                        'title': title,
                        'url': thread_url,
                        'author': author,
                        'reply_count': reply_count
                    })
            
            return {
                'type': 'category',
                'category': category_name,
                'thread_count': len(threads),
                'threads': threads,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            logging.error(f"Error extracting category page from {file_path}: {e}")
            return None
    
    def process_forum_file(self, file_path: Path) -> List[Dict]:
        """Process a single forum HTML file."""
        try:
            # Skip if already processed (handles duplicate files with parameters)
            file_key = str(file_path).replace('?', '_').replace('&', '_')
            if file_key in self.processed_files:
                return []
            self.processed_files.add(file_key)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Determine page type
            documents = []
            
            # Check if it's a thread page or category page
            if soup.find('div', class_='forum-post-wrapper') or soup.find('div', class_='forum-posts-wrapper'):
                # It's a thread page
                thread_data = self.extract_forum_thread(soup, file_path)
                if thread_data:
                    # Create documents from thread and posts
                    
                    # Thread overview document
                    thread_meta = {
                        'source': 'forum',
                        'type': 'thread',
                        'category': thread_data['category'],
                        'title': thread_data['title'],
                        'url': thread_data['url'],
                        'author': thread_data['author'],
                        'date': thread_data['date'],
                        'post_count': thread_data['post_count'],
                        'filename': file_path.name,
                        'processed_date': datetime.now().isoformat()
                    }
                    
                    # Create chunks from posts
                    for i, post in enumerate(thread_data['posts']):
                        if post.get('content'):
                            chunks = self.create_chunks(post['content'], {
                                **thread_meta,
                                'post_author': post['author'],
                                'post_date': post['date'],
                                'post_likes': post['likes'],
                                'post_index': i
                            })
                            documents.extend(chunks)
            
            else:
                # It's a category or index page
                category_data = self.extract_category_page(soup, file_path)
                if category_data:
                    # Create a summary document for the category
                    category_text = f"Forum-Kategorie: {category_data['category']}\n"
                    category_text += f"Anzahl Themen: {category_data['thread_count']}\n\n"
                    
                    for thread in category_data['threads'][:10]:  # Top 10 threads
                        category_text += f"- {thread['title']}"
                        if thread.get('author'):
                            category_text += f" (von {thread['author']})"
                        if thread.get('reply_count'):
                            category_text += f" - {thread['reply_count']} Antworten"
                        category_text += "\n"
                    
                    meta = {
                        'source': 'forum',
                        'type': 'category',
                        'category': category_data['category'],
                        'filename': file_path.name,
                        'processed_date': datetime.now().isoformat()
                    }
                    
                    documents.append({
                        'text': category_text,
                        'metadata': meta,
                        'title': f"Forum - {category_data['category']}"
                    })
            
            logging.debug(f"Extracted {len(documents)} documents from {file_path.name}")
            return documents
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            return []
    
    def create_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Create overlapping chunks from text."""
        chunks = []
        
        if not text or len(text.strip()) < 50:  # Skip very short content
            return chunks
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Split into sentences
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
        if current_chunk.strip() and len(current_chunk.strip()) > 50:
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata.copy()
            })
        
        # Add chunk IDs
        for i, chunk in enumerate(chunks):
            chunk['metadata']['chunk_id'] = hashlib.md5(
                f"{metadata.get('filename', '')}_{i}_{chunk['text'][:50]}".encode()
            ).hexdigest()
            chunk['metadata']['chunk_index'] = i
            chunk['title'] = metadata.get('title', 'Forum')
        
        return chunks
    
    def process_all_forum_files(self) -> Dict:
        """Process all forum HTML files."""
        # Find all HTML files
        html_files = []
        for pattern in ['*.html', '**/*.html']:
            html_files.extend(self.raw_forum_dir.glob(pattern))
        
        # Remove duplicates based on content
        unique_files = []
        seen_paths = set()
        
        for file in html_files:
            # Normalize path (remove query parameters for comparison)
            norm_path = str(file).split('?')[0]
            if norm_path not in seen_paths:
                seen_paths.add(norm_path)
                unique_files.append(file)
        
        logging.info(f"Found {len(unique_files)} unique forum files to process")
        
        all_documents = []
        processed_count = 0
        error_count = 0
        
        # Process statistics
        stats = {
            'categories': set(),
            'authors': set(),
            'dates': set(),
            'thread_count': 0,
            'post_count': 0
        }
        
        for i, html_file in enumerate(unique_files):
            if i % 100 == 0:
                logging.info(f"Processing file {i+1}/{len(unique_files)}")
            
            documents = self.process_forum_file(html_file)
            
            if documents:
                all_documents.extend(documents)
                processed_count += 1
                
                # Update statistics
                for doc in documents:
                    meta = doc.get('metadata', {})
                    if meta.get('category'):
                        stats['categories'].add(meta['category'])
                    if meta.get('author'):
                        stats['authors'].add(meta['author'])
                    if meta.get('post_author'):
                        stats['authors'].add(meta['post_author'])
                    if meta.get('date'):
                        stats['dates'].add(meta['date'])
                    if meta.get('post_date'):
                        stats['dates'].add(meta['post_date'])
                    if meta.get('type') == 'thread':
                        stats['thread_count'] += 1
                    if meta.get('post_index') is not None:
                        stats['post_count'] += 1
            else:
                error_count += 1
        
        # Save processed documents
        output_file = self.processed_dir / f"forum_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_documents, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved {len(all_documents)} chunks to {output_file}")
        
        # Log statistics
        logging.info("\n=== FORUM PROCESSING STATISTICS ===")
        logging.info(f"Processed files: {processed_count}")
        logging.info(f"Error files: {error_count}")
        logging.info(f"Total chunks: {len(all_documents)}")
        logging.info(f"Categories found: {sorted(stats['categories'])}")
        logging.info(f"Unique authors: {len(stats['authors'])}")
        logging.info(f"Date range: {min(stats['dates']) if stats['dates'] else 'N/A'} to {max(stats['dates']) if stats['dates'] else 'N/A'}")
        logging.info(f"Threads: {stats['thread_count']}")
        logging.info(f"Posts: {stats['post_count']}")
        
        return {
            'processed_files': processed_count,
            'error_files': error_count,
            'total_chunks': len(all_documents),
            'output_file': str(output_file),
            'statistics': {
                'categories': list(stats['categories']),
                'author_count': len(stats['authors']),
                'date_range': f"{min(stats['dates']) if stats['dates'] else 'N/A'} to {max(stats['dates']) if stats['dates'] else 'N/A'}",
                'thread_count': stats['thread_count'],
                'post_count': stats['post_count']
            }
        }
    
    def build_faiss_index(self, documents: List[Dict]) -> str:
        """Build FAISS index from documents."""
        logging.info(f"Building FAISS index for {len(documents)} forum chunks...")
        
        # Generate embeddings
        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save index
        index_dir = self.data_dir / "faiss_indices" / "forum"
        index_dir.mkdir(parents=True, exist_ok=True)
        
        index_file = index_dir / f"forum_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.faiss"
        faiss.write_index(index, str(index_file))
        
        # Save metadata
        metadata_file = index_file.with_suffix('.json')
        metadata = {
            'documents': documents,
            'total_documents': len(documents),
            'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'embedding_dim': self.embedding_dim,
            'created_date': datetime.now().isoformat(),
            'source': 'forum'
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved FAISS index to {index_file}")
        
        return str(index_file)
    
    def update_combined_index(self, forum_index_file: str):
        """Update the combined FAISS index with forum data."""
        logging.info("Updating combined FAISS index with new forum data...")
        
        # This would need to be implemented based on your combined index strategy
        # For now, just log that it should be done
        logging.info("Note: Combined index update should be run after all sources are processed")

def main():
    processor = ForumProcessor()
    
    # Process all forum files
    logging.info("Starting comprehensive forum processing...")
    result = processor.process_all_forum_files()
    
    logging.info(f"\nProcessing complete:")
    logging.info(f"  - Processed files: {result['processed_files']}")
    logging.info(f"  - Error files: {result['error_files']}")
    logging.info(f"  - Total chunks: {result['total_chunks']}")
    logging.info(f"\nStatistics:")
    for key, value in result['statistics'].items():
        logging.info(f"  - {key}: {value}")
    
    if result['total_chunks'] > 0:
        # Load processed documents
        with open(result['output_file'], 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Build FAISS index
        index_file = processor.build_faiss_index(documents)
        
        logging.info("\n✅ Forum processing and indexing complete!")
        logging.info("\nNote: Run the combined index updater to merge with other sources")

if __name__ == "__main__":
    main()