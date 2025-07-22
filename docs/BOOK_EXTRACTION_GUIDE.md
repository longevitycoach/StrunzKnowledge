# Book Extraction Guide: Dr. Strunz PDF Processing with Docling

## Overview

This guide explains how to extract full text and images from Dr. Strunz's PDF books and load them into the FAISS vector database using the Docling document processing library.

## System Architecture

### 1. Book Processing Pipeline

```
PDF Books → Docling → Text/Images → Chunks → Embeddings → FAISS Index
```

1. **PDF Input**: PDF books stored in `data/books/`
2. **Docling Processing**: Advanced PDF extraction with OCR and layout analysis
3. **Text Extraction**: Full text with preserved structure, tables, and metadata
4. **Image Extraction**: Images and diagrams (if present)
5. **Chunking**: Intelligent text chunking (1500 chars with 300 char overlap)
6. **Embeddings**: Sentence-transformer embeddings (384 dimensions)
7. **FAISS Index**: Vector search index for semantic retrieval

### 2. Key Components

- **`src/rag/book_processor.py`**: Main book processing script
- **`src/rag/docling_processor.py`**: Docling service integration
- **`docs/docling_preparation.md`**: Processing guidelines

## Installation & Setup

### Step 1: Install Docling

```bash
# Install docling library (not currently in requirements.txt)
pip install docling

# Or add to requirements.txt:
echo "docling" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Prepare Book Directory

```bash
# Create books directory if it doesn't exist
mkdir -p data/books/

# Place PDF books using proper naming convention:
# Dr.Ulrich-Strunz_Title_Year.pdf
```

### Step 3: Current Dr. Strunz Books

Based on `CLAUDE.md`, you should have these 13 books:

```
data/books/
├── Dr.Ulrich-Strunz_Fitness_drinks_2002.pdf
├── Dr.Ulrich-Strunz_Die_neue_Diaet_Das_Fitnessbuch_2010.pdf
├── Dr.Ulrich-Strunz_Das_Geheimnis_der_Gesundheit_2010.pdf
├── Dr.Ulrich-Strunz_Das_neue_Anti-Krebs-Programm_-_dem_Krebs_keine_Chance_geben__2012.pdf
├── Dr.Ulrich-Strunz_No-Carb-Smoothies_2015.pdf
├── Dr.Ulrich-Strunz_Wunder_der_Heilung_2015.pdf
├── Dr.Ulrich-Strunz_Blut_-_Die_Geheimnisse_Unseres_flussigen_Organs_2016.pdf
├── Dr.Ulrich-Strunz_Das_Strunz-Low-Carb-Kochbuch_2016.pdf
├── Dr.Ulrich-Strunz_Heilung_erfahren_2019.pdf
├── Dr.Ulrich-Strunz_77_Tipps_fuer_Ruecken_und_Gelenke_2021.pdf
├── Dr.Ulrich-Strunz_Das_Stress-weg-Buch_2022.pdf
├── Dr.Ulrich-Strunz_Die_Amino-Revolution_2022.pdf
└── Dr.Ulrich-Strunz_Der_Gen-Trick_2025.pdf
```

## Usage Instructions

### Step 1: Run Book Processing

```bash
# Process all PDF books in data/books/
python -m src.rag.book_processor

# Or run directly
python src/rag/book_processor.py
```

### Step 2: Monitor Processing

The script will:
1. **Scan** `data/books/` for PDF files
2. **Process** each book with Docling
3. **Extract** text, tables, and images
4. **Create** semantic chunks (1500 characters with 300 overlap)
5. **Generate** embeddings using sentence-transformers
6. **Build** FAISS index for book content
7. **Update** combined index with all sources

### Step 3: Processing Output

```
Processing Results:
✓ Found 13 PDF books to process
✓ Processing book: Dr.Ulrich-Strunz_Fitness_drinks_2002.pdf
✓ Created 156 chunks from Fitness_drinks_2002.pdf
✓ Processing book: Dr.Ulrich-Strunz_Die_neue_Diaet_Das_Fitnessbuch_2010.pdf
✓ Created 287 chunks from Die_neue_Diaet_Das_Fitnessbuch_2010.pdf
...
✓ Processing complete:
  - Processed books: 13
  - Error books: 0
  - Total chunks: 2,500
✓ Building FAISS index for 2,500 book chunks...
✓ Saved FAISS index to data/faiss_indices/books/books_index_20250718_143022.faiss
✓ Updated combined index with 2,500 book chunks
✓ Total documents in combined index: 43,373
```

## Technical Details

### 1. Docling Processing Features

```python
# Key features used from Docling:
- DocumentConverter: Main PDF processing class
- export_to_markdown(): Preserves structure and formatting
- Table extraction: Preserves table data and relationships
- Image extraction: Extracts embedded images and diagrams
- OCR capabilities: Handles scanned PDFs and poor quality text
- Layout analysis: Understands document structure (chapters, sections)
```

### 2. Chunking Strategy

```python
# Book-specific chunking parameters:
chunk_size = 1500        # Larger chunks for books (vs 843 for news)
chunk_overlap = 300      # Larger overlap (vs 200 for news)

