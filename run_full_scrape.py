#!/usr/bin/env python3
"""
Run full scraping of all Strunz website content.
This will take considerable time due to pagination and rate limiting.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from scrape_strunz import StrunzContentScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraping.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run full scraping with all categories."""
    
    logger.info("="*60)
    logger.info("Starting FULL Strunz Knowledge Base Scraping")
    logger.info("This will take considerable time...")
    logger.info("="*60)
    
    # Create scraper without article limit
    scraper = StrunzContentScraper(max_articles=None)
    
    # Override to scrape all categories
    scraper.categories = [
        ("News", f"{scraper.base_url}/news.html"),
        ("Forum: Fitness", f"{scraper.base_url}/forum/fitness"),
        ("Forum: Gesundheit", f"{scraper.base_url}/forum/gesundheit"),
        ("Forum: Ernährung", f"{scraper.base_url}/forum/ernaehrung"),
        ("Forum: Bluttuning", f"{scraper.base_url}/forum/bluttuning"),
        ("Forum: Mental", f"{scraper.base_url}/forum/mental"),
        ("Forum: Prävention", f"{scraper.base_url}/forum/infektion-und-praevention")
    ]
    
    start_time = datetime.now()
    
    try:
        # Run the scraper
        all_articles = {}
        
        for category_name, category_url in scraper.categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting category: {category_name}")
            logger.info(f"URL: {category_url}")
            logger.info(f"{'='*60}")
            
            articles = scraper.scrape_category(category_name, category_url)
            all_articles[category_name] = articles
            
            logger.info(f"Completed {category_name}: {len(articles)} articles")
        
        # Save overall summary
        scraper._save_overall_summary(all_articles)
        
        # Calculate statistics
        end_time = datetime.now()
        duration = end_time - start_time
        
        total_articles = sum(len(articles) for articles in all_articles.values())
        
        logger.info("\n" + "="*60)
        logger.info("SCRAPING COMPLETE!")
        logger.info(f"Total time: {duration}")
        logger.info(f"Total categories: {len(all_articles)}")
        logger.info(f"Total articles: {total_articles}")
        logger.info(f"Average time per article: {duration.total_seconds() / total_articles:.2f} seconds")
        logger.info("="*60)
        
        # Create completion report
        report_path = Path("data/raw/scraping_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Strunz Knowledge Base Scraping Report\n\n")
            f.write(f"**Date**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration**: {duration}\n")
            f.write(f"**Total Articles**: {total_articles}\n\n")
            
            f.write("## Category Breakdown\n\n")
            for category, articles in all_articles.items():
                f.write(f"- **{category}**: {len(articles)} articles\n")
            
            f.write(f"\n## Output Files\n\n")
            f.write(f"- Docling Input: `data/raw/docling_input/`\n")
            f.write(f"- JSON Data: `data/raw/*.json`\n")
            f.write(f"- Markdown Summaries: `data/raw/*.md`\n")
        
        logger.info(f"Report saved to: {report_path}")
        
    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user!")
        logger.info("Partial results have been saved.")
    except Exception as e:
        logger.error(f"Scraping failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Confirm before starting
    print("\n" + "="*60)
    print("FULL SCRAPING MODE")
    print("="*60)
    print("This will scrape ALL content from strunz.com")
    print("This process may take several hours.")
    print("The scraper will respect rate limits (1 second between requests).")
    print("\nPress Ctrl+C at any time to stop (partial results will be saved).")
    print("="*60)
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Scraping cancelled.")
        sys.exit(0)
    
    main()