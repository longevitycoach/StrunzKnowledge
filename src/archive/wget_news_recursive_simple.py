#!/usr/bin/env python3
"""
Simple Recursive News Downloader - Just get ALL news articles recursively
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_recursive_simple.log'),
        logging.StreamHandler()
    ]
)

def download_all_news():
    """Simple recursive download of ALL news articles"""
    
    logging.info("Starting simple recursive news download")
    logging.info("This will download ALL news articles from www.strunz.com/news/")
    
    # Create directory
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    # Simple wget command - just get everything under /news/
    cmd = [
        "wget",
        "--mirror",  # Mirror the site structure
        "--no-parent",  # Don't go up to parent directories
        "--page-requisites",
        "--adjust-extension",
        "--convert-links",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--reject=index.html*,archiv.html*,archiv*",  # Skip archive pages
        "--accept=*.html",  # Only HTML files
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.pdf,*.css,*.js,*.ico,*.xml,*.txt",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "--wait=0.2",
        "--random-wait",
        "--limit-rate=500k",
        "--timeout=30",
        "--tries=3",
        "--continue",  # Continue partial downloads
        "https://www.strunz.com/news/"
    ]
    
    logging.info("Running wget --mirror to download all news articles...")
    logging.info("Command: " + " ".join(cmd))
    
    try:
        # Run wget
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor output
        articles = 0
        for line in process.stdout:
            if "Saving to:" in line and "/news/" in line and "archiv" not in line:
                articles += 1
                if articles % 100 == 0:
                    logging.info(f"Downloaded {articles} articles so far...")
                elif articles % 10 == 0:
                    print(f"\rDownloaded {articles} articles...", end='', flush=True)
        
        process.wait()
        
        if process.returncode == 0 or process.returncode == 8:
            logging.info(f"\nWget completed! Downloaded approximately {articles} articles")
        else:
            logging.warning(f"\nWget finished with code {process.returncode}")
            
    except KeyboardInterrupt:
        logging.info("\nDownload interrupted by user")
        process.terminate()
        process.wait()
    except Exception as e:
        logging.error(f"Error: {e}")
    
    # Count results
    count_downloaded_articles()

def count_downloaded_articles():
    """Count and report on downloaded articles"""
    
    news_dir = Path("data/raw/news")
    if news_dir.exists():
        all_files = list(news_dir.rglob("*.html"))
        
        # Separate articles from other files
        articles = []
        archive_files = []
        other_files = []
        
        for f in all_files:
            if "archiv" in f.name.lower():
                archive_files.append(f)
            elif f.name == "index.html":
                other_files.append(f)
            else:
                articles.append(f)
        
        logging.info("\n=== DOWNLOAD SUMMARY ===")
        logging.info(f"Total HTML files: {len(all_files)}")
        logging.info(f"News articles: {len(articles)}")
        logging.info(f"Archive pages: {len(archive_files)} (ignored)")
        logging.info(f"Other files: {len(other_files)}")
        
        if articles:
            logging.info("\nFirst 10 articles:")
            for article in sorted(articles)[:10]:
                logging.info(f"  - {article.name}")
            if len(articles) > 10:
                logging.info(f"  ... and {len(articles) - 10} more")
        
        print(f"\n{'✅' if len(articles) > 1000 else '⚠️ '}  Downloaded {len(articles)} news articles")
        
        if len(articles) < 1000:
            print("\nIf you need more articles, try:")
            print("1. Remove --no-parent flag to follow more links")
            print("2. Increase --level parameter")
            print("3. Run multiple times - wget continues partial downloads")
            
    else:
        logging.error("No news directory found!")

def alternative_spider_approach():
    """Alternative: Use wget spider mode to find all URLs first"""
    
    logging.info("\nAlternative approach: Spider mode to find all article URLs")
    
    # First, spider the site to get all URLs
    spider_cmd = [
        "wget",
        "--spider",  # Don't download, just check URLs
        "--recursive",
        "--level=10",  # Go deep
        "--no-parent",
        "--accept=*.html",
        "--reject=*archiv*,index.html",
        "--user-agent=Mozilla/5.0",
        "--wait=0.1",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "https://www.strunz.com/news/",
        "2>&1",  # Redirect stderr to stdout
        "|",
        "grep", "'^--'",  # Find URL lines
        "|",
        "awk", "'{print $3}'"  # Extract URLs
    ]
    
    # This would give us a list of all URLs to download
    # Then we could download them one by one

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    
    print("=== Simple News Downloader ===")
    print("This will recursively download ALL news articles")
    print("Expected: ~7,000 articles from www.strunz.com/news/")
    print()
    
    response = input("Start download? (y/n): ")
    if response.lower() == 'y':
        download_all_news()
    else:
        print("Download cancelled")