# Smart chunking preserves:
- Chapter boundaries
- Section breaks  
- Paragraph structure
- Sentence completeness
```

### 3. Metadata Extraction

Each chunk includes:
```json
{
  "text": "Chapter content...",
  "metadata": {
    "source": "book",
    "filename": "Dr.Ulrich-Strunz_Fitness_drinks_2002.pdf",
    "author": "Dr. Ulrich Strunz",
    "title": "Fitness drinks",
    "year": "2002",
    "chunk_id": "a1b2c3d4e5f6...",
    "chunk_index": 42,
    "processed_date": "2025-07-18T14:30:22"
  }
}
```

### 4. FAISS Index Structure

```python
# Index specifications:
embedding_model = "paraphrase-multilingual-MiniLM-L12-v2"
embedding_dim = 384
index_type = "IndexFlatL2"  # Exact similarity search

# File structure:
data/faiss_indices/books/
├── books_index_20250718_143022.faiss     # Vector index
├── books_index_20250718_143022.json      # Metadata
└── combined/
    ├── index.faiss                       # Combined index (all sources)
    └── metadata.json                     # Combined metadata
```

## Integration with Existing System

### 1. Vector Search Integration

The processed books automatically integrate with the existing search system:

```python
# Search across all sources (including books)
from src.rag.search import get_vector_store_singleton
vs = get_vector_store_singleton()
results = vs.search("vitamin D deficiency", k=10)

# Filter to books only
book_results = vs.search("vitamin D", k=10, source_filter=["books"])
```

### 2. MCP Tool Integration

Books are accessible through MCP tools:
```python
# Available in MCP tools:
knowledge_search(query="amino acids", sources=["books"])
trace_topic_evolution(topic="nutrition", sources=["books"])
```

### 3. Combined Index Benefits

After book processing, the system contains:
- **Books**: ~2,500 chunks (13 books, 2002-2025)
- **News**: ~35,000 chunks (6,953 articles, 2004-2025) 
- **Forum**: ~5,873 chunks (community discussions)
- **Total**: ~43,373 searchable documents

## Troubleshooting

### Common Issues

1. **Docling Not Installed**
   ```bash
   ImportError: No module named 'docling'
   # Solution: pip install docling
   ```

2. **No PDFs Found**
   ```bash
   Found 0 PDF books to process
   # Check: ls data/books/*.pdf
   # Ensure PDFs are in correct directory
   ```

3. **Processing Fails**
   ```bash
   Error processing book.pdf: [specific error]
   # Check PDF is not corrupted
   # Verify file permissions
   # Check disk space
   ```

4. **Memory Issues**
   ```bash
   # For large books, increase memory:
   export PYTHONHASHSEED=0
   ulimit -m 8388608  # 8GB
   ```

### Verification

After processing, verify:
```bash
# Check processed files
ls data/processed/books/
ls data/faiss_indices/books/

# Check combined index
python -c "
import json
with open('data/faiss_indices/combined/metadata.json', 'r') as f:
    meta = json.load(f)
print(f'Total documents: {meta[\"total_documents\"]}')
print(f'Sources: {meta.get(\"sources\", [])}')
book_docs = [d for d in meta['documents'] if d.get('metadata', {}).get('source') == 'book']
print(f'Book documents: {len(book_docs)}')
"
```

## Advanced Usage

### Custom Processing

```python
# Process specific book
from src.rag.book_processor import BookProcessor
processor = BookProcessor()

# Process single book
result = processor.process_book(Path("data/books/specific_book.pdf"))

# Custom chunking
chunks = processor.create_chunks(result['content'], result['metadata'])
```

### Batch Processing

```python
# Process books in batches
import glob
from pathlib import Path

pdf_files = glob.glob("data/books/*.pdf")
batch_size = 3

for i in range(0, len(pdf_files), batch_size):
    batch = pdf_files[i:i+batch_size]
    # Process batch...
```

## Integration with Railway Deployment

The book processing creates the FAISS indices that are deployed to Railway:

1. **Local Processing**: Books processed locally with full Docling
2. **Index Creation**: FAISS indices created and chunked for GitHub
3. **Railway Deployment**: Indices reconstructed during Docker build
4. **Production Search**: Books searchable through MCP tools in production

This ensures the full Dr. Strunz knowledge base (books + news + forum) is available in production while keeping the repository size manageable.

## Next Steps

1. **Install Docling**: Add to requirements if not present
2. **Prepare Books**: Ensure all 13 books are in `data/books/`
3. **Run Processing**: Execute book processor script
4. **Verify Results**: Check combined index has book content
5. **Test Search**: Verify book content is searchable
6. **Deploy**: Push updated indices to production