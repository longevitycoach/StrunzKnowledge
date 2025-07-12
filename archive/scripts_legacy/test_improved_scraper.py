#!/usr/bin/env python3
"""
Test script for the improved Strunz scraper with Selenium support.
"""

import sys
import os
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
        logging.FileHandler('improved_scraper_test.log')
    ]
)

logger = logging.getLogger(__name__)


def test_content_quality_assessment():
    """Test the content quality assessment system."""
    scraper = ImprovedStrunzScraper()
    
    test_cases = [
        {
            'content': 'Das ist ein sehr kurzer Text.',
            'expected_low': True,
            'description': 'Short content'
        },
        {
            'content': '''
            Die Omega-3-Fettsäuren sind essentiell für die Gesundheit. Studien zeigen, dass eine ausreichende 
            Versorgung mit EPA und DHA wichtig für das Herz-Kreislauf-System ist. Besonders in der Prävention 
            von Herzkrankheiten spielen diese Fettsäuren eine wichtige Rolle. Forschungen haben gezeigt, dass 
            Menschen mit höheren Omega-3-Spiegeln im Blut ein geringeres Risiko für Herzinfarkte haben.
            ''',
            'expected_low': False,
            'description': 'High-quality health content'
        },
        {
            'content': 'Klicken Sie hier für mehr Informationen. Newsletter abonnieren. Cookie akzeptieren.',
            'expected_low': True,
            'description': 'Navigation/promotional content'
        }
    ]
    
    logger.info("Testing content quality assessment...")
    
    for i, test_case in enumerate(test_cases, 1):
        quality = scraper._assess_content_quality(test_case['content'])
        is_low_quality = quality.score < scraper.min_content_score
        
        logger.info(f"Test {i} ({test_case['description']}):")
        logger.info(f"  Content: {test_case['content'][:50]}...")
        logger.info(f"  Quality score: {quality.score:.2f}")
        logger.info(f"  Word count: {quality.word_count}")
        logger.info(f"  Is meaningful: {quality.is_meaningful}")
        logger.info(f"  Expected low quality: {test_case['expected_low']}, Got: {is_low_quality}")
        
        if test_case['expected_low'] == is_low_quality:
            logger.info("  ✅ PASS")
        else:
            logger.warning("  ❌ FAIL")
        logger.info("")
    
    scraper.close()


def test_forum_scraping():
    """Test forum scraping with different categories."""
    scraper = ImprovedStrunzScraper(use_selenium=True, delay=2.0)
    
    # Test categories
    categories = ['fitness', 'gesundheit', 'ernährung']
    
    for category in categories:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing forum scraping for category: {category}")
        logger.info(f"{'='*50}")
        
        try:
            posts = scraper.scrape_forum(category)
            
            logger.info(f"Results for {category}:")
            logger.info(f"  Total posts scraped: {len(posts)}")
            
            if posts:
                # Analyze quality distribution
                high_quality = [p for p in posts if p.get('quality_score', 0) >= 0.7]
                medium_quality = [p for p in posts if 0.4 <= p.get('quality_score', 0) < 0.7]
                low_quality = [p for p in posts if p.get('quality_score', 0) < 0.4]
                
                logger.info(f"  High quality (≥0.7): {len(high_quality)}")
                logger.info(f"  Medium quality (0.4-0.7): {len(medium_quality)}")
                logger.info(f"  Low quality (<0.4): {len(low_quality)}")
                
                # Show sample posts
                for i, post in enumerate(posts[:3], 1):
                    logger.info(f"  Sample post {i}:")
                    logger.info(f"    Title: {post.get('title', 'N/A')[:50]}...")
                    logger.info(f"    Author: {post.get('author', 'N/A')}")
                    logger.info(f"    Content length: {len(post.get('content', ''))}")
                    logger.info(f"    Quality score: {post.get('quality_score', 0):.2f}")
                    logger.info(f"    Word count: {post.get('word_count', 0)}")
            else:
                logger.warning(f"  No posts found for {category}")
        
        except Exception as e:
            logger.error(f"Error scraping {category}: {e}")
        
        logger.info("")
    
    scraper.close()


def test_news_scraping():
    """Test improved news scraping."""
    scraper = ImprovedStrunzScraper(use_selenium=False, delay=1.0)  # News doesn't need Selenium
    
    logger.info(f"\n{'='*50}")
    logger.info("Testing improved news scraping")
    logger.info(f"{'='*50}")
    
    try:
        articles = scraper.scrape_news()
        
        logger.info(f"Results for news:")
        logger.info(f"  Total articles scraped: {len(articles)}")
        
        if articles:
            # Analyze quality distribution
            excellent = [a for a in articles if a.get('quality_score', 0) >= 0.8]
            good = [a for a in articles if 0.6 <= a.get('quality_score', 0) < 0.8]
            fair = [a for a in articles if 0.4 <= a.get('quality_score', 0) < 0.6]
            poor = [a for a in articles if a.get('quality_score', 0) < 0.4]
            
            logger.info(f"  Excellent quality (≥0.8): {len(excellent)}")
            logger.info(f"  Good quality (0.6-0.8): {len(good)}")
            logger.info(f"  Fair quality (0.4-0.6): {len(fair)}")
            logger.info(f"  Poor quality (<0.4): {len(poor)}")
            
            # Show sample articles
            for i, article in enumerate(articles[:5], 1):
                logger.info(f"  Sample article {i}:")
                logger.info(f"    Title: {article.get('title', 'N/A')[:60]}...")
                logger.info(f"    Author: {article.get('author', 'N/A')}")
                logger.info(f"    Date: {article.get('date', 'N/A')}")
                logger.info(f"    Content length: {len(article.get('content', ''))}")
                logger.info(f"    Quality score: {article.get('quality_score', 0):.2f}")
                logger.info(f"    Word count: {article.get('word_count', 0)}")
        else:
            logger.warning("  No articles found")
    
    except Exception as e:
        logger.error(f"Error scraping news: {e}")
    
    scraper.close()


def main():
    """Run all tests."""
    logger.info("Starting improved scraper tests...")
    logger.info(f"Test started at: {datetime.now()}")
    
    try:
        # Test content quality assessment
        test_content_quality_assessment()
        
        # Test news scraping (faster, no Selenium needed)
        test_news_scraping()
        
        # Test forum scraping (requires Selenium)
        logger.info("\nStarting forum scraping tests (requires Chrome WebDriver)...")
        test_forum_scraping()
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        logger.info(f"Test completed at: {datetime.now()}")


if __name__ == "__main__":
    main()