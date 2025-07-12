#!/usr/bin/env python3
"""
Analyze content dates from all sources and store latest update information
for future incremental updates
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ContentDateAnalyzer:
    def __init__(self):
        self.data_dir = Path("data")
        self.index_dir = self.data_dir / "faiss_indices"
        self.update_info_file = self.data_dir / "update_info.json"
        
    def analyze_forum_dates(self):
        """Analyze forum content dates."""
        forum_metadata_file = self.index_dir / "forum" / "forum_index_20250711.json"
        
        if not forum_metadata_file.exists():
            logging.warning("Forum metadata not found")
            return None
            
        with open(forum_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        documents = metadata.get('documents', [])
        dates = []
        
        for doc in documents:
            # Forum content might have different date fields
            if 'date' in doc.get('metadata', {}):
                dates.append(doc['metadata']['date'])
            elif 'processed_date' in doc.get('metadata', {}):
                dates.append(doc['metadata']['processed_date'][:10])
                
        if dates:
            latest_date = max(dates)
            earliest_date = min(dates)
            
            return {
                'source': 'forum',
                'total_documents': len(documents),
                'latest_content_date': latest_date,
                'earliest_content_date': earliest_date,
                'date_count': len(set(dates)),
                'processed_date': metadata.get('created_date', 'Unknown'),
                'index_file': str(forum_metadata_file)
            }
        
        return None
    
    def analyze_news_dates(self):
        """Analyze news content dates and find latest article."""
        news_metadata_file = self.index_dir / "news" / "news_index_20250712_202935.json"
        
        if not news_metadata_file.exists():
            logging.warning("News metadata not found")
            return None
            
        with open(news_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        documents = metadata.get('documents', [])
        
        # Collect all articles with dates
        articles = {}
        for doc in documents:
            if 'date' in doc.get('metadata', {}):
                date = doc['metadata']['date']
                title = doc.get('title', 'Unknown')
                filename = doc['metadata'].get('filename', '')
                
                if date not in articles:
                    articles[date] = []
                
                # Store unique articles only
                article_info = {
                    'title': title,
                    'filename': filename,
                    'url': doc['metadata'].get('url', '')
                }
                
                # Check if this article is already added (different chunks of same article)
                if not any(a['filename'] == filename for a in articles[date]):
                    articles[date].append(article_info)
        
        if articles:
            sorted_dates = sorted(articles.keys(), reverse=True)
            latest_date = sorted_dates[0]
            earliest_date = sorted_dates[-1]
            
            # Get latest articles
            latest_articles = articles[latest_date][:5]  # Top 5 latest
            
            # Count articles by year
            year_counts = defaultdict(int)
            for date in articles.keys():
                year = int(date[:4])
                year_counts[year] += len(articles[date])
            
            return {
                'source': 'news',
                'total_documents': len(documents),
                'total_unique_articles': sum(len(arts) for arts in articles.values()),
                'latest_content_date': latest_date,
                'earliest_content_date': earliest_date,
                'latest_articles': latest_articles,
                'articles_by_year': dict(sorted(year_counts.items(), reverse=True)),
                'processed_date': metadata.get('created_date', 'Unknown'),
                'index_file': str(news_metadata_file)
            }
        
        return None
    
    def analyze_book_dates(self):
        """Analyze book content dates."""
        book_metadata_file = self.index_dir / "books" / "books_index_20250712_205242.json"
        
        if not book_metadata_file.exists():
            logging.warning("Book metadata not found")
            return None
            
        with open(book_metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        documents = metadata.get('documents', [])
        
        # Collect book information
        books = {}
        for doc in documents:
            book_title = doc.get('title', 'Unknown')
            year = doc['metadata'].get('year', 'Unknown')
            filename = doc['metadata'].get('filename', '')
            
            if book_title not in books:
                books[book_title] = {
                    'title': book_title,
                    'year': year,
                    'filename': filename,
                    'chunks': 0
                }
            
            books[book_title]['chunks'] += 1
        
        # Sort books by year
        sorted_books = sorted(books.values(), key=lambda x: x['year'], reverse=True)
        
        years = [b['year'] for b in sorted_books if b['year'] != 'Unknown']
        latest_year = max(years) if years else 'Unknown'
        earliest_year = min(years) if years else 'Unknown'
        
        return {
            'source': 'books',
            'total_documents': len(documents),
            'total_books': len(books),
            'latest_book_year': latest_year,
            'earliest_book_year': earliest_year,
            'books': sorted_books,
            'processed_date': metadata.get('created_date', 'Unknown'),
            'index_file': str(book_metadata_file)
        }
    
    def save_update_info(self, forum_info, news_info, book_info):
        """Save update information for future scripts."""
        update_info = {
            'last_analysis_date': datetime.now().isoformat(),
            'sources': {
                'forum': forum_info,
                'news': news_info,
                'books': book_info
            },
            'update_markers': {
                'forum': {
                    'last_known_date': forum_info['latest_content_date'] if forum_info else None,
                    'last_processed': forum_info['processed_date'] if forum_info else None
                },
                'news': {
                    'last_known_date': news_info['latest_content_date'] if news_info else None,
                    'last_known_articles': news_info['latest_articles'] if news_info else [],
                    'last_processed': news_info['processed_date'] if news_info else None
                },
                'books': {
                    'last_known_year': book_info['latest_book_year'] if book_info else None,
                    'book_count': book_info['total_books'] if book_info else 0,
                    'last_processed': book_info['processed_date'] if book_info else None
                }
            }
        }
        
        with open(self.update_info_file, 'w', encoding='utf-8') as f:
            json.dump(update_info, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Update information saved to {self.update_info_file}")
        
    def print_summary(self, forum_info, news_info, book_info):
        """Print analysis summary."""
        print("\n" + "="*60)
        print("CONTENT DATE ANALYSIS")
        print("="*60)
        
        if forum_info:
            print(f"\nFORUM CONTENT:")
            print(f"  - Total chunks: {forum_info['total_documents']:,}")
            print(f"  - Date range: {forum_info['earliest_content_date']} to {forum_info['latest_content_date']}")
            print(f"  - Unique dates: {forum_info['date_count']}")
            print(f"  - Processed: {forum_info['processed_date'][:10] if forum_info['processed_date'] != 'Unknown' else 'Unknown'}")
        
        if news_info:
            print(f"\nNEWS CONTENT:")
            print(f"  - Total chunks: {news_info['total_documents']:,}")
            print(f"  - Unique articles: {news_info['total_unique_articles']:,}")
            print(f"  - Date range: {news_info['earliest_content_date']} to {news_info['latest_content_date']}")
            print(f"  - Processed: {news_info['processed_date'][:10] if news_info['processed_date'] != 'Unknown' else 'Unknown'}")
            
            print(f"\n  Latest articles ({news_info['latest_content_date']}):")
            for article in news_info['latest_articles']:
                print(f"    - {article['title']}")
            
            print(f"\n  Recent years:")
            recent_years = sorted(news_info['articles_by_year'].items(), reverse=True)[:5]
            for year, count in recent_years:
                print(f"    - {year}: {count} articles")
        
        if book_info:
            print(f"\nBOOK CONTENT:")
            print(f"  - Total chunks: {book_info['total_documents']:,}")
            print(f"  - Total books: {book_info['total_books']}")
            print(f"  - Year range: {book_info['earliest_book_year']} to {book_info['latest_book_year']}")
            print(f"  - Processed: {book_info['processed_date'][:10] if book_info['processed_date'] != 'Unknown' else 'Unknown'}")
            
            print(f"\n  Recent books:")
            for book in book_info['books'][:5]:
                print(f"    - {book['year']}: {book['title']} ({book['chunks']} chunks)")

def main():
    analyzer = ContentDateAnalyzer()
    
    # Analyze each source
    logging.info("Analyzing forum content dates...")
    forum_info = analyzer.analyze_forum_dates()
    
    logging.info("Analyzing news content dates...")
    news_info = analyzer.analyze_news_dates()
    
    logging.info("Analyzing book content dates...")
    book_info = analyzer.analyze_book_dates()
    
    # Save update information
    analyzer.save_update_info(forum_info, news_info, book_info)
    
    # Print summary
    analyzer.print_summary(forum_info, news_info, book_info)
    
    print(f"\n✅ Analysis complete! Update information saved to data/update_info.json")
    print("\nThis file can be used by future update scripts to:")
    print("  - Check for new forum posts after the last known date")
    print("  - Download only new news articles")
    print("  - Detect when new books are added")

if __name__ == "__main__":
    main()