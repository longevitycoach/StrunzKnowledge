#!/usr/bin/env python3
"""
Strict Wget Downloader - Only Forum and News Content
====================================================

Ensures ONLY forum and news content is downloaded, nothing else.
Uses strict URL filtering to prevent downloading shop, static content, etc.

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
"""

import subprocess
import time
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/strict_download.log'),
        logging.StreamHandler()
    ]
)

def download_forum_category(category: str, url_name: str):
    """Download a single forum category with strict filtering"""
    
    logging.info(f"Downloading forum category: {category} ({url_name})")
    
    # Strict wget command - ONLY forum content
    cmd = [
        "wget",
        "--recursive",
        "--level=5",
        "--directory-prefix=data/raw/forum",
        "--no-host-directories",
        "--cut-dirs=1",  # Removes /forum/ from path
        "--html-extension",
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--no-parent",  # Don't go up to parent directories
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "--wait=1",
        "--random-wait",
        # Strict URL acceptance - ONLY this forum category
        f"--include-directories=/forum/{url_name}",
        # Accept only HTML files in this category
        f"--accept={url_name}*.html,{url_name}?*.html,{url_name}/*.html",
        # Reject all media and document files
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.ico,*.css,*.js,*.pdf,*.zip,*.exe,*.doc,*.docx",
        "--reject=*shop*,*product*,*catalog*,*cart*,*checkout*,*customer*",
        # Start URL
        f"https://www.strunz.com/forum/{url_name}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"✓ {category} downloaded successfully")
        else:
            logging.error(f"✗ {category} download failed: {result.stderr}")
    except Exception as e:
        logging.error(f"✗ {category} download error: {e}")

def download_news_with_pagination():
    """Download news with strict pagination (limit=50, pages 0-139)"""
    
    logging.info("Downloading news with pagination (140 pages × 50 articles)")
    
    # Ensure news directory exists
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    successful_pages = 0
    
    for page in range(140):
        url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        logging.info(f"Downloading news page {page + 1}/140")
        
        cmd = [
            "wget",
            "--recursive",
            "--level=2",  # Follow links to individual articles
            "--directory-prefix=data/raw/news",
            "--no-host-directories",
            "--cut-dirs=1",  # Remove /news/ from path
            "--html-extension",
            "--convert-links",
            "--domains=strunz.com,www.strunz.com",
            "--no-parent",
            "--user-agent=Mozilla/5.0",
            "--wait=0.5",
            "--random-wait",
            # Strict inclusion - ONLY news directory
            "--include-directories=/news",
            # Accept only news HTML files
            "--accept=news/*.html,archiv*.html",
            # Reject all non-news content
            "--reject=*.jpg,*.jpeg,*.png,*.gif,*.ico,*.css,*.js,*.pdf",
            "--reject=*shop*,*product*,*catalog*,*cart*,*forum*",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                successful_pages += 1
                if (page + 1) % 10 == 0:
                    logging.info(f"Progress: {page + 1}/140 pages ({successful_pages} successful)")
        except:
            logging.error(f"Failed to download page {page + 1}")
        
        time.sleep(0.5)  # Be nice to the server
    
    logging.info(f"News download complete: {successful_pages}/140 pages successful")

def download_all_content():
    """Download all forum categories and news with strict filtering"""
    
    logging.info("=== STRICT CONTENT DOWNLOAD ===")
    logging.info("Downloading ONLY forum and news content")
    
    # Forum categories
    forum_categories = {
        'fitness': 'fitness',
        'gesundheit': 'gesundheit',
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    # Download each forum category
    logging.info("\n--- FORUM DOWNLOADS ---")
    for category, url_name in forum_categories.items():
        download_forum_category(category, url_name)
        time.sleep(2)  # Pause between categories
    
    # Download news
    logging.info("\n--- NEWS DOWNLOADS ---")
    download_news_with_pagination()
    
    # Summary
    logging.info("\n=== DOWNLOAD COMPLETE ===")
    
    # Count files
    forum_files = list(Path("data/raw/forum").rglob("*.html"))
    news_files = list(Path("data/raw/news").rglob("*.html"))
    
    logging.info(f"Forum files: {len(forum_files)}")
    logging.info(f"News files: {len(news_files)}")
    logging.info(f"Total files: {len(forum_files) + len(news_files)}")

def create_update_script():
    """Create script for incremental updates"""
    
    script_content = '''#!/usr/bin/env python3
"""
Incremental Update Script - Only New/Modified Content
"""

import subprocess
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def update_forum_category(category: str, url_name: str):
    """Update a forum category - only new/modified files"""
    
    cmd = [
        "wget",
        "--recursive",
        "--level=5",
        "--directory-prefix=data/raw/forum",
        "--no-host-directories",
        "--cut-dirs=1",
        "--timestamping",  # Only download newer files
        "--no-clobber",    # Don't overwrite existing files
        "--html-extension",
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--no-parent",
        "--user-agent=Mozilla/5.0",
        "--wait=1",
        "--random-wait",
        f"--include-directories=/forum/{url_name}",
        f"--accept={url_name}*.html",
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.ico,*.css,*.js,*.pdf",
        f"https://www.strunz.com/forum/{url_name}"
    ]
    
    logging.info(f"Updating {category}...")
    subprocess.run(cmd, capture_output=True)

def update_news():
    """Update news - check recent pages only"""
    
    # Only check first 10 pages for updates
    for page in range(10):
        url = f"https://www.strunz.com/news/archiv?limit=50&p={page}"
        
        cmd = [
            "wget",
            "--recursive",
            "--level=2",
            "--directory-prefix=data/raw/news",
            "--no-host-directories",
            "--cut-dirs=1",
            "--timestamping",
            "--no-clobber",
            "--html-extension",
            "--convert-links",
            "--domains=strunz.com,www.strunz.com",
            "--no-parent",
            "--user-agent=Mozilla/5.0",
            "--include-directories=/news",
            "--accept=news/*.html,archiv*.html",
            "--reject=*.jpg,*.jpeg,*.png,*.gif,*.ico,*.css,*.js,*.pdf",
            url
        ]
        
        subprocess.run(cmd, capture_output=True)

if __name__ == "__main__":
    logging.info("Starting incremental update...")
    
    # Update forums
    forums = {
        'fitness': 'fitness',
        'gesundheit': 'gesundheit',
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    for category, url_name in forums.items():
        update_forum_category(category, url_name)
    
    # Update news
    update_news()
    
    logging.info("Update complete!")
'''
    
    update_file = Path("src/tools/incremental_update.py")
    with open(update_file, 'w') as f:
        f.write(script_content)
    
    update_file.chmod(0o755)
    logging.info(f"Created update script: {update_file}")

if __name__ == "__main__":
    # Ensure directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("data/raw/forum").mkdir(parents=True, exist_ok=True)
    Path("data/raw/news").mkdir(parents=True, exist_ok=True)
    
    # Run full download
    download_all_content()
    
    # Create update script
    create_update_script()
    
    logging.info("\nUse src/tools/incremental_update.py for daily updates")