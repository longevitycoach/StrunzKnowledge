import logging
import os
from datetime import datetime
from typing import List, Dict
import json
from pathlib import Path

from .base_scraper import StrunzScraper
from .markdown_generator import MarkdownGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StrunzKnowledgeScraper:
    def __init__(self, output_dir: str = "data/raw"):
        self.scraper = StrunzScraper()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {}
        
    def scrape_all(self):
        """Scrape all sections of the Strunz website."""
        logger.info("Starting complete scraping process")
        
        # Scrape news
        logger.info("Scraping news section...")
        news_articles = self.scraper.scrape_news()
        self.stats['news'] = len(news_articles)
        self._save_data('news', news_articles)
        
        # Scrape forum categories
        forum_categories = [
            'fitness',
            'gesundheit',
            'ernaehrung',
            'bluttuning',
            'mental',
            'infektion-und-praevention'
        ]
        
        for category in forum_categories:
            logger.info(f"Scraping forum category: {category}")
            posts = self.scraper.scrape_forum(category)
            self.stats[f'forum_{category}'] = len(posts)
            self._save_data(f'forum_{category}', posts)
        
        # Log statistics
        logger.info("Scraping completed. Statistics:")
        total_items = 0
        for section, count in self.stats.items():
            logger.info(f"  {section}: {count} items")
            total_items += count
        logger.info(f"  Total: {total_items} items")
        
        # Save statistics
        self._save_statistics()
        
    def _save_data(self, section: str, data: List[Dict]):
        """Save scraped data to JSON file."""
        output_file = self.output_dir / f"{section}.json"
        
        # Convert datetime objects to strings
        for item in data:
            if item.get('date') and isinstance(item['date'], datetime):
                item['date'] = item['date'].isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(data)} items to {output_file}")
        
    def _save_statistics(self):
        """Save scraping statistics."""
        stats_file = self.output_dir / "scraping_stats.json"
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'sections': self.stats,
            'total': sum(self.stats.values())
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)


def main():
    """Main entry point for the scraper."""
    scraper = StrunzKnowledgeScraper()
    scraper.scrape_all()
    
    # Generate markdown files
    logger.info("Generating markdown files...")
    generator = MarkdownGenerator()
    generator.generate_all()
    
    logger.info("All tasks completed successfully!")


if __name__ == "__main__":
    main()