#!/usr/bin/env python3
"""
Scraping Manager - Production Ready
==================================

MCP-compliant scraping manager that coordinates all content extraction operations.
This is the main production interface for scraping strunz.com content.

Status: PRODUCTION
Usage: Called by main.py scrape command
Dependencies: src/scraper/production_scraper.py

Author: Claude Code
Last Updated: 2025-07-11
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from scraper.production_scraper import ProductionStrunzScraper

logger = logging.getLogger(__name__)


class ScrapingManager:
    """Production-ready scraping manager following MCP standards."""
    
    def __init__(self, 
                 unlimited: bool = False,
                 max_pages: Optional[int] = None,
                 use_selenium: bool = True,
                 forum_only: bool = False,
                 news_only: bool = False):
        """
        Initialize scraping manager.
        
        Args:
            unlimited: Remove all page limits
            max_pages: Maximum pages per category
            use_selenium: Use Selenium for JavaScript content
            forum_only: Scrape forums only
            news_only: Scrape news only
        """
        self.unlimited = unlimited
        self.max_pages = max_pages if not unlimited else None
        self.use_selenium = use_selenium
        self.forum_only = forum_only
        self.news_only = news_only
        
        # Setup output directories
        self.output_dir = Path("data/scraped")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ScrapingManager initialized:")
        logger.info(f"  Unlimited: {self.unlimited}")
        logger.info(f"  Max pages: {self.max_pages}")
        logger.info(f"  Use Selenium: {self.use_selenium}")
        logger.info(f"  Forum only: {self.forum_only}")
        logger.info(f"  News only: {self.news_only}")
    
    def run_test_scraping(self) -> Dict:
        """Run limited test scraping (max 2 pages per category)."""
        logger.info("🧪 Running test scraping with limited pages")
        
        scraper = ProductionStrunzScraper(
            use_selenium=self.use_selenium,
            max_pages_per_category=2,  # Always limit for tests
            min_content_score=0.3
        )
        
        try:
            results = scraper.run_complete_scraping()
            stats = scraper.get_statistics()
            
            # Save test results
            self._save_scraping_results(results, stats, "test")
            
            return {
                'status': 'success',
                'type': 'test',
                'total_items': self._count_total_items(results),
                'statistics': stats,
                'output_dir': str(self.output_dir)
            }
        
        except Exception as e:
            logger.error(f"Test scraping failed: {e}")
            return {
                'status': 'failed',
                'type': 'test',
                'error': str(e),
                'total_items': 0
            }
        finally:
            scraper.close()
    
    def run_production_scraping(self) -> Dict:
        """Run full production scraping."""
        if self.unlimited:
            logger.info("🚀 Running UNLIMITED production scraping")
        else:
            logger.info(f"🔄 Running limited production scraping (max {self.max_pages} pages)")
        
        scraper = ProductionStrunzScraper(
            use_selenium=self.use_selenium,
            max_pages_per_category=self.max_pages,
            min_content_score=0.4
        )
        
        try:
            if self.forum_only:
                results = self._scrape_forums_only(scraper)
            elif self.news_only:
                results = self._scrape_news_only(scraper)
            else:
                results = scraper.run_complete_scraping()
            
            stats = scraper.get_statistics()
            
            # Save production results
            self._save_scraping_results(results, stats, "production")
            
            return {
                'status': 'success',
                'type': 'production',
                'total_items': self._count_total_items(results),
                'statistics': stats,
                'output_dir': str(self.output_dir)
            }
        
        except Exception as e:
            logger.error(f"Production scraping failed: {e}")
            return {
                'status': 'failed',
                'type': 'production',
                'error': str(e),
                'total_items': 0
            }
        finally:
            scraper.close()
    
    def _scrape_forums_only(self, scraper: ProductionStrunzScraper) -> Dict:
        """Scrape forums only."""
        logger.info("📋 Scraping forums only")
        
        results = {'news': [], 'forums': {}}
        
        for category in scraper.FORUM_CATEGORIES.keys():
            logger.info(f"Scraping forum: {category}")
            try:
                posts = scraper.scrape_forum_complete(category)
                results['forums'][category] = posts
                logger.info(f"✅ {category}: {len(posts)} posts")
            except Exception as e:
                logger.error(f"❌ Failed to scrape {category}: {e}")
                results['forums'][category] = []
        
        return results
    
    def _scrape_news_only(self, scraper: ProductionStrunzScraper) -> Dict:
        """Scrape news only."""
        logger.info("📰 Scraping news only")
        
        try:
            news_articles = scraper.scrape_news_complete()
            logger.info(f"✅ News: {len(news_articles)} articles")
            return {'news': news_articles, 'forums': {}}
        except Exception as e:
            logger.error(f"❌ Failed to scrape news: {e}")
            return {'news': [], 'forums': {}}
    
    def _count_total_items(self, results: Dict) -> int:
        """Count total items in results."""
        total = len(results.get('news', []))
        for posts in results.get('forums', {}).values():
            total += len(posts)
        return total
    
    def _save_scraping_results(self, results: Dict, stats: Dict, run_type: str):
        """Save scraping results with comprehensive metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw results
        results_file = self.output_dir / f"{run_type}_scraping_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Save statistics
        stats_file = self.output_dir / f"{run_type}_statistics_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
        
        # Create summary report
        summary = {
            'run_type': run_type,
            'timestamp': timestamp,
            'configuration': {
                'unlimited': self.unlimited,
                'max_pages': self.max_pages,
                'use_selenium': self.use_selenium,
                'forum_only': self.forum_only,
                'news_only': self.news_only
            },
            'results_summary': {
                'total_items': self._count_total_items(results),
                'news_articles': len(results.get('news', [])),
                'forum_categories': len([cat for cat, posts in results.get('forums', {}).items() if posts]),
                'total_forum_posts': sum(len(posts) for posts in results.get('forums', {}).values())
            },
            'files_created': {
                'results': str(results_file),
                'statistics': str(stats_file)
            }
        }
        
        summary_file = self.output_dir / f"{run_type}_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Results saved:")
        logger.info(f"   Results: {results_file}")
        logger.info(f"   Statistics: {stats_file}")
        logger.info(f"   Summary: {summary_file}")
    
    def get_latest_results(self) -> Optional[Dict]:
        """Get the most recent scraping results."""
        result_files = list(self.output_dir.glob("*_scraping_*.json"))
        if not result_files:
            return None
        
        # Get most recent file
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load latest results from {latest_file}: {e}")
            return None