#!/usr/bin/env python3
"""
Update content by checking for new articles, forum posts, and books
Uses the update_info.json to perform incremental updates
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ContentUpdater:
    def __init__(self):
        self.data_dir = Path("data")
        self.update_info_file = self.data_dir / "update_info.json"
        self.load_update_info()
        
    def load_update_info(self):
        """Load the last update information."""
        if self.update_info_file.exists():
            with open(self.update_info_file, 'r', encoding='utf-8') as f:
                self.update_info = json.load(f)
        else:
            logging.warning("No update info found. Run content_date_analyzer.py first.")
            self.update_info = None
    
    def check_news_updates(self):
        """Check for new news articles since last update."""
        if not self.update_info:
            return
            
        last_date = self.update_info['update_markers']['news']['last_known_date']
        last_articles = self.update_info['update_markers']['news']['last_known_articles']
        
        print(f"\n=== CHECKING NEWS UPDATES ===")
        print(f"Last known article date: {last_date}")
        print(f"Last known articles:")
        for article in last_articles[:3]:
            print(f"  - {article['title']}")
        
        # Convert date string to datetime for comparison
        last_datetime = datetime.strptime(last_date, "%Y-%m-%d")
        days_since = (datetime.now() - last_datetime).days
        
        print(f"\nDays since last update: {days_since}")
        
        if days_since > 0:
            print(f"⚠️  Potential new articles available!")
            print(f"Run news scraper to check for articles after {last_date}")
            
            # Create wget command for incremental update
            print("\nSuggested command for incremental news update:")
            print(f"cd data/raw/news && wget -r -l 1 -H -t 1 -nd -N -np -A '*.html' -erobots=off https://www.strunz.com/news/")
            print("(The -N flag will only download files newer than existing ones)")
        else:
            print("✅ News content appears to be up to date")
    
    def check_forum_updates(self):
        """Check for new forum posts since last update."""
        if not self.update_info:
            return
            
        last_date = self.update_info['update_markers']['forum']['last_known_date']
        
        print(f"\n=== CHECKING FORUM UPDATES ===")
        print(f"Last known forum date: {last_date}")
        
        # Note: The forum data shows only one date (02.05.2020), which seems incomplete
        print("⚠️  Forum data appears incomplete (only one date found)")
        print("Consider re-scraping forum content to get complete date range")
    
    def check_book_updates(self):
        """Check for new books."""
        if not self.update_info:
            return
            
        last_year = self.update_info['update_markers']['books']['last_known_year']
        book_count = self.update_info['update_markers']['books']['book_count']
        
        print(f"\n=== CHECKING BOOK UPDATES ===")
        print(f"Last known book year: {last_year}")
        print(f"Total books in database: {book_count}")
        
        # List current books in directory
        books_dir = self.data_dir / "books"
        current_books = list(books_dir.glob("*.pdf"))
        
        print(f"Current books in directory: {len(current_books)}")
        
        if len(current_books) > book_count:
            print(f"⚠️  New books detected! ({len(current_books) - book_count} new)")
            print("Run book processor to add new books to the index")
        elif len(current_books) < book_count:
            print(f"⚠️  Some books may have been removed")
        else:
            print("✅ Book collection appears unchanged")
    
    def generate_update_report(self):
        """Generate a comprehensive update report."""
        if not self.update_info:
            return
            
        last_analysis = self.update_info['last_analysis_date']
        last_datetime = datetime.fromisoformat(last_analysis)
        time_since = datetime.now() - last_datetime
        
        print("\n" + "="*60)
        print("CONTENT UPDATE REPORT")
        print("="*60)
        print(f"\nLast analysis: {last_analysis[:10]} ({time_since.days} days ago)")
        
        # Summary of each source
        for source in ['forum', 'news', 'books']:
            info = self.update_info['sources'].get(source)
            if info:
                print(f"\n{source.upper()}:")
                print(f"  - Documents: {info['total_documents']:,}")
                if source == 'news':
                    print(f"  - Articles: {info['total_unique_articles']:,}")
                    print(f"  - Latest: {info['latest_content_date']}")
                elif source == 'books':
                    print(f"  - Books: {info['total_books']}")
                    print(f"  - Latest: {info['latest_book_year']}")
                elif source == 'forum':
                    print(f"  - Date range: {info['earliest_content_date']} to {info['latest_content_date']}")
    
    def create_update_scripts(self):
        """Create specific update scripts for each source."""
        scripts_dir = Path("src/update/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # News update script
        news_script = scripts_dir / "update_news.sh"
        with open(news_script, 'w') as f:
            f.write("""#!/bin/bash
# Update news articles

echo "Updating news articles..."
cd data/raw/news

# Download only new files (-N flag)
wget -r -l 1 -H -t 1 -nd -N -np -A '*.html' -erobots=off https://www.strunz.com/news/

# Count new files
NEW_FILES=$(find . -name "*.html" -mtime -1 | wc -l)
echo "Downloaded $NEW_FILES new articles"

if [ $NEW_FILES -gt 0 ]; then
    echo "Processing new articles..."
    cd ../../..
    source venv/bin/activate
    python src/rag/news_processor_batch.py
fi
""")
        news_script.chmod(0o755)
        
        # Book update script
        book_script = scripts_dir / "update_books.sh"
        with open(book_script, 'w') as f:
            f.write("""#!/bin/bash
# Update books

echo "Checking for new books..."
cd data/books

# Count PDF files
BOOK_COUNT=$(ls -1 *.pdf 2>/dev/null | wc -l)
echo "Found $BOOK_COUNT books"

# Run book processor
cd ../..
source venv/bin/activate
python src/rag/book_processor_simple.py
""")
        book_script.chmod(0o755)
        
        print(f"\n✅ Update scripts created in {scripts_dir}")
        print("  - update_news.sh: Download and process new news articles")
        print("  - update_books.sh: Process any new books added to data/books/")

def main():
    updater = ContentUpdater()
    
    if not updater.update_info:
        print("❌ No update information found. Please run content_date_analyzer.py first.")
        return
    
    # Generate report and check for updates
    updater.generate_update_report()
    updater.check_news_updates()
    updater.check_forum_updates()
    updater.check_book_updates()
    
    # Create update scripts
    updater.create_update_scripts()
    
    print("\n✅ Update check complete!")
    print("\nTo update content:")
    print("  1. For news: ./src/update/scripts/update_news.sh")
    print("  2. For books: Add new PDFs to data/books/, then run ./src/update/scripts/update_books.sh")
    print("  3. After updates, run content_date_analyzer.py again to update markers")

if __name__ == "__main__":
    main()