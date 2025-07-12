#!/usr/bin/env python3
"""
Run improved scraping with quality filtering and better content extraction.
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper.improved_scraper import ImprovedStrunzScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('improved_scraping.log')
    ]
)

logger = logging.getLogger(__name__)


def create_output_directories():
    """Create output directory structure."""
    base_dir = Path("data/raw")
    dirs = [
        base_dir / "improved_output",
        base_dir / "improved_output" / "news",
        base_dir / "improved_output" / "forum_fitness",
        base_dir / "improved_output" / "forum_gesundheit", 
        base_dir / "improved_output" / "forum_ernährung",
        base_dir / "improved_output" / "forum_bluttuning",
        base_dir / "improved_output" / "forum_mental",
        base_dir / "improved_output" / "forum_prävention",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")


def save_content(content_list, category, output_format='json'):
    """Save scraped content in multiple formats."""
    if not content_list:
        logger.warning(f"No content to save for {category}")
        return
    
    base_dir = Path("data/raw/improved_output")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = base_dir / f"{category}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(content_list, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Saved {len(content_list)} items to {json_file}")
    
    # Save Markdown summary
    md_file = base_dir / f"{category}_{timestamp}_summary.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {category.title()} Content Summary\n\n")
        f.write(f"**Generated:** {datetime.now()}\n")
        f.write(f"**Total Items:** {len(content_list)}\n\n")
        
        # Quality distribution
        quality_scores = [item.get('quality_score', 0) for item in content_list]
        high_quality = sum(1 for s in quality_scores if s >= 0.7)
        medium_quality = sum(1 for s in quality_scores if 0.4 <= s < 0.7)
        low_quality = sum(1 for s in quality_scores if s < 0.4)
        
        f.write(f"## Quality Distribution\n\n")
        f.write(f"- High quality (≥0.7): {high_quality}\n")
        f.write(f"- Medium quality (0.4-0.7): {medium_quality}\n")
        f.write(f"- Low quality (<0.4): {low_quality}\n\n")
        
        # Top articles
        sorted_content = sorted(content_list, key=lambda x: x.get('quality_score', 0), reverse=True)
        f.write(f"## Top Quality Content\n\n")
        
        for i, item in enumerate(sorted_content[:10], 1):
            title = item.get('title', 'Untitled')[:60]
            score = item.get('quality_score', 0)
            words = item.get('word_count', 0)
            f.write(f"{i}. **{title}...** (Score: {score:.3f}, Words: {words})\n")
        
        # Save individual high-quality content as HTML
        category_dir = base_dir / category
        for i, item in enumerate(sorted_content, 1):
            if item.get('quality_score', 0) >= 0.6:  # Only save medium+ quality
                html_file = category_dir / f"{i:03d}_{title[:30].replace(' ', '_').replace('/', '_')}.html"
                
                html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="{item.get('author', 'Dr. Ulrich Strunz')}">
    <meta name="date" content="{item.get('date', '')}">
    <meta name="category" content="{category}">
    <meta name="quality_score" content="{item.get('quality_score', 0):.3f}">
    <title>{item.get('title', 'Untitled')}</title>
</head>
<body>
    <article>
        <header>
            <h1>{item.get('title', 'Untitled')}</h1>
            <p class="metadata">
                <span class="date">{item.get('date', '')}</span> | 
                <span class="author">{item.get('author', 'Dr. Ulrich Strunz')}</span> | 
                <span class="category">{category}</span> |
                <span class="quality">Quality: {item.get('quality_score', 0):.3f}</span>
            </p>
        </header>
        <div class="content">
            <div class="post-content">
                {item.get('content', '').replace('\n', '<br>\n')}
            </div>
        </div>
    </article>
</body>
</html>"""
                
                try:
                    with open(html_file, 'w', encoding='utf-8') as hf:
                        hf.write(html_content)
                except Exception as e:
                    logger.warning(f"Could not save HTML file {html_file}: {e}")
    
    logger.info(f"Saved content summary to {md_file}")


