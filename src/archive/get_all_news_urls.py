#!/usr/bin/env python3
"""
Extract ALL news article URLs from archive pages
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from pathlib import Path
import json
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_all_article_urls():
    """Extract all article URLs from all 140 archive pages"""
    
    all_urls = set()
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Process each archive page
    for page in range(140):
        if page == 0:
            url = "https://www.strunz.com/news/archiv.html?limit=50"
        else:
            url = f"https://www.strunz.com/news/archiv.html?limit=50&p={page}"
        
        try:
            logging.info(f"Fetching archive page {page + 1}/140: {url}")
            response = session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links - try different patterns
                page_urls = set()
                
                # Pattern 1: Direct href to /news/article.html
                for link in soup.find_all('a', href=re.compile(r'/news/[^/]+\.html$')):
                    href = link.get('href', '')
                    if '/archiv' not in href:
                        full_url = f"https://www.strunz.com{href}" if href.startswith('/') else href
                        page_urls.add(full_url)
                
                # Pattern 2: Look for article containers (common patterns)
                for article in soup.find_all(['article', 'div'], class_=re.compile('(post|article|entry|news|item)')):
                    links = article.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if '/news/' in href and href.endswith('.html') and '/archiv' not in href:
                            full_url = f"https://www.strunz.com{href}" if href.startswith('/') else href
                            page_urls.add(full_url)
                
                # Pattern 3: Look for h2, h3, h4 with links (common for article titles)
                for heading in soup.find_all(['h2', 'h3', 'h4']):
                    link = heading.find('a', href=True)
                    if link:
                        href = link['href']
                        if '/news/' in href and href.endswith('.html') and '/archiv' not in href:
                            full_url = f"https://www.strunz.com{href}" if href.startswith('/') else href
                            page_urls.add(full_url)
                
                # Pattern 4: Any link with news in it
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    # Match: /news/some-article.html but not /news/archiv
                    if re.match(r'.*/news/[a-z0-9-]+\.html$', href) and '/archiv' not in href:
                        full_url = f"https://www.strunz.com{href}" if href.startswith('/') else href
                        page_urls.add(full_url)
                
                logging.info(f"  Found {len(page_urls)} articles on page {page + 1}")
                all_urls.update(page_urls)
                
                # If we're not finding articles, print some diagnostic info
                if len(page_urls) == 0 and page < 5:
                    logging.warning(f"No articles found on page {page + 1}. Sample HTML:")
                    # Find any links with 'news' in them
                    news_links = [link.get('href', '') for link in soup.find_all('a', href=True) if 'news' in link.get('href', '')][:5]
                    for link in news_links:
                        logging.warning(f"  Sample link: {link}")
                
            else:
                logging.error(f"Failed to fetch page {page + 1}: HTTP {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error on page {page + 1}: {e}")
        
        time.sleep(0.5)  # Be respectful
        
        # Progress update
        if (page + 1) % 10 == 0:
            logging.info(f"Progress: {page + 1}/140 pages processed, {len(all_urls)} unique articles found so far")
    
    # Save URLs to file
    if all_urls:
        output_file = Path("data/raw/news_urls.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        urls_list = sorted(list(all_urls))
        with open(output_file, 'w') as f:
            json.dump(urls_list, f, indent=2)
        
        logging.info(f"\nSaved {len(urls_list)} URLs to {output_file}")
        
        # Show some examples
        logging.info("\nSample URLs:")
        for url in urls_list[:5]:
            logging.info(f"  {url}")
        if len(urls_list) > 5:
            logging.info(f"  ... and {len(urls_list) - 5} more")
    
    return all_urls

def download_from_url_list(urls):
    """Download articles from a list of URLs"""
    
    import subprocess
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    failed = []
    
    for i, url in enumerate(sorted(urls), 1):
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        # Skip if already exists
        if output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
            continue
        
        cmd = [
            "wget",
            "-O", str(output_file),
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "--timeout=30",
            "--tries=2",
            "-q",  # Quiet mode
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 1000:
            downloaded += 1
        else:
            failed.append(url)
            if output_file.exists():
                output_file.unlink()  # Remove empty/failed files
        
        # Progress
        if i % 100 == 0:
            logging.info(f"Downloaded {downloaded}/{i} articles ({len(failed)} failed)")
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
        else:
            time.sleep(0.1)
    
    logging.info(f"\nDownload complete: {downloaded} successful, {len(failed)} failed")
    
    return downloaded, failed

def main():
    """Main process"""
    
    logging.info("=== News URL Extractor ===")
    
    # First, try to load existing URLs
    url_file = Path("data/raw/news_urls.json")
    
    if url_file.exists():
        logging.info(f"Loading existing URLs from {url_file}")
        with open(url_file) as f:
            urls = set(json.load(f))
        logging.info(f"Loaded {len(urls)} URLs")
    else:
        # Extract all URLs
        urls = get_all_article_urls()
    
    if not urls:
        logging.error("No URLs found! The archive structure might have changed.")
        
        # Let's check what's actually on the page
        logging.info("\nDiagnostic check - fetching page 0 to see structure...")
        
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        try:
            response = session.get("https://www.strunz.com/news/archiv.html?limit=50", timeout=30)
            if response.status_code == 200:
                # Save the page for manual inspection
                with open("data/raw/archive_page_0.html", "w", encoding='utf-8') as f:
                    f.write(response.text)
                logging.info("Saved archive page 0 to data/raw/archive_page_0.html for inspection")
                
                # Try to find ANY links
                soup = BeautifulSoup(response.text, 'html.parser')
                all_links = soup.find_all('a', href=True)
                news_links = [l['href'] for l in all_links if 'news' in l.get('href', '')]
                
                logging.info(f"\nFound {len(all_links)} total links, {len(news_links)} with 'news' in URL")
                logging.info("First 10 news-related links:")
                for link in news_links[:10]:
                    logging.info(f"  {link}")
                    
        except Exception as e:
            logging.error(f"Diagnostic failed: {e}")
    
    else:
        # Download all articles
        logging.info(f"\nReady to download {len(urls)} articles")
        response = input("Proceed with download? (y/n): ")
        
        if response.lower() == 'y':
            downloaded, failed = download_from_url_list(urls)
            
            # Save failed URLs for retry
            if failed:
                with open("data/raw/failed_news_urls.json", "w") as f:
                    json.dump(failed, f, indent=2)
                logging.info(f"Saved {len(failed)} failed URLs for retry")

if __name__ == "__main__":
    main()