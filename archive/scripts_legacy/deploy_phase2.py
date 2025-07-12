#!/usr/bin/env python3
"""
Phase 2 Deployment: Complete unlimited scraping with full pagination crawling.

Features:
- Unlimited article extraction (no 50-article limit)
- Complete pagination crawling for all sections
- All 6 forum categories included
- Production-ready error handling and statistics
- Graceful interrupt handling
- Comprehensive logging and reporting
"""

import sys
import os
import json
import logging
import signal
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper.production_scraper import ProductionStrunzScraper

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'phase2_deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


class Phase2Deployment:
    """Phase 2 deployment manager for complete unlimited scraping."""
    
    def __init__(self, max_pages_per_category: int = None):
        """
        Initialize Phase 2 deployment.
        
        Args:
            max_pages_per_category: Maximum pages per category (None = unlimited)
        """
        self.max_pages_per_category = max_pages_per_category
        self.deployment_start = datetime.now()
        self.results = {}
        self.interrupted = False
        
        # Create output directories
        self.output_dir = Path("data/phase2_deployment")
        self.create_output_structure()
        
        # Setup interrupt handling
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        logger.info("\n🛑 DEPLOYMENT INTERRUPTED - Saving current progress...")
        self.interrupted = True
    
    def create_output_structure(self):
        """Create comprehensive output directory structure."""
        directories = [
            self.output_dir,
            self.output_dir / "raw_data",
            self.output_dir / "processed_data", 
            self.output_dir / "news",
            self.output_dir / "forums",
            self.output_dir / "forums" / "fitness",
            self.output_dir / "forums" / "gesundheit",
            self.output_dir / "forums" / "ernährung", 
            self.output_dir / "forums" / "bluttuning",
            self.output_dir / "forums" / "mental",
            self.output_dir / "forums" / "infektion_prävention",
            self.output_dir / "reports",
            self.output_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def save_category_data(self, category: str, data: list, data_type: str = "forum"):
        """Save category data in multiple formats."""
        if not data:
            logger.warning(f"⚠️  No data to save for {category}")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine save directory
        if data_type == "news":
            save_dir = self.output_dir / "news"
        else:
            save_dir = self.output_dir / "forums" / category
        
        # Save JSON data
        json_file = save_dir / f"{category}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate summary statistics
        quality_scores = [item.get('quality_score', 0) for item in data if 'quality_score' in item]
        word_counts = [len(item.get('content', '').split()) for item in data]
        
        summary = {
            'category': category,
            'data_type': data_type,
            'timestamp': timestamp,
            'total_items': len(data),
            'average_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
            'total_words': sum(word_counts),
            'quality_distribution': {
                'high': len([s for s in quality_scores if s >= 0.7]),
                'medium': len([s for s in quality_scores if 0.4 <= s < 0.7]),
                'low': len([s for s in quality_scores if s < 0.4])
            } if quality_scores else None,
            'sample_titles': [item.get('title', 'Untitled')[:50] for item in data[:5]]
        }
        
        # Save summary
        summary_file = save_dir / f"{category}_{timestamp}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(data)} items for {category} to {json_file}")
        logger.info(f"📊 Summary: Avg words={summary['average_word_count']:.0f}, Total words={summary['total_words']}")
    
    def run_unlimited_scraping(self):
        """Execute unlimited scraping for all categories."""
        logger.info("🚀 STARTING PHASE 2: UNLIMITED DEPLOYMENT")
        logger.info("=" * 80)
        logger.info(f"📅 Start time: {self.deployment_start}")
        logger.info(f"🔄 Max pages per category: {self.max_pages_per_category or 'UNLIMITED'}")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info("=" * 80)
        
        # Initialize production scraper
        scraper = ProductionStrunzScraper(
            use_selenium=True,
            delay=1.5,
            max_pages_per_category=self.max_pages_per_category,
            min_content_score=0.3  # Lower threshold for more content
        )
        
        try:
            # Run complete scraping
            logger.info("🎯 Launching complete unlimited scraping...")
            self.results = scraper.run_complete_scraping()
            
            # Save results as they're generated
            if not self.interrupted:
                self._save_all_results()
            
        except KeyboardInterrupt:
            logger.info("⏹️  Scraping interrupted by user")
            self.interrupted = True
        except Exception as e:
            logger.error(f"❌ Critical error during deployment: {e}")
            raise
        finally:
            # Get final statistics
            stats = scraper.get_statistics()
            self._generate_deployment_report(stats)
            scraper.close()
    
    def _save_all_results(self):
        """Save all scraping results."""
        logger.info("💾 Saving all scraping results...")
        
        # Save news
        if self.results.get('news'):
            self.save_category_data('news', self.results['news'], 'news')
        
        # Save forum data
        for category, posts in self.results.get('forums', {}).items():
            if posts:
                self.save_category_data(category, posts, 'forum')
    
    def _generate_deployment_report(self, stats: dict):
        """Generate comprehensive deployment report."""
        deployment_end = datetime.now()
        deployment_duration = deployment_end - self.deployment_start
        
        # Calculate totals
        total_content = len(self.results.get('news', []))
        forum_totals = {}
        
        for category, posts in self.results.get('forums', {}).items():
            forum_totals[category] = len(posts)
            total_content += len(posts)
        
        # Generate comprehensive report
        report = {
            'deployment_info': {
                'phase': 'Phase 2 - Unlimited Deployment',
                'start_time': self.deployment_start.isoformat(),
                'end_time': deployment_end.isoformat(),
                'duration': str(deployment_duration),
                'interrupted': self.interrupted,
                'max_pages_per_category': self.max_pages_per_category
            },
            'scraping_statistics': stats,
            'content_summary': {
                'total_content_items': total_content,
                'news_articles': len(self.results.get('news', [])),
                'forum_posts_by_category': forum_totals,
                'total_forum_posts': sum(forum_totals.values()),
                'categories_processed': len([cat for cat, posts in self.results.get('forums', {}).items() if posts])
            },
            'performance_metrics': {
                'pages_per_minute': stats.get('total_pages_visited', 0) / (deployment_duration.total_seconds() / 60) if deployment_duration.total_seconds() > 0 else 0,
                'content_per_minute': total_content / (deployment_duration.total_seconds() / 60) if deployment_duration.total_seconds() > 0 else 0,
                'success_rate': (1 - (stats.get('errors_encountered', 0) / max(stats.get('total_pages_visited', 1), 1))) * 100
            },
            'quality_analysis': self._analyze_content_quality(),
            'next_steps': [
                "Process content through Docling for enhanced text extraction",
                "Build FAISS vector database for semantic search",
                "Test MCP server with real content",
                "Deploy to production environment"
            ]
        }
        
        # Save report
        report_file = self.output_dir / "reports" / f"phase2_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate human-readable summary
        self._print_deployment_summary(report)
        
        logger.info(f"📋 Complete deployment report saved to: {report_file}")
    
    def _analyze_content_quality(self) -> dict:
        """Analyze overall content quality across all categories."""
        all_content = []
        
        # Collect all content
        all_content.extend(self.results.get('news', []))
        for posts in self.results.get('forums', {}).values():
            all_content.extend(posts)
        
        if not all_content:
            return {}
        
        # Calculate quality metrics
        word_counts = [len(item.get('content', '').split()) for item in all_content]
        char_counts = [len(item.get('content', '')) for item in all_content]
        
        return {
            'total_items_analyzed': len(all_content),
            'average_word_count': sum(word_counts) / len(word_counts),
            'average_char_count': sum(char_counts) / len(char_counts),
            'word_count_distribution': {
                'excellent_content': len([w for w in word_counts if w >= 200]),
                'good_content': len([w for w in word_counts if 100 <= w < 200]),
                'acceptable_content': len([w for w in word_counts if 50 <= w < 100]),
                'short_content': len([w for w in word_counts if w < 50])
            },
            'content_variety': {
                'news_articles': len(self.results.get('news', [])),
                'forum_categories': len([cat for cat, posts in self.results.get('forums', {}).items() if posts])
            }
        }
    
    def _print_deployment_summary(self, report: dict):
        """Print human-readable deployment summary."""
        print("\n" + "=" * 80)
        print("🎉 PHASE 2 DEPLOYMENT COMPLETED")
        print("=" * 80)
        
        # Deployment info
        deployment = report['deployment_info']
        print(f"⏱️  Duration: {deployment['duration']}")
        print(f"🔄 Max pages per category: {deployment['max_pages_per_category'] or 'UNLIMITED'}")
        print(f"⚠️  Interrupted: {deployment['interrupted']}")
        
        # Content summary
        content = report['content_summary']
        print(f"\n📊 CONTENT SUMMARY")
        print(f"   Total content items: {content['total_content_items']}")
        print(f"   News articles: {content['news_articles']}")
        print(f"   Total forum posts: {content['total_forum_posts']}")
        print(f"   Categories processed: {content['categories_processed']}/6")
        
        # Forum breakdown
        print(f"\n📋 FORUM BREAKDOWN")
        for category, count in content['forum_posts_by_category'].items():
            print(f"   {category.capitalize()}: {count} posts")
        
        # Performance metrics
        perf = report['performance_metrics']
        print(f"\n⚡ PERFORMANCE METRICS")
        print(f"   Pages per minute: {perf['pages_per_minute']:.1f}")
        print(f"   Content per minute: {perf['content_per_minute']:.1f}")
        print(f"   Success rate: {perf['success_rate']:.1f}%")
        
        # Quality analysis
        if 'quality_analysis' in report and report['quality_analysis']:
            quality = report['quality_analysis']
            print(f"\n🎯 QUALITY ANALYSIS")
            print(f"   Average word count: {quality['average_word_count']:.0f}")
            print(f"   Excellent content (≥200 words): {quality['word_count_distribution']['excellent_content']}")
            print(f"   Good content (100-199 words): {quality['word_count_distribution']['good_content']}")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS")
        for step in report['next_steps']:
            print(f"   • {step}")
        
        print("=" * 80)
    
    def run_test_deployment(self, max_pages: int = 2):
        """Run limited test deployment for validation."""
        logger.info(f"🧪 RUNNING TEST DEPLOYMENT (max {max_pages} pages per category)")
        self.max_pages_per_category = max_pages
        self.run_unlimited_scraping()
    
    def run_full_deployment(self):
        """Run full unlimited deployment."""
        logger.info("🚀 RUNNING FULL UNLIMITED DEPLOYMENT")
        self.max_pages_per_category = None  # Unlimited
        self.run_unlimited_scraping()


def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2 Deployment: Complete unlimited scraping")
    parser.add_argument('--test', action='store_true', help='Run test deployment with limited pages')
    parser.add_argument('--max-pages', type=int, default=None, help='Maximum pages per category (for testing)')
    parser.add_argument('--full', action='store_true', help='Run full unlimited deployment')
    
    args = parser.parse_args()
    
    deployment = Phase2Deployment()
    
    try:
        if args.test:
            max_pages = args.max_pages or 2
            deployment.run_test_deployment(max_pages)
        elif args.full:
            deployment.run_full_deployment()
        else:
            # Default: prompt user for choice
            print("Phase 2 Deployment Options:")
            print("1. Test deployment (2 pages per category)")
            print("2. Limited deployment (specify max pages)")
            print("3. Full unlimited deployment")
            
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                deployment.run_test_deployment(2)
            elif choice == "2":
                max_pages = int(input("Enter max pages per category: "))
                deployment.max_pages_per_category = max_pages
                deployment.run_unlimited_scraping()
            elif choice == "3":
                deployment.run_full_deployment()
            else:
                print("Invalid choice. Running test deployment.")
                deployment.run_test_deployment(2)
    
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise


if __name__ == "__main__":
    main()