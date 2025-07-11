import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
import hashlib
from datetime import datetime
import re

from .vector_store import FAISSVectorStore
from .docling_processor import DoclingProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents and build the vector store."""
    
    def __init__(self,
                 vector_store: Optional[FAISSVectorStore] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        self.vector_store = vector_store or FAISSVectorStore()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.docling = DoclingProcessor()
    
    def process_all_documents(self, 
                            processed_dir: str = "data/processed",
                            use_docling: bool = True) -> Dict:
        """Process all documents and build the vector index."""
        stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'categories': {}
        }
        
        processed_path = Path(processed_dir)
        
        # Process with Docling if enabled
        if use_docling and self.docling.is_available():
            logger.info("Processing documents with Docling")
            docling_docs = self.docling.process_markdown_files(processed_dir)
            
            # Process Docling output
            for doc in docling_docs:
                chunks = self._process_docling_document(doc)
                stats['total_chunks'] += len(chunks)
                
                # Add to vector store
                self.vector_store.add_documents(chunks)
        else:
            # Process markdown files directly
            logger.info("Processing markdown files directly")
            markdown_files = list(processed_path.glob("*.md"))
            
            for md_file in markdown_files:
                category = self._extract_category(md_file.stem)
                logger.info(f"Processing {md_file.name}")
                
                chunks = self._process_markdown_file(md_file)
                stats['total_documents'] += 1
                stats['total_chunks'] += len(chunks)
                stats['categories'][category] = stats['categories'].get(category, 0) + len(chunks)
                
                # Add to vector store
                if chunks:
                    self.vector_store.add_documents(chunks)
        
        logger.info(f"Processing complete. Stats: {stats}")
        return stats
    
    def _process_markdown_file(self, file_path: Path) -> List[Dict]:
        """Process a markdown file into chunks."""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from header
            metadata = self._extract_file_metadata(content, file_path)
            
            # Split into posts (separated by ---)
            posts = content.split('\n---\n')
            
            for post in posts:
                if not post.strip():
                    continue
                
                # Extract post metadata
                post_metadata = self._extract_post_metadata(post)
                post_metadata.update(metadata)
                
                # Create chunks from post
                post_chunks = self._chunk_text(post, post_metadata)
                chunks.extend(post_chunks)
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return chunks
    
    def _process_docling_document(self, doc: Dict) -> List[Dict]:
        """Process a Docling-processed document into chunks."""
        chunks = []
        
        metadata = {
            'source': doc.get('filename', 'unknown'),
            'processed_at': doc.get('processed_at'),
            'category': self._extract_category(doc.get('filename', ''))
        }
        
        # Process sections
        sections = doc.get('sections', [])
        for section in sections:
            section_metadata = metadata.copy()
            section_metadata['section'] = section.get('title', 'Unknown')
            
            content = section.get('content', '')
            if content:
                section_chunks = self._chunk_text(content, section_metadata)
                chunks.extend(section_chunks)
        
        return chunks
    
    def _chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks."""
        chunks = []
        
        # Clean text
        text = text.strip()
        if not text:
            return chunks
        
        # Split by sentences for better chunking
        sentences = self._split_sentences(text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunk_id = self._generate_chunk_id(chunk_text)
                
                chunks.append({
                    'id': chunk_id,
                    'content': chunk_text,
                    'metadata': {
                        **metadata,
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
                    **metadata,
                    'chunk_index': len(chunks),
                    'chunk_length': len(chunk_text)
                }
            })
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter for German text
        sentence_endings = r'[.!?]\s+'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _extract_file_metadata(self, content: str, file_path: Path) -> Dict:
        """Extract metadata from markdown file header."""
        metadata = {
            'source_file': file_path.name,
            'category': self._extract_category(file_path.stem)
        }
        
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('Last Updated:'):
                metadata['last_updated'] = line.replace('Last Updated:', '').strip()
            elif line.startswith('Source URL:'):
                metadata['source_url'] = line.replace('Source URL:', '').strip()
            elif line.startswith('Summary:'):
                metadata['summary'] = line.replace('Summary:', '').strip()
        
        return metadata
    
    def _extract_post_metadata(self, post: str) -> Dict:
        """Extract metadata from a post."""
        metadata = {}
        
        lines = post.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            # Extract date
            date_match = re.match(r'^##\s+(\d{1,2}\.\d{1,2}\.\d{4})', line)
            if date_match:
                metadata['post_date'] = date_match.group(1)
            
            # Extract title
            title_match = re.match(r'^###\s+(.+)', line)
            if title_match:
                metadata['post_title'] = title_match.group(1)
            
            # Extract author
            if line.startswith('**Autor:**'):
                metadata['author'] = line.replace('**Autor:**', '').strip()
        
        return metadata
    
    def _extract_category(self, filename: str) -> str:
        """Extract category from filename."""
        # Remove 'forum_' prefix if present
        category = filename.replace('forum_', '')
        
        # Map to readable names
        category_map = {
            'news': 'News',
            'fitness': 'Fitness',
            'gesundheit': 'Gesundheit',
            'ernaehrung': 'Ernährung',
            'bluttuning': 'Bluttuning',
            'mental': 'Mental',
            'infektion-und-praevention': 'Prävention'
        }
        
        return category_map.get(category, category)
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate unique ID for a chunk."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]