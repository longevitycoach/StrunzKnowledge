#!/usr/bin/env python3
"""
Proper News Downloader - Downloads all news articles correctly
"""

import subprocess
import time
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_proper_download.log'),
        logging.StreamHandler()
    ]
)

def download_news_properly():
    """Download news with correct wget parameters"""
    
    logging.info("Starting proper news download")
    logging.info("This will download ~7,000 articles from 140 archive pages")
    
    # Ensure directory exists
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = []
    
    # First, download the main news page and archive pages
    logging.info("Downloading archive pages...")
    
    for page in range(140):
        # Build the archive URL
        if page == 0:
            url = "https://www.strunz.com/news/archiv?limit=50"
        else:
            url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        
        logging.info(f"Processing archive page {page + 1}/140: {url}")
        
        # Simpler wget command that actually works
        cmd = [
            "wget",
            "--recursive",
            "--level=3",  # Go deep enough to get individual articles
            "--no-clobber",  # Don't re-download existing files
            "--page-requisites",
            "--html-extension",
            "--convert-links",
            "--restrict-file-names=windows",
            "--domains=www.strunz.com",
            "--no-parent",
            "--directory-prefix=data/raw",
            "--no-host-directories",
            "--accept=*.html",
            "--reject=*.jpg,*.jpeg,*.png,*.gif,*.pdf,*.css,*.js,*.ico",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--wait=0.5",
            "--random-wait",
            url
        ]
        
        try:
            # Run wget
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 or result.returncode == 8:  # 8 = some errors but continued
                successful += 1
                logging.info(f"  ✓ Page {page + 1} processed")
            else:
                failed.append(page)
                logging.warning(f"  ✗ Page {page + 1} failed: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            failed.append(page)
            logging.error(f"  ✗ Page {page + 1} timed out")
        except Exception as e:
            failed.append(page)
            logging.error(f"  ✗ Page {page + 1} error: {e}")
        
        # Progress update
        if (page + 1) % 10 == 0:
            logging.info(f"Progress: {page + 1}/140 pages ({successful} successful)")
            # Count current files
            news_files = list(Path("data/raw/news").rglob("*.html"))
            logging.info(f"  Current news files: {len(news_files)}")
    
    # Final summary
    logging.info("\n" + "="*50)
    logging.info("DOWNLOAD COMPLETE")
    logging.info("="*50)
    logging.info(f"Archive pages processed: {successful}/140")
    if failed:
        logging.warning(f"Failed pages: {failed}")
    
    # Count final results
    all_files = list(Path("data/raw").rglob("*.html"))
    news_files = [f for f in all_files if "/news/" in str(f) or "news/" in f.name]
    archive_files = [f for f in news_files if "archiv" in f.name]
    article_files = [f for f in news_files if "archiv" not in f.name]
    
    logging.info(f"\nFinal counts:")
    logging.info(f"  Total HTML files: {len(all_files)}")
    logging.info(f"  News-related files: {len(news_files)}")
    logging.info(f"  Archive pages: {len(archive_files)}")
    logging.info(f"  Article files: {len(article_files)}")
    
    # Clean up any non-news files that might have been downloaded
    logging.info("\nCleaning up non-news content...")
    cleanup_count = 0
    for file in Path("data/raw").rglob("*.html"):
        file_str = str(file)
        # Keep only news and forum files
        if "/news/" not in file_str and "/forum/" not in file_str and "news" not in file.parent.name and "forum" not in file.parent.name:
            if file.is_file():
                file.unlink()
                cleanup_count += 1
    
    if cleanup_count > 0:
        logging.info(f"  Removed {cleanup_count} non-news/forum files")
    
    # Move news files to proper location if needed
    news_dir = Path("data/raw/news")
    move_count = 0
    for file in Path("data/raw").rglob("*.html"):
        if "/news/" in str(file) and file.parent != news_dir:
            # Move to news directory
            new_path = news_dir / file.name
            if not new_path.exists():
                file.rename(new_path)
                move_count += 1
    
    if move_count > 0:
        logging.info(f"  Moved {move_count} files to news directory")
    
    # Final count
    final_news_files = list(Path("data/raw/news").rglob("*.html"))
    logging.info(f"\nFinal news articles in data/raw/news: {len(final_news_files)}")
    
    if len(final_news_files) < 1000:
        logging.warning("Warning: Downloaded fewer than 1000 articles. You may want to re-run the script.")
    
    return len(final_news_files)

if __name__ == "__main__":
    # Create directories
    Path("logs").mkdir(exist_ok=True)
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    # Run download
    total_files = download_news_properly()
    
    if total_files < 1000:
        print(f"\n⚠️  Only {total_files} news files downloaded.")
        print("The news section might require authentication or has a different structure.")
        print("You may need to adjust the wget parameters or use a different approach.")
    else:
        print(f"\n✅ Successfully downloaded {total_files} news articles!")