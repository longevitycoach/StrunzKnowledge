#!/usr/bin/env python3
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
    
    logging.info("Updating news articles...")
    
    # Only check first 10 pages for updates
    urls = ["https://www.strunz.com/news"]
    for page in range(10):
        if page == 0:
            urls.append("https://www.strunz.com/news/archiv?limit=50")
        else:
            urls.append(f"https://www.strunz.com/news/archiv?limit=50&p={page}")
    
    cmd = [
        "wget",
        "--recursive",
        "--level=3",
        "--directory-prefix=data/raw",
        "--no-host-directories",
        "--timestamping",  # Only download newer files
        "--no-clobber",    # Don't overwrite existing files
        "--html-extension",
        "--convert-links",
        "--domains=www.strunz.com",
        "--no-parent",
        "--user-agent=Mozilla/5.0",
        "--accept-regex=/news/[a-z0-9-]+\\.html",
        "--reject=*.jpg,*.jpeg,*.png,*.gif,*.ico,*.css,*.js,*.pdf",
        "--wait=0.5",
        "--random-wait"
    ] + urls
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        logging.info("News update completed successfully")
    else:
        logging.warning(f"News update finished with code {result.returncode}")

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
