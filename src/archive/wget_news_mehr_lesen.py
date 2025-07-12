#!/usr/bin/env python3
"""
News Downloader using MEHR LESEN links from archive pages
Goes through pages p=0 to p=140 and follows all "MEHR LESEN" links
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
        logging.FileHandler('logs/news_mehr_lesen.log'),
        logging.StreamHandler()
    ]
)

def get_article_urls_from_archive_page(page_num):
    """Extract article URLs from a single archive page by finding MEHR LESEN links"""
    
    if page_num == 0:
        url = "https://www.strunz.com/news/archiv.html?limit=50"
    else:
        url = f"https://www.strunz.com/news/archiv.html?limit=50&p={page_num}"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    article_urls = []
    
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all "MEHR LESEN" links
            # These are typically in <a> tags with text "MEHR LESEN" or similar
            mehr_lesen_links = []
            
            # Method 1: Find by link text
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).upper()
                if 'MEHR LESEN' in link_text or 'WEITERLESEN' in link_text or 'MORE' in link_text:
                    href = link['href']
                    if href.startswith('/'):
                        full_url = f"https://www.strunz.com{href}"
                    else:
                        full_url = href
                    mehr_lesen_links.append(full_url)
            
            # Method 2: Find article containers and get their main link
            # Often articles are in divs with class like 'article', 'post', 'entry', etc.
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['article', 'post', 'entry', 'item', 'teaser'])):
                # Find the main link in this article (usually the title or "mehr lesen")
                links = article.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/news/' in href and href.endswith('.html') and 'archiv' not in href:
                        if href.startswith('/'):
                            full_url = f"https://www.strunz.com{href}"
                        else:
                            full_url = href
                        article_urls.append(full_url)
            
            # Combine and deduplicate
            all_urls = list(set(mehr_lesen_links + article_urls))
            
            # Filter to only keep news articles
            article_urls = [url for url in all_urls if '/news/' in url and url.endswith('.html') and 'archiv' not in url]
            
            logging.info(f"Page {page_num}: Found {len(article_urls)} article URLs")
            
            return article_urls
            
        else:
            logging.error(f"Failed to fetch page {page_num}: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error on page {page_num}: {e}")
        return []

def download_all_articles():
    """Go through all archive pages and download articles"""
    
    all_article_urls = set()
    
    # Process pages 0 to 140
    for page_num in range(141):  # 0 to 140
        logging.info(f"\nProcessing archive page {page_num}/140")
        
        article_urls = get_article_urls_from_archive_page(page_num)
        all_article_urls.update(article_urls)
        
        # Progress update
        if (page_num + 1) % 10 == 0:
            logging.info(f"Progress: {page_num + 1}/141 pages processed, {len(all_article_urls)} unique articles found")
        
        # Be nice to the server
        time.sleep(0.5)
    
    logging.info(f"\nTotal unique articles found: {len(all_article_urls)}")
    
    # Save URLs for reference
    if all_article_urls:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        with open("data/raw/news_article_urls.json", "w") as f:
            json.dump(sorted(list(all_article_urls)), f, indent=2)
        logging.info(f"Saved {len(all_article_urls)} URLs to data/raw/news_article_urls.json")
    
    # Download the articles
    download_articles_from_urls(all_article_urls)

def download_articles_from_urls(urls):
    """Download articles from a set of URLs"""
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    failed = []
    
    total = len(urls)
    
    for i, url in enumerate(sorted(urls), 1):
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        # Skip if already exists and has content
        if output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
            continue
        
        # Download with wget
        cmd = [
            "wget",
            "-O", str(output_file),
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "--timeout=30",
            "--tries=2",
            "-q",  # Quiet
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
            if downloaded % 50 == 0:
                logging.info(f"Downloaded {downloaded}/{total} articles...")
        else:
            failed.append(url)
            if output_file.exists():
                output_file.unlink()  # Remove empty files
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
        else:
            time.sleep(0.2)
    
    logging.info(f"\nDownload complete!")
    logging.info(f"Successfully downloaded: {downloaded} articles")
    logging.info(f"Failed: {len(failed)} articles")
    
    if failed:
        with open("data/raw/failed_urls.json", "w") as f:
            json.dump(failed, f, indent=2)
        logging.info("Failed URLs saved to data/raw/failed_urls.json")
    
    return downloaded

def check_archive_page_structure():
    """Check the structure of an archive page to understand the HTML"""
    
    logging.info("Checking archive page structure...")
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    # Check page 0
    url = "https://www.strunz.com/news/archiv.html?limit=50"
    
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save for inspection
            with open("data/raw/sample_archive_page.html", "w", encoding='utf-8') as f:
                f.write(response.text)
            
            # Look for "MEHR LESEN" or similar
            mehr_lesen_count = 0
            for link in soup.find_all('a', href=True):
                text = link.get_text(strip=True)
                if 'MEHR' in text.upper() or 'LESEN' in text.upper():
                    mehr_lesen_count += 1
                    logging.info(f"Found MEHR LESEN link: {text} -> {link.get('href', '')}")
            
            logging.info(f"Found {mehr_lesen_count} MEHR LESEN links")
            
            # Also check for any news article links
            news_links = [a['href'] for a in soup.find_all('a', href=True) if '/news/' in a.get('href', '') and a['href'].endswith('.html')]
            logging.info(f"Found {len(news_links)} news article links total")
            
            if news_links:
                logging.info("Sample article links:")
                for link in news_links[:5]:
                    logging.info(f"  {link}")
                    
    except Exception as e:
        logging.error(f"Error checking structure: {e}")

def main():
    """Main function"""
    
    logging.info("=== News Downloader via MEHR LESEN ===")
    logging.info("This will go through archive pages p=0 to p=140")
    logging.info("and download all articles linked with 'MEHR LESEN'\n")
    
    # First check the structure
    check_archive_page_structure()
    
    print("\nReady to download articles from all 141 archive pages.")
    response = input("Continue? (y/n): ")
    
    if response.lower() == 'y':
        download_all_articles()
        
        # Final count
        news_files = list(Path("data/raw/news").glob("*.html"))
        article_files = [f for f in news_files if "archiv" not in f.name]
        
        print(f"\n{'✅' if len(article_files) > 1000 else '⚠️ '} Downloaded {len(article_files)} news articles")
        
        if len(article_files) > 0:
            print("\nSample articles:")
            for f in sorted(article_files)[:5]:
                print(f"  - {f.name}")
            if len(article_files) > 5:
                print(f"  ... and {len(article_files) - 5} more")

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    Path("data/raw").mkdir(exist_ok=True)
    main()