def scrape_news_improved():
    """Scrape news with improved quality filtering."""
    logger.info("Starting improved news scraping...")
    
    scraper = ImprovedStrunzScraper(use_selenium=False, delay=1.0)
    scraper.min_content_score = 0.4  # Lower threshold for testing
    
    try:
        articles = scraper.scrape_news()
        save_content(articles, "news")
        return articles
    except Exception as e:
        logger.error(f"News scraping failed: {e}")
        return []
    finally:
        scraper.close()


def scrape_forum_improved(category):
    """Scrape forum with improved extraction (no Selenium)."""
    logger.info(f"Starting improved forum scraping for {category}...")
    
    scraper = ImprovedStrunzScraper(use_selenium=False, delay=2.0)  # No Selenium, longer delay
    scraper.min_content_score = 0.3  # Even lower threshold for forum content
    
    try:
        posts = scraper.scrape_forum(category)
        save_content(posts, f"forum_{category}")
        return posts
    except Exception as e:
        logger.error(f"Forum scraping failed for {category}: {e}")
        return []
    finally:
        scraper.close()


def run_complete_improved_scraping():
    """Run complete improved scraping with quality filtering."""
    start_time = datetime.now()
    logger.info(f"Starting complete improved scraping at {start_time}")
    
    create_output_directories()
    
    results = {
        'news': [],
        'forums': {}
    }
    
    # Scrape news
    news_articles = scrape_news_improved()
    results['news'] = news_articles
    
    # Scrape forums
    forum_categories = ['fitness', 'gesundheit', 'ernährung', 'bluttuning', 'mental', 'prävention']
    
    for category in forum_categories:
        logger.info(f"\n{'='*50}")
        logger.info(f"Scraping forum: {category}")
        logger.info(f"{'='*50}")
        
        forum_posts = scrape_forum_improved(category)
        results['forums'][category] = forum_posts
        
        # Brief delay between categories
        import time
        time.sleep(3)
    
    # Generate final report
    end_time = datetime.now()
    duration = end_time - start_time
    
    total_content = len(results['news'])
    for forum_posts in results['forums'].values():
        total_content += len(forum_posts)
    
    report = {
        'timestamp': start_time.isoformat(),
        'duration': str(duration),
        'total_content_items': total_content,
        'news_articles': len(results['news']),
        'forum_categories': len(results['forums']),
        'forum_posts_by_category': {cat: len(posts) for cat, posts in results['forums'].items()},
        'quality_summary': {}
    }
    
    # Quality analysis
    all_content = results['news'].copy()
    for forum_posts in results['forums'].values():
        all_content.extend(forum_posts)
    
    if all_content:
        quality_scores = [item.get('quality_score', 0) for item in all_content]
        report['quality_summary'] = {
            'average_quality': sum(quality_scores) / len(quality_scores),
            'high_quality_count': sum(1 for s in quality_scores if s >= 0.7),
            'medium_quality_count': sum(1 for s in quality_scores if 0.4 <= s < 0.7),
            'low_quality_count': sum(1 for s in quality_scores if s < 0.4)
        }
    
    # Save report
    report_file = Path("data/raw/improved_output/scraping_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("IMPROVED SCRAPING COMPLETED")
    logger.info(f"{'='*60}")
    logger.info(f"Duration: {duration}")
    logger.info(f"Total content items: {total_content}")
    logger.info(f"News articles: {len(results['news'])}")
    
    for category, posts in results['forums'].items():
        logger.info(f"Forum {category}: {len(posts)} posts")
    
    if all_content:
        qs = report['quality_summary']
        logger.info(f"Quality - High: {qs['high_quality_count']}, Medium: {qs['medium_quality_count']}, Low: {qs['low_quality_count']}")
        logger.info(f"Average quality score: {qs['average_quality']:.3f}")
    
    logger.info(f"Report saved to: {report_file}")
    
    return results


def main():
    """Main execution function."""
    try:
        results = run_complete_improved_scraping()
        return results
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise


if __name__ == "__main__":
    main()