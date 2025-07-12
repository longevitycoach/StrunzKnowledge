#!/usr/bin/env python3
"""
Process PDF books using PyPDF2 and build/update FAISS index
Simpler and faster than Docling for text extraction
Ensures book content is properly tagged and separated from forum and news content
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import re

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pypdfium2 as pdfium

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BookProcessor:
    def __init__(self):
        self.data_dir = Path("data")
        self.books_dir = self.data_dir / "books"
        self.processed_dir = self.data_dir / "processed" / "books"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Model for embeddings (same as other processors)
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.embedding_dim = 384
        
        # Chunk settings - larger for books
        self.chunk_size = 1500
        self.chunk_overlap = 300
        
    def extract_book_metadata(self, pdf_path: Path) -> Dict:
        """Extract metadata from book filename and content."""
        # Parse filename: Dr.Ulrich-Strunz_Title_Year.pdf
        filename = pdf_path.stem
        parts = filename.split('_')
        
        metadata = {
            'source': 'book',  # Important: Mark as book content
            'filename': pdf_path.name,
            'author': 'Dr. Ulrich Strunz',
            'processed_date': datetime.now().isoformat(),
            'file_path': str(pdf_path)
        }
        
        # Extract year from filename
        year_match = re.search(r'_(\d{4})$', filename)
        if year_match:
            metadata['year'] = year_match.group(1)
            # Extract title (everything between author and year)
            title_part = filename.replace('Dr.Ulrich-Strunz_', '').replace(f'_{year_match.group(1)}', '')
            metadata['title'] = title_part.replace('_', ' ')
        else:
            # No year found, use full name after author as title
            metadata['title'] = filename.replace('Dr.Ulrich-Strunz_', '').replace('_', ' ')
        
        return metadata
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using pypdfium2."""
        try:
            text_parts = []
            
            # Load PDF
            pdf = pdfium.PdfDocument(str(pdf_path))
            
            # Extract text from each page
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                if text:
                    text_parts.append(f"\n\n--- Page {page_num + 1} ---\n\n{text}")
            
            # Close the PDF
            pdf.close()
            
            return '\n'.join(text_parts)
            
        except Exception as e:
            logging.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def process_book(self, pdf_path: Path) -> Optional[Dict]:
        """Process a single book PDF."""
        try:
            logging.info(f"Processing book: {pdf_path.name}")
            
            # Extract metadata
            metadata = self.extract_book_metadata(pdf_path)
            
            # Extract text content
            full_content = self.extract_text_from_pdf(pdf_path)
            
            # Clean up text
            full_content = re.sub(r'\n{3,}', '\n\n', full_content)
            full_content = re.sub(r' {2,}', ' ', full_content)
            full_content = full_content.strip()
            
            if not full_content:
                logging.warning(f"No content extracted from {pdf_path.name}")
                return None
            
            logging.info(f"Extracted {len(full_content)} characters from {pdf_path.name}")
            
            return {
                'content': full_content,
                'metadata': metadata,
                'title': metadata['title']
            }
            
        except Exception as e:
            logging.error(f"Error processing {pdf_path}: {e}")
            return None
    
    def create_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Create overlapping chunks from text."""
        chunks = []
        
        if not text:
            return chunks
        
        # For books, try to preserve chapter/section boundaries
        # Look for common chapter patterns
        chapter_patterns = [
            r'\n(?=(?:Kapitel|Chapter|KAPITEL|CHAPTER)\s+[\dIVXLCDM]+)',
            r'\n(?=\d+\.\s+[A-Z])',
            r'\n(?=(?:Teil|Part|TEIL|PART)\s+[\dIVXLCDM]+)',
            r'\n{2,}(?=[A-Z][A-Z\s]{10,}\n)'  # All caps headings
        ]
        
        sections = [text]
        for pattern in chapter_patterns:
            new_sections = []
            for section in sections:
                split_sections = re.split(pattern, section, flags=re.MULTILINE)
                new_sections.extend(split_sections)
            sections = new_sections
            if len(sections) > 1:  # Found a pattern that splits the text
                break
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # If section is small enough, keep it as one chunk
            if len(section) <= self.chunk_size:
                chunks.append({
                    'text': section,
                    'metadata': metadata.copy()
                })
            else:
                # Split large sections into chunks
                sentences = re.split(r'(?<=[.!?])\s+', section)
                
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
        
        # Add chunk IDs and book title to each chunk
        for i, chunk in enumerate(chunks):
            chunk['metadata']['chunk_id'] = hashlib.md5(
                f"{metadata['filename']}_{i}_{chunk['text'][:50]}".encode()
            ).hexdigest()
            chunk['metadata']['chunk_index'] = i
            chunk['title'] = metadata['title']
        
        return chunks
    
    def process_all_books(self) -> Dict:
        """Process all PDF books in the books directory."""
        pdf_files = list(self.books_dir.glob("*.pdf"))
        
        logging.info(f"Found {len(pdf_files)} PDF books to process")
        
        all_documents = []
        processed_count = 0
        error_count = 0
        
        for pdf_file in pdf_files:
            # Process book
            result = self.process_book(pdf_file)
            
            if result and result['content']:
                # Create chunks
                chunks = self.create_chunks(result['content'], result['metadata'])
                
                logging.info(f"Created {len(chunks)} chunks from {pdf_file.name}")
                all_documents.extend(chunks)
                
                processed_count += 1
            else:
                error_count += 1
        
        # Save processed documents
        output_file = self.processed_dir / f"book_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        logging.info(f"Building FAISS index for {len(documents)} book chunks...")
        
        # Generate embeddings
        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save index
        index_dir = self.data_dir / "faiss_indices" / "books"
        index_dir.mkdir(parents=True, exist_ok=True)
        
        index_file = index_dir / f"books_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.faiss"
        faiss.write_index(index, str(index_file))
        
        # Save metadata
        metadata_file = index_file.with_suffix('.json')
        metadata = {
            'documents': documents,
            'total_documents': len(documents),
            'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'embedding_dim': self.embedding_dim,
            'created_date': datetime.now().isoformat(),
            'source': 'book'
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved FAISS index to {index_file}")
        
        return str(index_file)
    
    def update_combined_index(self, book_index_file: str):
        """Update the combined FAISS index with book data."""
        logging.info("Updating combined FAISS index with book data...")
        
        # Load existing combined index if exists
        combined_index_dir = self.data_dir / "faiss_indices"
        combined_index_file = combined_index_dir / "combined_index.faiss"
        combined_metadata_file = combined_index_dir / "combined_metadata.json"
        
        # Load book index and metadata
        book_index = faiss.read_index(book_index_file)
        with open(Path(book_index_file).with_suffix('.json'), 'r') as f:
            book_metadata = json.load(f)
        
        if combined_index_file.exists():
            # Load existing combined index
            combined_index = faiss.read_index(str(combined_index_file))
            with open(combined_metadata_file, 'r') as f:
                combined_metadata = json.load(f)
            
            # Merge indices
            combined_index.add(book_index.reconstruct_n(0, book_index.ntotal))
            
            # Update metadata - mark book documents
            for doc in book_metadata['documents']:
                doc['metadata']['content_type'] = 'book'
            
            combined_metadata['documents'].extend(book_metadata['documents'])
            combined_metadata['total_documents'] = len(combined_metadata['documents'])
            combined_metadata['last_updated'] = datetime.now().isoformat()
            combined_metadata['sources'] = list(set(
                combined_metadata.get('sources', []) + ['book']
            ))
        else:
            # Create new combined index with book data
            combined_index = book_index
            combined_metadata = book_metadata
            combined_metadata['sources'] = ['book']
        
        # Save updated combined index
        faiss.write_index(combined_index, str(combined_index_file))
        with open(combined_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(combined_metadata, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Updated combined index with {book_metadata['total_documents']} book chunks")
        logging.info(f"Total documents in combined index: {combined_metadata['total_documents']}")

def main():
    processor = BookProcessor()
    
    # Process all books
    logging.info("Starting book processing...")
    result = processor.process_all_books()
    
    logging.info(f"Processing complete:")
    logging.info(f"  - Processed books: {result['processed_files']}")
    logging.info(f"  - Error books: {result['error_files']}")
    logging.info(f"  - Total chunks: {result['total_chunks']}")
    
    if result['total_chunks'] > 0:
        # Load processed documents
        with open(result['output_file'], 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # Build FAISS index
        index_file = processor.build_faiss_index(documents)
        
        # Update combined index
        processor.update_combined_index(index_file)
        
        logging.info("✅ Book processing and indexing complete!")

if __name__ == "__main__":
    main()