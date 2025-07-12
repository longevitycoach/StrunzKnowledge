#!/usr/bin/env python3
"""
Fixed News Downloader - Handles redirects and actual URL structure
"""

import subprocess
import time
from pathlib import Path
import logging
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_fixed_download.log'),
        logging.StreamHandler()
    ]
)

def extract_article_urls():
    """Extract all article URLs from archive pages"""
    
    logging.info("Extracting article URLs from archive pages...")
    
    all_urls = set()
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for page in range(140):
        # Note: The URL uses .html extension
        if page == 0:
            url = "https://www.strunz.com/news/archiv.html?limit=50"
        else:
            url = f"https://www.strunz.com/news/archiv.html?limit=50&p={page}"
        
        try:
            logging.info(f"Fetching archive page {page + 1}/140")
            response = session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all news article links
                # Looking for links that point to /news/[article-name].html
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Match pattern: /news/some-article-name.html
                    if re.match(r'^/news/[a-z0-9-]+\.html$', href):
                        full_url = f"https://www.strunz.com{href}"
                        all_urls.add(full_url)
                
                # Also check for full URLs
                for link in soup.find_all('a', href=re.compile(r'https://www\.strunz\.com/news/[a-z0-9-]+\.html')):
                    all_urls.add(link['href'])
                
            else:
                logging.warning(f"Failed to fetch page {page + 1}: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error fetching page {page + 1}: {e}")
        
        time.sleep(0.5)  # Be nice to the server
    
    logging.info(f"Found {len(all_urls)} unique article URLs")
    return all_urls

def download_articles(urls):
    """Download individual articles"""
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = 0
    failed = []
    
    for i, url in enumerate(sorted(urls), 1):
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        if output_file.exists() and output_file.stat().st_size > 0:
            logging.debug(f"Skipping existing: {filename}")
            downloaded += 1
            continue
        
        try:
            cmd = [
                "wget",
                "-O", str(output_file),
                "--user-agent=Mozilla/5.0",
                "--timeout=30",
                "--tries=3",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
                downloaded += 1
                if downloaded % 100 == 0:
                    logging.info(f"Progress: {downloaded}/{len(urls)} articles downloaded")
            else:
                failed.append(url)
                if output_file.exists() and output_file.stat().st_size == 0:
                    output_file.unlink()  # Remove empty files
                    
        except Exception as e:
            logging.error(f"Error downloading {url}: {e}")
            failed.append(url)
        
        if i % 10 == 0:
            time.sleep(1)  # Longer pause every 10 downloads
        else:
            time.sleep(0.2)
    
    logging.info(f"Downloaded {downloaded} articles successfully")
    if failed:
        logging.warning(f"Failed to download {len(failed)} articles")
    
    return downloaded, failed

def main():
    """Main download process"""
    
    logging.info("=== Fixed News Downloader ===")
    
    # First, extract all article URLs
    article_urls = extract_article_urls()
    
    if not article_urls:
        logging.error("No article URLs found!")
        logging.info("Trying direct recursive download instead...")
        
        # Fallback: Try direct recursive download
        cmd = [
            "wget",
            "--recursive",
            "--level=4",
            "--no-clobber",
            "--page-requisites",
            "--html-extension",
            "--convert-links",
            "--restrict-file-names=windows",
            "--domains=www.strunz.com",
            "--directory-prefix=data/raw",
            "--no-host-directories",
            "--accept=*.html",
            "--reject=*.jpg,*.jpeg,*.png,*.gif,*.pdf,*.css,*.js,*.ico",
            "--reject-regex=.*(shop|product|catalog|cart|customer|account|login|register|static|media|pub).*",
            "--user-agent=Mozilla/5.0",
            "--wait=0.5",
            "--random-wait",
            "https://www.strunz.com/news.html",
            "https://www.strunz.com/news/archiv.html"
        ]
        
        logging.info("Running recursive wget...")
        subprocess.run(cmd)
        
    else:
        # Download all found articles
        downloaded, failed = download_articles(article_urls)
        
        # Retry failed downloads once
        if failed:
            logging.info(f"Retrying {len(failed)} failed downloads...")
            retry_downloaded, still_failed = download_articles(failed)
            downloaded += retry_downloaded
            
            if still_failed:
                logging.error(f"Still failed after retry: {len(still_failed)} articles")
    
    # Final count
    news_files = list(Path("data/raw/news").glob("*.html"))
    article_files = [f for f in news_files if "archiv" not in f.name]
    
    logging.info("\n=== Final Statistics ===")
    logging.info(f"Total news files: {len(news_files)}")
    logging.info(f"Article files: {len(article_files)}")
    logging.info(f"Expected: ~7,000 articles")
    
    if len(article_files) < 1000:
        print(f"\n⚠️  Only {len(article_files)} articles downloaded")
        print("\nPossible issues:")
        print("1. The site may require authentication for full access")
        print("2. Archive pages may be dynamically loaded with JavaScript")
        print("3. Anti-bot protection may be blocking automated downloads")
        print("\nYou may need to:")
        print("- Use a browser automation tool like Selenium")
        print("- Manually download with browser developer tools")
        print("- Contact the site owner for API access")
    else:
        print(f"\n✅ Successfully downloaded {len(article_files)} news articles!")

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    main()