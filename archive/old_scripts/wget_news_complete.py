#!/usr/bin/env python3
"""
Complete News Downloader - Downloads all news articles with proper pagination
Gets all 140 pages with limit=50 (approximately 7,000 articles)
"""

import subprocess
import time
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_complete_download.log'),
        logging.StreamHandler()
    ]
)

def download_news_archives():
    """Download all news archive pages with limit=50"""
    
    # Create news directory if it doesn't exist
    news_dir = Path("data/raw/news")
    news_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info("Starting complete news download with limit=50")
    logging.info("Expected: 140 pages × 50 articles = ~7,000 articles")
    
    # Base wget command
    base_cmd = [
        "wget",
        "--recursive",
        "--level=2",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--page-requisites",
        "--html-extension", 
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "--wait=1",
        "--random-wait",
        "--tries=3",
        "--timeout=30"
    ]
    
    # First, download the main news page
    logging.info("Downloading main news page...")
    main_cmd = base_cmd + ["https://www.strunz.com/news"]
    subprocess.run(main_cmd, capture_output=True)
    
    # Download archive pages with pagination
    successful_pages = 0
    failed_pages = []
    
    for page in range(140):  # Pages 0-139
        url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        logging.info(f"Downloading archive page {page + 1}/140: {url}")
        
        cmd = base_cmd + [
            "--accept-regex=.*/news/.*",
            "--reject-regex=.*\\.(jpg|jpeg|png|gif|ico|css|js|pdf|zip|exe).*",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                successful_pages += 1
                logging.info(f"  ✓ Page {page + 1} downloaded successfully")
            else:
                failed_pages.append(page)
                logging.warning(f"  ✗ Page {page + 1} failed with code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            failed_pages.append(page)
            logging.error(f"  ✗ Page {page + 1} timed out")
        except Exception as e:
            failed_pages.append(page)
            logging.error(f"  ✗ Page {page + 1} error: {e}")
        
        # Progress update every 10 pages
        if (page + 1) % 10 == 0:
            logging.info(f"Progress: {page + 1}/140 pages processed ({successful_pages} successful)")
        
        # Small delay between pages
        time.sleep(0.5)
    
    # Summary
    logging.info("\n" + "="*50)
    logging.info("DOWNLOAD SUMMARY")
    logging.info("="*50)
    logging.info(f"Total pages attempted: 140")
    logging.info(f"Successful downloads: {successful_pages}")
    logging.info(f"Failed downloads: {len(failed_pages)}")
    
    if failed_pages:
        logging.warning(f"Failed pages: {failed_pages}")
    
    # Count downloaded files
    if Path("data/raw/news").exists():
        news_files = list(Path("data/raw/news").rglob("*.html"))
        logging.info(f"\nTotal HTML files downloaded: {len(news_files)}")
        
        # Show sample files
        if news_files:
            logging.info("\nSample of downloaded files:")
            for file in sorted(news_files)[:5]:
                logging.info(f"  - {file.name}")
            if len(news_files) > 5:
                logging.info(f"  ... and {len(news_files) - 5} more files")

def retry_failed_pages(failed_pages):
    """Retry downloading failed pages"""
    if not failed_pages:
        return
    
    logging.info(f"\nRetrying {len(failed_pages)} failed pages...")
    
    base_cmd = [
        "wget",
        "--recursive",
        "--level=2",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--page-requisites",
        "--html-extension",
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--user-agent=Mozilla/5.0",
        "--wait=2",
        "--random-wait",
        "--tries=5",
        "--timeout=60"
    ]
    
    retry_success = 0
    for page in failed_pages:
        url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        logging.info(f"Retrying page {page + 1}...")
        
        cmd = base_cmd + [url]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode == 0:
                retry_success += 1
                logging.info(f"  ✓ Page {page + 1} downloaded on retry")
            else:
                logging.warning(f"  ✗ Page {page + 1} failed again")
        except:
            logging.error(f"  ✗ Page {page + 1} retry failed")
    
    logging.info(f"Retry complete: {retry_success}/{len(failed_pages)} successful")

def main():
    """Main function"""
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    logging.info("=== Complete News Download ===")
    logging.info("Downloading ~7,000 news articles from strunz.com")
    logging.info("Using: limit=50, pages 0-139")
    
    start_time = time.time()
    
    # Run the download
    download_news_archives()
    
    # Calculate duration
    duration = time.time() - start_time
    logging.info(f"\nTotal download time: {duration/60:.1f} minutes")
    
    # Final file count
    if Path("data/raw/news").exists():
        all_files = list(Path("data/raw/news").rglob("*.html"))
        archive_files = [f for f in all_files if "archiv" in str(f)]
        article_files = [f for f in all_files if "archiv" not in str(f)]
        
        logging.info("\n=== FINAL STATISTICS ===")
        logging.info(f"Total HTML files: {len(all_files)}")
        logging.info(f"Archive pages: {len(archive_files)}")
        logging.info(f"News articles: {len(article_files)}")
        logging.info(f"Expected articles: ~7,000")
        logging.info(f"Coverage: {len(article_files)/7000*100:.1f}%")

if __name__ == "__main__":
    main()