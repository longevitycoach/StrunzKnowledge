#!/usr/bin/env python3
"""
Run COMPLETE scraping of ALL Strunz website content.
This will scrape all available articles without limits.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from scrape_strunz import StrunzContentScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('complete_scraping.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
scraper = None
interrupted = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global interrupted
    interrupted = True
    logger.warning("\n🛑 Scraping interrupted by user! Saving current progress...")

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def main():
    """Run complete scraping with all categories and no limits."""
    global scraper, interrupted
    
    logger.info("="*80)
    logger.info("🚀 STARTING COMPLETE STRUNZ KNOWLEDGE BASE SCRAPING")
    logger.info("="*80)
    logger.info("📋 This will scrape ALL available content without limits")
    logger.info("⏱️  Estimated time: 2-4 hours depending on content volume")
    logger.info("💾 All progress will be saved continuously")
    logger.info("🛑 Press Ctrl+C to stop gracefully at any time")
    logger.info("="*80)
    
    # Create scraper with NO limits
    scraper = StrunzContentScraper(max_articles=None)  # No limit!
    
    # Complete category list
    categories = [
        ("News", f"{scraper.base_url}/news.html"),
        ("Forum: Fitness", f"{scraper.base_url}/forum/fitness"),
        ("Forum: Gesundheit", f"{scraper.base_url}/forum/gesundheit"),
        ("Forum: Ernährung", f"{scraper.base_url}/forum/ernaehrung"),
        ("Forum: Bluttuning", f"{scraper.base_url}/forum/bluttuning"),
        ("Forum: Mental", f"{scraper.base_url}/forum/mental"),
        ("Forum: Prävention", f"{scraper.base_url}/forum/infektion-und-praevention")
    ]
    
    start_time = datetime.now()
    all_articles = {}
    completed_categories = []
    
    try:
        for category_name, category_url in categories:
            if interrupted:
                logger.warning(f"⏸️  Stopping before {category_name} due to interruption")
                break
                
            logger.info(f"\n{'='*80}")
            logger.info(f"📂 STARTING CATEGORY: {category_name}")
            logger.info(f"🔗 URL: {category_url}")
            logger.info(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
            logger.info(f"{'='*80}")
            
            category_start = datetime.now()
            
            try:
                articles = scraper.scrape_category(category_name, category_url)
                all_articles[category_name] = articles
                completed_categories.append(category_name)
                
                category_duration = datetime.now() - category_start
                logger.info(f"\n✅ COMPLETED {category_name}:")
                logger.info(f"   📄 Articles scraped: {len(articles)}")
                logger.info(f"   ⏱️  Time taken: {category_duration}")
                if articles:
                    logger.info(f"   📊 Avg time per article: {category_duration.total_seconds() / len(articles):.1f}s")
                
                # Check for interruption after each category
                if interrupted:
                    logger.warning(f"⏸️  Stopping after {category_name} due to interruption")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error scraping {category_name}: {e}")
                logger.info(f"⏭️  Continuing with next category...")
                all_articles[category_name] = []
        
        # Save overall summary even if interrupted
        if all_articles:
            scraper._save_overall_summary(all_articles)
        
        # Calculate final statistics
        end_time = datetime.now()
        total_duration = end_time - start_time
        total_articles = sum(len(articles) for articles in all_articles.values())
        
        logger.info("\n" + "="*80)
        if interrupted:
            logger.info("⏸️  SCRAPING STOPPED BY USER")
        else:
            logger.info("🎉 COMPLETE SCRAPING FINISHED!")
        logger.info("="*80)
        logger.info(f"⏱️  Total time: {total_duration}")
        logger.info(f"📂 Categories completed: {len(completed_categories)}/{len(categories)}")
        logger.info(f"📄 Total articles: {total_articles}")
        
        if total_articles > 0:
            logger.info(f"📊 Average time per article: {total_duration.total_seconds() / total_articles:.1f}s")
        
        # Category breakdown
        logger.info(f"\n📋 CATEGORY BREAKDOWN:")
        for category, articles in all_articles.items():
            status = "✅" if len(articles) > 0 else "❌"
            logger.info(f"   {status} {category}: {len(articles)} articles")
        
        # Create detailed completion report
        report_path = Path("data/raw/complete_scraping_report.md")
        create_completion_report(report_path, all_articles, total_duration, interrupted, completed_categories)
        
        logger.info(f"\n📊 Detailed report saved to: {report_path}")
        logger.info(f"📁 All content available in: data/raw/docling_input/")
        
        return all_articles
        
    except Exception as e:
        logger.error(f"💥 Critical error during scraping: {e}", exc_info=True)
        return all_articles if 'all_articles' in locals() else {}

def create_completion_report(report_path: Path, all_articles: dict, duration, interrupted: bool, completed_categories: list):
    """Create a detailed completion report."""
    total_articles = sum(len(articles) for articles in all_articles.values())
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Complete Strunz Knowledge Base Scraping Report\n\n")
        
        if interrupted:
            f.write(f"⚠️ **Status**: Interrupted by user\n")
        else:
            f.write(f"✅ **Status**: Completed successfully\n")
            
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duration**: {duration}\n")
        f.write(f"**Total Articles**: {total_articles}\n")
        f.write(f"**Categories Completed**: {len(completed_categories)}/7\n\n")
        
        f.write("## Category Results\n\n")
        for category, articles in all_articles.items():
            status = "✅ Success" if len(articles) > 0 else "❌ Failed"
            f.write(f"### {category}\n")
            f.write(f"- **Status**: {status}\n")
            f.write(f"- **Articles**: {len(articles)}\n")
            
            if articles:
                # Show sample articles
                f.write(f"- **Sample articles**:\n")
                for i, article in enumerate(articles[:3]):
                    f.write(f"  - {article.get('title', 'Untitled')} ({len(article.get('content_text', ''))} chars)\n")
                if len(articles) > 3:
                    f.write(f"  - ... and {len(articles) - 3} more\n")
            f.write("\n")
        
        f.write(f"## Output Structure\n\n")
        f.write(f"```\n")
        f.write(f"data/raw/\n")
        f.write(f"├── docling_input/           # Structured HTML for Docling\n")
        for category in all_articles.keys():
            safe_name = category.replace(' ', '_').replace(':', '').lower()
            f.write(f"│   └── {safe_name}/\n")
        f.write(f"├── *.json                   # JSON data for each category\n")
        f.write(f"├── *.md                     # Markdown summaries\n")
        f.write(f"└── complete_scraping_report.md\n")
        f.write(f"```\n\n")
        
        if interrupted:
            f.write(f"## Recovery Instructions\n\n")
            f.write(f"To continue scraping from where you left off:\n")
            f.write(f"1. Review which categories were completed\n")
            f.write(f"2. Modify the category list in the scraper\n")
            f.write(f"3. Re-run the scraping script\n\n")
        
        f.write(f"## Next Steps\n\n")
        f.write(f"1. **Review content quality** using `python scraping_analysis.py`\n")
        f.write(f"2. **Process with Docling** for enhanced text extraction\n")
        f.write(f"3. **Build FAISS index** for vector search\n")
        f.write(f"4. **Test MCP server** with real content\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 COMPLETE STRUNZ KNOWLEDGE BASE SCRAPING")
    print("="*80)
    print("This will scrape ALL available content from strunz.com")
    print("⚠️  This process may take 2-4 hours")
    print("💾 Progress is saved continuously")
    print("🛑 Press Ctrl+C to stop gracefully at any time")
    print("="*80)
    
    # Auto-start without confirmation for automation
    main()