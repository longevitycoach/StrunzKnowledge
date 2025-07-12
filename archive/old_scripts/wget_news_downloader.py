#!/usr/bin/env python3
"""
News Downloader - Downloads all news articles including archives using wget
"""

import subprocess
import time
import os
from pathlib import Path

def download_news():
    """Download all news articles including archives"""
    
    # Create backup of existing news if any
    news_dir = Path("data/raw/news")
    if news_dir.exists():
        backup_dir = Path("data/raw/news_backup_" + time.strftime("%Y%m%d_%H%M%S"))
        print(f"Backing up existing news to {backup_dir}")
        os.rename(news_dir, backup_dir)
    
    print("Starting news download with wget...")
    print("This will download all news articles and archive pages")
    
    # Base wget command for news
    base_cmd = [
        "wget",
        "--recursive",
        "--level=10",  # Deeper recursion for archives
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--cut-dirs=0",  # Keep /news structure
        "--page-requisites",
        "--html-extension",
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--no-parent",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "--wait=1",
        "--random-wait",
        "--accept-regex=.*/news/.*",  # Only news pages
        "--reject-regex=.*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf|jpg|jpeg|png|gif|ico|css|js)$",
        "https://www.strunz.com/news"
    ]
    
    # Log file
    log_file = "logs/news_download.log"
    
    print(f"\nDownloading news articles...")
    print(f"Log file: {log_file}")
    
    # Run wget
    with open(log_file, 'w') as log:
        try:
            # Start the download
            process = subprocess.Popen(
                base_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor progress
            for line in process.stdout:
                log.write(line)
                log.flush()
                
                # Show progress indicators
                if "Saving to:" in line:
                    filename = line.split("Saving to: '")[1].split("'")[0]
                    print(f"  Downloading: {filename}")
                elif "--" in line and "https://" in line:
                    url = line.split("--  ")[1].strip()
                    if "/news/" in url:
                        print(f"  Fetching: {url}")
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                print("\n✓ News download completed successfully!")
            else:
                print(f"\n✗ News download failed with code {process.returncode}")
                
        except KeyboardInterrupt:
            print("\n\nDownload interrupted by user")
            process.terminate()
            process.wait()
        except Exception as e:
            print(f"\nError during download: {e}")
    
    # Count downloaded files
    if Path("data/raw/www.strunz.com/news").exists():
        news_files = list(Path("data/raw/www.strunz.com/news").rglob("*.html"))
        print(f"\nDownloaded {len(news_files)} news HTML files")
        
        # Show sample of files
        print("\nSample of downloaded files:")
        for file in sorted(news_files)[:10]:
            print(f"  - {file.name}")
        
        if len(news_files) > 10:
            print(f"  ... and {len(news_files) - 10} more files")

def download_news_archive_pages():
    """Download news archive pagination pages"""
    
    print("\n\nDownloading news archive pages...")
    
    # The news archive has pagination
    archive_urls = []
    
    # First, get the main archive page to find total pages
    test_cmd = [
        "wget",
        "--output-document=-",
        "--quiet",
        "--user-agent=Mozilla/5.0",
        "https://www.strunz.com/news/archiv"
    ]
    
    try:
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # Look for pagination links
            content = result.stdout
            # Extract page numbers from pagination
            import re
            pages = re.findall(r'/news/archiv\?page=(\d+)', content)
            if pages:
                max_page = max(int(p) for p in pages)
                print(f"Found {max_page} archive pages")
                
                # Generate archive URLs
                for page in range(1, max_page + 1):
                    archive_urls.append(f"https://www.strunz.com/news/archiv?page={page}")
    except:
        # Fallback: assume 50 pages
        print("Using default 50 archive pages")
        for page in range(1, 51):
            archive_urls.append(f"https://www.strunz.com/news/archiv?page={page}")
    
    # Download each archive page
    for i, url in enumerate(archive_urls, 1):
        print(f"  Downloading archive page {i}/{len(archive_urls)}: {url}")
        
        cmd = [
            "wget",
            "--recursive",
            "--level=3",
            "--directory-prefix=data/raw",
            "--no-host-directories", 
            "--cut-dirs=0",
            "--page-requisites",
            "--html-extension",
            "--convert-links",
            "--domains=strunz.com,www.strunz.com",
            "--user-agent=Mozilla/5.0",
            "--wait=0.5",
            "--random-wait",
            "--quiet",
            "--accept-regex=.*/news/.*",
            "--reject-regex=.*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf|jpg|jpeg|png|gif|ico|css|js)$",
            url
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Show progress
        if i % 10 == 0:
            print(f"    Progress: {i}/{len(archive_urls)} pages processed")
    
    print("\n✓ Archive download completed!")

def main():
    """Main function"""
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    print("=== News and Archive Downloader ===")
    print("This will download all news articles and archive pages")
    print()
    
    # Download main news
    download_news()
    
    # Download archive pages
    download_news_archive_pages()
    
    # Final summary
    if Path("data/raw/www.strunz.com/news").exists():
        all_files = list(Path("data/raw/www.strunz.com/news").rglob("*.html"))
        archive_files = [f for f in all_files if "archiv" in str(f)]
        article_files = [f for f in all_files if "archiv" not in str(f)]
        
        print("\n=== Download Summary ===")
        print(f"Total HTML files: {len(all_files)}")
        print(f"News articles: {len(article_files)}")
        print(f"Archive pages: {len(archive_files)}")
        print(f"Location: data/raw/www.strunz.com/news/")

if __name__ == "__main__":
    main()