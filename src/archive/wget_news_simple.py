#!/usr/bin/env python3
"""
Simple News Downloader - Direct approach for news articles
"""

import subprocess
import time
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_simple_download.log'),
        logging.StreamHandler()
    ]
)

def download_all_news():
    """Download all news articles using a simple recursive approach"""
    
    logging.info("Starting news download with simple recursive approach")
    
    # Create directory
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    # Simple wget command that follows all news links
    cmd = [
        "wget",
        "--recursive",
        "--level=5",
        "--no-clobber",
        "--page-requisites",
        "--html-extension", 
        "--convert-links",
        "--domains=www.strunz.com",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--accept-regex=/news/[a-z0-9-]+\\.html",  # Match news article pattern
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.pdf,*.css,*.js,*.ico,*.mp3,*.mp4",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "--wait=0.2",
        "--random-wait",
        "--limit-rate=200k",  # Be nice to the server
        "https://www.strunz.com/news",
        "https://www.strunz.com/news/archiv"
    ]
    
    # Also download archive pages with pagination
    for page in range(140):
        if page == 0:
            cmd.append("https://www.strunz.com/news/archiv?limit=50")
        else:
            cmd.append(f"https://www.strunz.com/news/archiv?limit=50&p={page}")
    
    logging.info("Running wget with recursive download...")
    logging.info("This will take a while as it downloads ~7,000 articles")
    
    try:
        # Run wget - this will take a long time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor progress
        for line in process.stdout:
            if "Saving to:" in line and "/news/" in line:
                filename = line.split("'")[1] if "'" in line else "unknown"
                if "archiv" not in filename:
                    logging.info(f"  Downloaded: {filename}")
        
        process.wait()
        
        if process.returncode == 0:
            logging.info("✓ News download completed successfully")
        else:
            logging.warning(f"wget finished with code {process.returncode}")
            
    except KeyboardInterrupt:
        logging.info("Download interrupted by user")
        process.terminate()
        process.wait()
    except Exception as e:
        logging.error(f"Error during download: {e}")
    
    # Count results
    return count_and_organize_news()

def count_and_organize_news():
    """Count and organize downloaded news files"""
    
    logging.info("\nOrganizing news files...")
    
    # Find all news HTML files
    all_news = []
    for file in Path("data/raw").rglob("*.html"):
        if "/news/" in str(file) or (file.parent.name == "news" and "news" in file.name):
            all_news.append(file)
    
    # Move files to news directory if needed
    news_dir = Path("data/raw/news")
    moved = 0
    
    for file in all_news:
        if file.parent != news_dir:
            new_path = news_dir / file.name
            if not new_path.exists():
                file.rename(new_path)
                moved += 1
    
    # Final count
    final_news = list(news_dir.glob("*.html"))
    archive_files = [f for f in final_news if "archiv" in f.name]
    article_files = [f for f in final_news if "archiv" not in f.name]
    
    logging.info(f"\nFinal statistics:")
    logging.info(f"  Total news files: {len(final_news)}")
    logging.info(f"  Archive pages: {len(archive_files)}")
    logging.info(f"  News articles: {len(article_files)}")
    if moved > 0:
        logging.info(f"  Files organized: {moved}")
    
    # Sample of articles
    if article_files:
        logging.info(f"\nSample articles downloaded:")
        for article in sorted(article_files)[:5]:
            logging.info(f"  - {article.name}")
        if len(article_files) > 5:
            logging.info(f"  ... and {len(article_files) - 5} more")
    
    return len(article_files)

def alternative_download():
    """Alternative method: Download archive pages first, then extract links"""
    
    logging.info("\nTrying alternative download method...")
    logging.info("First downloading all archive pages to extract article links")
    
    # Step 1: Download all archive pages
    archive_dir = Path("data/raw/news/archives")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for page in range(140):
        if page == 0:
            url = "https://www.strunz.com/news/archiv?limit=50"
        else:
            url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        
        output_file = archive_dir / f"archiv_p{page}.html"
        
        if not output_file.exists():
            cmd = ["wget", "-O", str(output_file), "--user-agent=Mozilla/5.0", url]
            subprocess.run(cmd, capture_output=True)
            logging.info(f"Downloaded archive page {page + 1}/140")
            time.sleep(0.5)
    
    # Step 2: Extract all article URLs
    article_urls = set()
    import re
    
    for archive_file in archive_dir.glob("*.html"):
        try:
            content = archive_file.read_text(encoding='utf-8', errors='ignore')
            # Find all news article links
            links = re.findall(r'href="/news/([a-z0-9-]+)\.html"', content)
            for link in links:
                article_urls.add(f"https://www.strunz.com/news/{link}.html")
        except:
            pass
    
    logging.info(f"Found {len(article_urls)} unique article URLs")
    
    # Step 3: Download each article
    news_dir = Path("data/raw/news")
    downloaded = 0
    
    for i, url in enumerate(article_urls, 1):
        filename = url.split('/')[-1]
        output_file = news_dir / filename
        
        if not output_file.exists():
            cmd = ["wget", "-O", str(output_file), "--user-agent=Mozilla/5.0", url]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                downloaded += 1
                if downloaded % 100 == 0:
                    logging.info(f"Downloaded {downloaded}/{len(article_urls)} articles")
            
            time.sleep(0.2)  # Be nice to the server
    
    logging.info(f"Downloaded {downloaded} new articles")
    return downloaded

if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    
    # Try the simple recursive approach first
    article_count = download_all_news()
    
    # If we don't have enough articles, try the alternative method
    if article_count < 1000:
        logging.info(f"\nOnly {article_count} articles found with recursive method")
        logging.info("Trying alternative download method...")
        
        additional = alternative_download()
        article_count = count_and_organize_news()
    
    if article_count < 1000:
        print(f"\n⚠️  Only {article_count} news articles downloaded")
        print("This is less than expected. Possible reasons:")
        print("1. The site structure has changed")
        print("2. Some content requires authentication")
        print("3. Rate limiting is in effect")
    else:
        print(f"\n✅ Successfully downloaded {article_count} news articles!")