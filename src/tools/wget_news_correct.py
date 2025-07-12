#!/usr/bin/env python3
"""
Correct News Downloader - Downloads from news.html?limit=50&p=0 to p=140
"""

import requests
from bs4 import BeautifulSoup
import subprocess
import time
from pathlib import Path
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_correct.log'),
        logging.StreamHandler()
    ]
)

def get_article_urls_from_news_page(page_num):
    """Extract article URLs from a news page"""
    
    if page_num == 0:
        url = "https://www.strunz.com/news.html?limit=50"
    else:
        url = f"https://www.strunz.com/news.html?limit=50&p={page_num}"
    
    logging.info(f"Fetching: {url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    article_urls = []
    
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links to individual news articles
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Look for links to individual news articles
                if '/news/' in href and href.endswith('.html') and 'limit=' not in href and 'p=' not in href:
                    if href.startswith('/'):
                        full_url = f"https://www.strunz.com{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Avoid duplicates and pagination links
                    if 'news.html' not in full_url.split('/')[-1]:
                        article_urls.append(full_url)
            
            # Deduplicate
            article_urls = list(set(article_urls))
            
            logging.info(f"Page {page_num}: Found {len(article_urls)} articles")
            
            # Look for "MEHR LESEN" links specifically
            mehr_lesen_count = 0
            for link in soup.find_all('a'):
                text = link.get_text(strip=True)
                if 'MEHR LESEN' in text.upper():
                    mehr_lesen_count += 1
            
            if mehr_lesen_count > 0:
                logging.info(f"  Found {mehr_lesen_count} 'MEHR LESEN' links")
            
            return article_urls
            
        else:
            logging.error(f"Failed to fetch page {page_num}: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error on page {page_num}: {e}")
        return []

def download_all_news_articles():
    """Download articles from all news pages (p=0 to p=140)"""
    
    all_article_urls = set()
    
    # Process pages 0 to 140
    logging.info("Processing news pages from p=0 to p=140...")
    
    for page_num in range(141):  # 0 to 140
        article_urls = get_article_urls_from_news_page(page_num)
        all_article_urls.update(article_urls)
        
        # Progress update
        if (page_num + 1) % 10 == 0:
            logging.info(f"Progress: {page_num + 1}/141 pages, {len(all_article_urls)} unique articles found")
        
        # Be nice to server
        time.sleep(0.5)
    
    logging.info(f"\nTotal unique articles found: {len(all_article_urls)}")
    
    # Save URLs
    if all_article_urls:
        urls_file = Path("data/raw/all_news_urls.json")
        urls_file.parent.mkdir(parents=True, exist_ok=True)
        with open(urls_file, "w") as f:
            json.dump(sorted(list(all_article_urls)), f, indent=2)
        logging.info(f"Saved URLs to {urls_file}")
    
    # Download the articles
    download_articles(all_article_urls)

def download_articles(urls):
    """Download individual articles"""
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    failed = []
    total = len(urls)
    
    logging.info(f"\nDownloading {total} articles...")
    
    for i, url in enumerate(sorted(urls), 1):
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        # Skip existing files
        if output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
            continue
        
        # Download
        cmd = [
            "wget",
            "-O", str(output_file),
            "--user-agent=Mozilla/5.0",
            "--timeout=30",
            "--tries=2",
            "-q",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
            if downloaded % 100 == 0:
                logging.info(f"Downloaded {downloaded}/{total} articles...")
            elif downloaded % 10 == 0:
                print(f"\rDownloaded {downloaded}/{total} articles...", end='', flush=True)
        else:
            failed.append(url)
            if output_file.exists():
                output_file.unlink()
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
        else:
            time.sleep(0.2)
    
    print()  # New line after progress
    
    logging.info(f"\nDownload complete!")
    logging.info(f"Downloaded: {downloaded} articles")
    logging.info(f"Failed: {len(failed)} articles")
    
    if failed:
        with open("data/raw/failed_news_urls.json", "w") as f:
            json.dump(failed, f, indent=2)

def quick_test():
    """Quick test with page 140"""
    
    logging.info("Quick test with page 140...")
    
    # Test page 140 (oldest articles from 2006)
    urls = get_article_urls_from_news_page(140)
    
    if urls:
        logging.info(f"\nFound {len(urls)} articles on page 140")
        logging.info("Sample URLs:")
        for url in urls[:5]:
            logging.info(f"  {url}")
        
        # Download a few to test
        logging.info("\nDownloading first 3 articles as test...")
        news_dir = Path("data/raw/news")
        news_dir.mkdir(parents=True, exist_ok=True)
        
        for url in urls[:3]:
            filename = url.split('/')[-1]
            output_file = news_dir / filename
            
            cmd = ["wget", "-O", str(output_file), "--user-agent=Mozilla/5.0", "-q", url]
            result = subprocess.run(cmd)
            
            if output_file.exists() and output_file.stat().st_size > 1000:
                logging.info(f"  ✓ {filename} ({output_file.stat().st_size} bytes)")
            else:
                logging.info(f"  ✗ {filename}")
        
        return True
    else:
        logging.error("No articles found on page 140!")
        return False

def main():
    """Main function"""
    
    print("=== Correct News Downloader ===")
    print("Downloads from: https://www.strunz.com/news.html?limit=50&p=0 to p=140")
    print()
    
    # Run quick test first
    if quick_test():
        print("\nTest successful! Ready to download all articles.")
        response = input("Download all articles from pages 0-140? (y/n): ")
        
        if response.lower() == 'y':
            download_all_news_articles()
            
            # Final count
            news_files = list(Path("data/raw/news").glob("*.html"))
            print(f"\n✅ Downloaded {len(news_files)} news articles total")
    else:
        print("\nTest failed. Please check the URL structure.")

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    main()