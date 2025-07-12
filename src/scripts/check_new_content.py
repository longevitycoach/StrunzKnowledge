#!/usr/bin/env python3
"""
Check for new content that requires index updates
"""

import requests
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentChecker:
    def __init__(self):
        self.data_dir = Path("data")
        self.news_dir = self.data_dir / "raw" / "news"
        self.last_check_file = self.data_dir / "last_check.json"
        
    def load_last_check(self):
        """Load the timestamp of the last check."""
        if self.last_check_file.exists():
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_check', '2024-01-01'))
        return datetime.now() - timedelta(days=7)  # Default to 1 week ago
    
    def save_last_check(self):
        """Save the current timestamp."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.last_check_file, 'w') as f:
            json.dump({
                'last_check': datetime.now().isoformat(),
                'check_type': 'automated'
            }, f, indent=2)
    
    def check_news_website(self):
        """Check Dr. Strunz news website for new articles."""
        try:
            # Get the news index page
            response = requests.get("https://www.strunz.com/news/", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links (adjust selector based on actual website structure)
            article_links = soup.find_all('a', href=True)
            news_links = [
                link['href'] for link in article_links 
                if '/news/' in link['href'] and link['href'].endswith('.html')
            ]
            
            logger.info(f"Found {len(news_links)} news links on index page")
            
            # Check if we have any new articles
            existing_files = set()
            if self.news_dir.exists():
                existing_files = {f.name for f in self.news_dir.glob("*.html")}
            
            new_articles = []
            for link in news_links[:20]:  # Check last 20 articles
                filename = Path(link).name
                if filename not in existing_files:
                    new_articles.append(link)
            
            logger.info(f"Found {len(new_articles)} new articles")
            return len(new_articles) > 0
            
        except Exception as e:
            logger.error(f"Error checking news website: {e}")
            return False
    
    def check_local_changes(self):
        """Check for local file changes since last check."""
        last_check = self.load_last_check()
        
        # Check if any files were modified since last check
        for data_path in [self.data_dir / "raw", self.data_dir / "books"]:
            if not data_path.exists():
                continue
                
            for file_path in data_path.rglob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime > last_check:
                        logger.info(f"Found modified file: {file_path}")
                        return True
        
        return False
    
    def needs_update(self):
        """Determine if indices need updating."""
        has_new_content = False
        
        # Check for new web content
        if self.check_news_website():
            logger.info("New content found on website")
            has_new_content = True
        
        # Check for local changes
        if self.check_local_changes():
            logger.info("Local file changes detected")
            has_new_content = True
        
        # Force update if it's been more than 7 days
        last_check = self.load_last_check()
        if datetime.now() - last_check > timedelta(days=7):
            logger.info("Forcing update - more than 7 days since last check")
            has_new_content = True
        
        return has_new_content

def main():
    checker = ContentChecker()
    
    if checker.needs_update():
        logger.info("Update needed - creating flag file")
        # Create a flag file to indicate updates are needed
        with open(".needs_update", "w") as f:
            f.write(datetime.now().isoformat())
        
        # Update the last check timestamp
        checker.save_last_check()
        exit(0)  # Success - updates needed
    else:
        logger.info("No updates needed")
        # Remove flag file if it exists
        if os.path.exists(".needs_update"):
            os.remove(".needs_update")
        exit(0)  # Success - no updates needed

if __name__ == "__main__":
    main()