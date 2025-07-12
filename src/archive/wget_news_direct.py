#!/usr/bin/env python3
"""
Direct News Downloader - Downloads articles directly from their URLs
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
        logging.FileHandler('logs/news_direct_download.log'),
        logging.StreamHandler()
    ]
)

def get_article_urls_from_archive():
    """Get article URLs by parsing the archive pages"""
    
    logging.info("Fetching article URLs from archive pages...")
    
    all_urls = set()
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    # First, let's check one archive page to see its structure
    test_url = "https://www.strunz.com/news/archiv.html?limit=50&p=140"
    
    try:
        response = session.get(test_url, timeout=30)
        if response.status_code == 200:
            logging.info(f"Successfully fetched archive page 140")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links to news articles
            article_count = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Look for news article pattern
                if '/news/' in href and href.endswith('.html') and 'archiv' not in href:
                    if href.startswith('/'):
                        full_url = f"https://www.strunz.com{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    all_urls.add(full_url)
                    article_count += 1
            
            logging.info(f"Found {article_count} articles on page 140")
            
            # If successful, continue with all pages
            if article_count > 0:
                for page in range(140):  # Pages 0-139
                    if page == 0:
                        url = "https://www.strunz.com/news/archiv.html?limit=50"
                    else:
                        url = f"https://www.strunz.com/news/archiv.html?limit=50&p={page}"
                    
                    try:
                        response = session.get(url, timeout=30)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                if '/news/' in href and href.endswith('.html') and 'archiv' not in href:
                                    if href.startswith('/'):
                                        full_url = f"https://www.strunz.com{href}"
                                    elif href.startswith('http'):
                                        full_url = href
                                    else:
                                        continue
                                    
                                    all_urls.add(full_url)
                            
                            if (page + 1) % 10 == 0:
                                logging.info(f"Processed {page + 1}/140 archive pages, found {len(all_urls)} unique articles so far")
                                
                    except Exception as e:
                        logging.warning(f"Error on page {page}: {e}")
                    
                    time.sleep(0.3)  # Be nice to server
                    
    except Exception as e:
        logging.error(f"Error fetching test page: {e}")
    
    return all_urls

def download_news_recursive():
    """Use wget to recursively download all news articles"""
    
    logging.info("Starting recursive news download...")
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    # Since we know the articles exist and have a consistent pattern,
    # let's use wget to recursively download from the news section
    cmd = [
        "wget",
        "--recursive",
        "--level=5",
        "--no-clobber",
        "--html-extension",
        "--convert-links",
        "--domains=www.strunz.com",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--accept-regex=/news/[a-z0-9-]+\\.html$",  # Only news articles
        "--reject-regex=.*(archiv|shop|product|catalog|cart|login|static|media).*",
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.pdf,*.css,*.js,*.ico,*.mp3,*.mp4",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "--wait=0.3",
        "--random-wait",
        "--timeout=30",
        "--tries=3",
        "--limit-rate=500k",  # Limit bandwidth
        "https://www.strunz.com/news/"
    ]
    
    # Also add specific archive pages to ensure we get all articles
    for i in range(0, 141, 10):  # Every 10th page
        if i == 0:
            cmd.append("https://www.strunz.com/news/archiv.html?limit=50")
        else:
            cmd.append(f"https://www.strunz.com/news/archiv.html?limit=50&p={i}")
    
    logging.info("Running wget with improved parameters...")
    logging.info("This will take a while - downloading ~7,000 articles")
    
    try:
        # Run wget with output monitoring
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        articles_downloaded = 0
        for line in process.stdout:
            if "Saving to:" in line and "/news/" in line and "archiv" not in line:
                articles_downloaded += 1
                if articles_downloaded % 100 == 0:
                    logging.info(f"Downloaded {articles_downloaded} articles...")
        
        process.wait()
        
        if process.returncode == 0 or process.returncode == 8:
            logging.info("Wget completed successfully")
        else:
            logging.warning(f"Wget finished with code {process.returncode}")
            
    except KeyboardInterrupt:
        logging.info("Download interrupted by user")
        process.terminate()
        process.wait()
    except Exception as e:
        logging.error(f"Error during download: {e}")

def download_sample_articles():
    """Download the sample articles you provided to test"""
    
    logging.info("Testing with sample articles...")
    
    sample_urls = [
        "https://www.strunz.com/news/jod-fuer-schlankhormone.html",
        "https://www.strunz.com/news/die-empfindliche-folsaeure.html",
        "https://www.strunz.com/news/eiweiss-und-immunsystem.html",
        "https://www.strunz.com/news/wie-kann-ich-mit-dem-laufen-abnehmen.html",
        "https://www.strunz.com/news/anti-aging-und-forever-young.html"
    ]
    
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    for url in sample_urls:
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        cmd = ["wget", "-O", str(output_file), "--user-agent=Mozilla/5.0", url]
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
            success += 1
            logging.info(f"✓ Downloaded: {filename}")
        else:
            logging.error(f"✗ Failed: {filename}")
    
    logging.info(f"Sample test: {success}/5 articles downloaded successfully")
    return success == 5

def main():
    """Main download process"""
    
    logging.info("=== Direct News Downloader ===")
    
    # First test with sample articles
    if download_sample_articles():
        logging.info("Sample download successful! Proceeding with full download...")
        
        # Try to get URLs from archive pages
        article_urls = get_article_urls_from_archive()
        
        if article_urls:
            logging.info(f"Found {len(article_urls)} article URLs to download")
            # Download them individually if needed
        
        # Use recursive wget for comprehensive download
        download_news_recursive()
        
    else:
        logging.error("Sample download failed. The site may be blocking automated access.")
    
    # Count final results
    news_files = list(Path("data/raw/news").rglob("*.html"))
    article_files = [f for f in news_files if "archiv" not in f.name.lower()]
    
    logging.info("\n=== Final Statistics ===")
    logging.info(f"Total HTML files: {len(news_files)}")
    logging.info(f"News articles: {len(article_files)}")
    
    # Show some downloaded articles
    if article_files:
        logging.info("\nSample of downloaded articles:")
        for f in sorted(article_files)[:10]:
            logging.info(f"  - {f.name}")
        if len(article_files) > 10:
            logging.info(f"  ... and {len(article_files) - 10} more")
    
    print(f"\n{'✅' if len(article_files) > 1000 else '⚠️'}  Downloaded {len(article_files)} news articles")

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    main()