#!/usr/bin/env python3
"""
PDF Processor - Extract text from Dr. Strunz PDFs and integrate into knowledge base
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime
import re
import hashlib

# PDF processing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF books and integrate into the knowledge base."""
    
    def __init__(self, books_dir: str = "data/books", output_dir: str = "data/processed"):
        self.books_dir = Path(books_dir)
        self.output_dir = Path(output_dir)
        self.books_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if PDF processing libraries are available."""
        deps = {
            'PyPDF2': PYPDF2_AVAILABLE,
            'pdfplumber': PDFPLUMBER_AVAILABLE
        }
        
        logger.info("PDF Processing Dependencies:")
        for lib, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            logger.info(f"  {lib}: {status}")
        
        if not any(deps.values()):
            logger.error("No PDF processing libraries available!")
            logger.info("Install with: pip install PyPDF2 pdfplumber")
        
        return deps
    
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in the books directory."""
        pdf_files = list(self.books_dir.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {self.books_dir}")
        for pdf_file in pdf_files:
            size_mb = pdf_file.stat().st_size / 1024 / 1024
            logger.info(f"  - {pdf_file.name} ({size_mb:.1f} MB)")
        
        return pdf_files
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2."""
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        
        except Exception as e:
            logger.error(f"Error reading PDF with PyPDF2: {e}")
            
        return text
    
    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (more accurate)."""
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        
        except Exception as e:
            logger.error(f"Error reading PDF with pdfplumber: {e}")
            
        return text
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using best available method."""
        logger.info(f"Extracting text from: {pdf_path.name}")
        
        text = ""
        
        # Try pdfplumber first (more accurate)
        if PDFPLUMBER_AVAILABLE:
            logger.info("Using pdfplumber for text extraction")
            text = self.extract_text_pdfplumber(pdf_path)
        
        # Fallback to PyPDF2
        if not text and PYPDF2_AVAILABLE:
            logger.info("Falling back to PyPDF2 for text extraction")
            text = self.extract_text_pypdf2(pdf_path)
        
        if not text:
            logger.error(f"Failed to extract text from {pdf_path.name}")
        else:
            logger.info(f"Extracted {len(text)} characters from {pdf_path.name}")
        
        return text
    
    def extract_metadata(self, pdf_path: Path, text: str) -> Dict:
        """Extract metadata from PDF and text content."""
        metadata = {
            'source_file': pdf_path.name,
            'source_path': str(pdf_path),
            'category': 'book',
            'content_type': 'book',
            'author': 'Dr. Ulrich Strunz',
            'file_size': pdf_path.stat().st_size,
            'processed_at': datetime.now().isoformat()
        }
        
        # Extract title from filename
        filename_parts = pdf_path.stem.replace('_', ' ').replace('-', ' ')
        # Remove common prefixes
        title = re.sub(r'^(Strunz|Dr|Ulrich)\s*', '', filename_parts, flags=re.IGNORECASE)
        metadata['title'] = title.strip() or pdf_path.stem
        
        # Try to extract publication year
        year_match = re.search(r'(19|20)\d{2}', filename_parts)
        if year_match:
            metadata['year'] = year_match.group(0)
        
        # Extract language (assume German for Dr. Strunz)
        metadata['language'] = 'de'
        
        # Try to detect book topic from title
        topics = []
        title_lower = metadata['title'].lower()
        
        topic_keywords = {
            'fitness': ['fitness', 'training', 'sport', 'bewegung'],
            'nutrition': ['diät', 'ernährung', 'nahrung', 'essen'],
            'health': ['gesundheit', 'medizin', 'heilung', 'krankheit'],
            'genetics': ['gen', 'epigenetik', 'dna', 'vererbung'],
            'wellness': ['young', 'forever', 'jung', 'wohlbefinden']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                topics.append(topic)
        
        if topics:
            metadata['topics'] = topics
            metadata['primary_topic'] = topics[0]
        
        return metadata
    
    def create_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Create text chunks with overlap."""
        chunks = []
        
        if not text or len(text.strip()) < 50:
            return chunks
        
        # Clean text
        text = self._clean_text(text)
        
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
                        **metadata,
                        'chunk_index': len(chunks),
                        'chunk_length': len(chunk_text),
                        'source_type': 'book'
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
                    'chunk_length': len(chunk_text),
                    'source_type': 'book'
                }
            })
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove page markers
        text = re.sub(r'\n--- Page \d+ ---\n', '\n', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'\s+', ' ', text)  # Multiple whitespace
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Hyphenated words
        text = text.replace('\n', ' ')  # Line breaks
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # German sentence splitter
        sentence_endings = r'[.!?]\s+'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate unique ID for a chunk."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def process_all_pdfs(self) -> Dict:
        """Process all PDF files in the books directory."""
        logger.info("Starting PDF processing...")
        
        # Check dependencies
        deps = self.check_dependencies()
        if not any(deps.values()):
            return {'error': 'No PDF processing libraries available'}
        
        # Find PDF files
        pdf_files = self.find_pdf_files()
        if not pdf_files:
            logger.warning("No PDF files found to process")
            return {'total_files': 0, 'processed_files': 0, 'total_chunks': 0}
        
        # Process each PDF
        all_processed_docs = []
        stats = {
            'total_files': len(pdf_files),
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0
        }
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"\n--- Processing: {pdf_file.name} ---")
                
                # Extract text
                text = self.extract_text_from_pdf(pdf_file)
                
                if not text:
                    logger.error(f"No text extracted from {pdf_file.name}")
                    stats['failed_files'] += 1
                    continue
                
                # Extract metadata
                metadata = self.extract_metadata(pdf_file, text)
                
                # Create chunks
                chunks = self.create_chunks(text, metadata)
                
                if not chunks:
                    logger.error(f"No chunks created from {pdf_file.name}")
                    stats['failed_files'] += 1
                    continue
                
                # Create document record
                doc = {
                    'filename': pdf_file.name,
                    'category': 'book',
                    'processed_at': datetime.now().isoformat(),
                    'original_length': len(text),
                    'metadata': metadata,
                    'chunks': chunks
                }
                
                all_processed_docs.append(doc)
                stats['processed_files'] += 1
                stats['total_chunks'] += len(chunks)
                
                logger.info(f"✅ Successfully processed {pdf_file.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                stats['failed_files'] += 1
        
        # Save processed documents
        if all_processed_docs:
            output_file = self.output_dir / "books_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_processed_docs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(all_processed_docs)} processed books to {output_file}")
        
        logger.info(f"\n=== PDF Processing Complete ===")
        logger.info(f"Total files: {stats['total_files']}")
        logger.info(f"Processed: {stats['processed_files']}")
        logger.info(f"Failed: {stats['failed_files']}")
        logger.info(f"Total chunks: {stats['total_chunks']}")
        
        return stats


def main():
    """Main function."""
    print("=== Dr. Strunz PDF Processor ===")
    print("Processing PDF books for knowledge base integration")
    print()
    
    processor = PDFProcessor()
    
    # Check for PDF files
    pdf_files = processor.find_pdf_files()
    if not pdf_files:
        print("❌ No PDF files found in data/books/")
        print()
        print("📥 To add PDF files:")
        print("1. Obtain Dr. Strunz books through legal channels")
        print("2. Place PDF files in data/books/ directory")
        print("3. Run this processor again")
        return
    
    # Process PDFs
    stats = processor.process_all_pdfs()
    
    if 'error' in stats:
        print(f"❌ {stats['error']}")
        print("Install PDF libraries: pip install PyPDF2 pdfplumber")
    else:
        print(f"\n✅ PDF processing completed!")
        print(f"Processed {stats['processed_files']} books with {stats['total_chunks']} chunks")
        
        if stats['processed_files'] > 0:
            print("\n🔄 Next steps:")
            print("1. Update FAISS vector index with book content")
            print("2. Test search functionality")
            print("3. Deploy updated knowledge base")


if __name__ == "__main__":
    main()