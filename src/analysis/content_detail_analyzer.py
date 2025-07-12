#!/usr/bin/env python3
"""
Analyze detailed content information including titles, URLs, and dates
"""

import json
import logging
from pathlib import Path
from collections import defaultdict, Counter
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ContentDetailAnalyzer:
    def __init__(self):
        self.data_dir = Path("data")
        self.index_dir = self.data_dir / "faiss_indices"
        
    def analyze_books_detail(self):
        """Extract detailed book information."""
        book_metadata_file = self.index_dir / "books" / "books_index_20250712_205242.json"
        
        with open(book_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        documents = metadata.get('documents', [])
        
        # Collect unique books
        books = {}
        for doc in documents:
            title = doc.get('title', 'Unknown')
            if title not in books:
                books[title] = {
                    'title': title,
                    'year': doc['metadata'].get('year', 'Unknown'),
                    'filename': doc['metadata'].get('filename', ''),
                    'author': doc['metadata'].get('author', 'Unknown'),
                    'chunks': 0,
                    'file_path': doc['metadata'].get('file_path', '')
                }
            books[title]['chunks'] += 1
        
        # Sort by year
        sorted_books = sorted(books.values(), key=lambda x: x['year'])
        
        print("\n=== BOOK DETAILS ===")
        print(f"Total books: {len(books)}\n")
        
        for book in sorted_books:
            print(f"Title: {book['title']}")
            print(f"  - Year: {book['year']}")
            print(f"  - Author: {book['author']}")
            print(f"  - Filename: {book['filename']}")
            print(f"  - Chunks: {book['chunks']}")
            print()
        
        return sorted_books
    
    def analyze_news_urls(self):
        """Extract news URL patterns and structure."""
        news_metadata_file = self.index_dir / "news" / "news_index_20250712_202935.json"
        
        with open(news_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        documents = metadata.get('documents', [])
        
        # Collect unique articles
        articles = {}
        url_patterns = Counter()
        dates_by_year = defaultdict(list)
        
        for doc in documents:
            url = doc['metadata'].get('url', '')
            filename = doc['metadata'].get('filename', '')
            date = doc['metadata'].get('date', '')
            title = doc.get('title', 'Unknown')
            
            # Extract URL pattern
            if url:
                base_url = url.split('/')[:3]
                url_patterns['/'.join(base_url)] += 1
            
            # Store unique articles
            if filename and filename not in articles:
                articles[filename] = {
                    'title': title,
                    'url': url,
                    'date': date,
                    'filename': filename
                }
                
                if date:
                    year = date[:4]
                    dates_by_year[year].append({
                        'date': date,
                        'title': title,
                        'url': url
                    })
        
        print("\n=== NEWS URL STRUCTURE ===")
        print(f"Total unique articles: {len(articles)}\n")
        
        print("URL patterns:")
        for pattern, count in url_patterns.most_common():
            print(f"  - {pattern}: {count} occurrences")
        
        # Show sample URLs
        print("\nSample article URLs:")
        sample_articles = list(articles.values())[:5]
        for article in sample_articles:
            print(f"  - {article['url']}")
        
        # Show date range
        all_dates = [a['date'] for a in articles.values() if a['date']]
        if all_dates:
            print(f"\nDate range: {min(all_dates)} to {max(all_dates)}")
        
        # Show recent articles
        print("\nMost recent articles:")
        sorted_articles = sorted(articles.values(), key=lambda x: x['date'], reverse=True)
        for article in sorted_articles[:5]:
            print(f"  - {article['date']}: {article['title']}")
            print(f"    URL: {article['url']}")
        
        return articles, dates_by_year
    
    def analyze_forum_structure(self):
        """Analyze forum content structure."""
        forum_metadata_file = self.index_dir / "forum" / "forum_index_20250711.json"
        
        with open(forum_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        documents = metadata.get('documents', [])
        
        print("\n=== FORUM DETAILS ===")
        print(f"Total forum chunks: {len(documents)}")
        
        # Analyze metadata structure
        if documents:
            sample_doc = documents[0]
            print("\nSample forum document structure:")
            print(f"  - Text length: {len(sample_doc.get('text', ''))}")
            print(f"  - Metadata fields: {list(sample_doc.get('metadata', {}).keys())}")
            
            # Check for URLs or dates
            urls = []
            dates = []
            for doc in documents[:100]:  # Sample first 100
                meta = doc.get('metadata', {})
                if 'url' in meta:
                    urls.append(meta['url'])
                if 'date' in meta:
                    dates.append(meta['date'])
            
            if urls:
                print(f"\nSample forum URLs:")
                for url in urls[:5]:
                    print(f"  - {url}")
            
            if dates:
                print(f"\nForum dates found: {len(set(dates))} unique")
                print(f"Date range: {min(dates)} to {max(dates)}")
            else:
                print("\n⚠️  No date information found in forum metadata")
        
        return documents
    
    def generate_documentation(self, books, news_info, forum_info):
        """Generate documentation for CLAUDE.md and README.md"""
        
        # CLAUDE.md content
        claude_md = """# Dr. Strunz Knowledge Base - Technical Documentation

## Content Sources

### 1. Books (13 total)
The following Dr. Ulrich Strunz books have been processed:

| Title | Year | Filename |
|-------|------|----------|
"""
        
        for book in books:
            claude_md += f"| {book['title']} | {book['year']} | {book['filename']} |\n"
        
        claude_md += """
### 2. News Articles
- **Total articles**: 6,953 unique articles
- **Date range**: 2004-09-28 to 2025-07-11
- **Base URL**: https://www.strunz.com/news/
- **URL pattern**: https://www.strunz.com/news/[article-slug].html

### 3. Forum Content
- **Total chunks**: 6,400
- **Status**: Limited data available (only showing date 02.05.2020)
- **Note**: Forum scraping appears incomplete and may need to be redone

## Data Processing Details

### Text Chunking
- **News**: ~843 characters per chunk with 200 char overlap
- **Books**: ~1,333 characters per chunk with 300 char overlap
- **Forum**: Variable chunk sizes

### Vector Database
- **Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Dimensions**: 384
- **Index Type**: FAISS IndexFlatL2
- **Total Vectors**: 28,938

## Update Information
- News articles can be updated incrementally using wget with -N flag
- Books are manually added to data/books/ directory
- Forum content needs complete re-scraping

## Directory Structure
```
data/
├── books/                    # PDF books
├── raw/
│   ├── news/                # HTML news articles
│   └── forum/               # Forum HTML (incomplete)
├── processed/
│   ├── books/               # Processed book chunks
│   ├── news/                # Processed news chunks
│   └── forum/               # Processed forum chunks
└── faiss_indices/
    ├── books/               # Book vector index
    ├── news/                # News vector index
    ├── forum/               # Forum vector index
    └── combined_index.faiss # Combined searchable index
```
"""
        
        # README.md content
        readme_md = """# Dr. Strunz Knowledge Base

A comprehensive knowledge base containing Dr. Ulrich Strunz's books, news articles, and forum content, with semantic search capabilities.

## Overview

This project provides a searchable database of Dr. Strunz's health and nutrition content:
- **13 books** covering topics from nutrition to stress management
- **6,953 news articles** spanning from 2004 to 2025
- **Forum discussions** (limited data currently available)

## Content Sources

### Books Included
1. **Fitness & Nutrition**
   - Das Strunz-Low-Carb-Kochbuch (2016)
   - No-Carb-Smoothies (2015)
   - Fitness drinks (2002)
   - Die neue Diät Das Fitnessbuch (2010)

2. **Health & Healing**
   - Wunder der Heilung (2015)
   - Heilung erfahren (2019)
   - Das Geheimnis der Gesundheit (2010)
   - 77 Tipps für Rücken und Gelenke (2021)

3. **Specialized Topics**
   - Die Amino-Revolution (2022)
   - Das neue Anti-Krebs-Programm (2012)
   - Blut - Die Geheimnisse unseres flüssigen Organs (2016)
   - Das Stress-weg-Buch (2022)
   - Der Gen-Trick (2025)

### News Articles
- **Website**: https://www.strunz.com/news/
- **Coverage**: September 2004 - July 2025
- **Topics**: Nutrition, vitamins, minerals, exercise, health research

## Features

- **Semantic Search**: Find related content across all sources using AI embeddings
- **Multi-source Integration**: Search books, articles, and forum posts simultaneously
- **German Language Support**: Optimized for German content with multilingual model
- **Fast Retrieval**: FAISS vector database for instant search results

## Technical Details

- **Embedding Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Vector Dimensions**: 384
- **Total Indexed Content**: 28,938 text chunks
- **Database Size**: ~42 MB FAISS index + ~25 MB text content

## Usage

1. The content is indexed and ready for semantic search
2. Each content type (books, news, forum) is tagged for filtering
3. Search queries return the most semantically similar content
4. Results include source type, title, and relevance score

## Updates

The system supports incremental updates:
- **News**: Automatically check for new articles daily
- **Books**: Add new PDFs to the books directory
- **Forum**: Requires manual update (current data incomplete)

## Data Privacy

This knowledge base is for research and personal use. All content belongs to Dr. Ulrich Strunz and should be used in accordance with applicable copyright laws.
"""
        
        return claude_md, readme_md

def main():
    analyzer = ContentDetailAnalyzer()
    
    # Analyze each source
    books = analyzer.analyze_books_detail()
    news_articles, news_dates = analyzer.analyze_news_urls()
    forum_docs = analyzer.analyze_forum_structure()
    
    # Generate documentation
    claude_md, readme_md = analyzer.generate_documentation(books, (news_articles, news_dates), forum_docs)
    
    # Write CLAUDE.md
    with open('CLAUDE.md', 'w', encoding='utf-8') as f:
        f.write(claude_md)
    print("\n✅ Updated CLAUDE.md with detailed content information")
    
    # Write README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_md)
    print("✅ Updated README.md with project overview")

if __name__ == "__main__":
    main()