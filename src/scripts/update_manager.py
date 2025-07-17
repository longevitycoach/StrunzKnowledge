#!/usr/bin/env python3
"""
Comprehensive Update Manager for StrunzKnowledge
===============================================

This script implements a complete update process including:
1. Test scraping before production
2. Incremental updates (news-only, forum-only)
3. Output monitoring and logging
4. Forum structure analysis
5. FAISS index rebuilding
6. Automated update detection

Usage:
    python src/scripts/update_manager.py test-news
    python src/scripts/update_manager.py test-forums
    python src/scripts/update_manager.py update-news
    python src/scripts/update_manager.py update-forums
    python src/scripts/update_manager.py full-update
    python src/scripts/update_manager.py analyze-forums
    python src/scripts/update_manager.py rebuild-indices

Author: Claude Code
Created: 2025-07-16
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import shutil
import subprocess
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scraping_manager import ScrapingManager
from scripts.check_new_content import ContentChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/update_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UpdateManager:
    """Comprehensive update manager for StrunzKnowledge."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.scraped_dir = self.data_dir / "scraped"
        self.indices_dir = self.data_dir / "faiss_indices"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.scraped_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.content_checker = ContentChecker()
        
        logger.info("UpdateManager initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Data directory: {self.data_dir}")
    
    def run_test_scraping(self, content_type: str = "all") -> Dict:
        """Run test scraping with limited pages."""
        logger.info(f"🧪 Starting test scraping for: {content_type}")
        
        # Configure scraping based on content type
        if content_type == "news":
            manager = ScrapingManager(max_pages=2, news_only=True)
        elif content_type == "forums":
            manager = ScrapingManager(max_pages=2, forum_only=True)
        else:
            manager = ScrapingManager(max_pages=2)
        
        # Run test scraping
        results = manager.run_test_scraping()
        
        # Log results
        self._log_scraping_results(results, "test", content_type)
        
        return results
    
    def run_production_update(self, content_type: str = "all", unlimited: bool = False) -> Dict:
        """Run production update with proper testing first."""
        logger.info(f"🚀 Starting production update for: {content_type}")
        
        # Step 1: Run test scraping first
        logger.info("Step 1: Running test scraping...")
        test_results = self.run_test_scraping(content_type)
        
        if test_results['status'] != 'success':
            logger.error("Test scraping failed! Aborting production update.")
            return test_results
        
        logger.info(f"✅ Test scraping successful: {test_results['total_items']} items")
        
        # Step 2: Check if production update is needed
        if not self._should_run_production_update(test_results):
            logger.info("No significant changes detected. Skipping production update.")
            return {
                'status': 'skipped',
                'reason': 'No significant changes detected',
                'test_results': test_results
            }
        
        # Step 3: Run production scraping
        logger.info("Step 2: Running production scraping...")
        
        if content_type == "news":
            manager = ScrapingManager(unlimited=unlimited, news_only=True)
        elif content_type == "forums":
            manager = ScrapingManager(unlimited=unlimited, forum_only=True)
        else:
            manager = ScrapingManager(unlimited=unlimited)
        
        production_results = manager.run_production_scraping()
        
        # Log results
        self._log_scraping_results(production_results, "production", content_type)
        
        if production_results['status'] != 'success':
            logger.error("Production scraping failed!")
            return production_results
        
        # Step 4: Process and integrate new content
        logger.info("Step 3: Processing new content...")
        processing_results = self._process_new_content(production_results)
        
        # Step 5: Rebuild FAISS indices if needed
        if processing_results['should_rebuild_indices']:
            logger.info("Step 4: Rebuilding FAISS indices...")
            index_results = self.rebuild_faiss_indices()
            production_results['index_rebuild'] = index_results
        
        # Step 6: Cleanup and final logging
        self._cleanup_old_files()
        self._generate_update_report(production_results, processing_results)
        
        logger.info("✅ Production update completed successfully!")
        return production_results
    
    def analyze_forum_structure(self) -> Dict:
        """Analyze current forum structure to update scrapers."""
        logger.info("🔍 Analyzing forum structure...")
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'recommendations': [],
            'issues_found': []
        }
        
        # Test each forum category
        forum_categories = {
            'fitness': 'fitness',
            'gesundheit': 'gesundheit', 
            'ernährung': 'ernaehrung',
            'bluttuning': 'bluttuning',
            'mental': 'mental',
            'infektion_prävention': 'infektion-und-praevention'
        }
        
        for category, url_name in forum_categories.items():
            logger.info(f"Analyzing forum category: {category}")
            
            try:
                # Import here to avoid circular imports
                from scraper.production_scraper import ProductionStrunzScraper
                
                scraper = ProductionStrunzScraper(max_pages_per_category=1)
                base_url = f"https://www.strunz.com/forum/{url_name}"
                
                # Get page content
                soup = scraper._get_page_content(base_url)
                
                if soup:
                    # Analyze page structure
                    thread_links = scraper._extract_forum_thread_links(soup, url_name)
                    pagination_links = scraper._extract_pagination_urls(soup, base_url)
                    
                    analysis_results['categories'][category] = {
                        'url': base_url,
                        'accessible': True,
                        'thread_links_found': len(thread_links),
                        'pagination_links_found': len(pagination_links),
                        'sample_thread_links': thread_links[:3],
                        'sample_pagination_links': pagination_links[:3]
                    }
                    
                    # Check for issues
                    if len(thread_links) == 0:
                        analysis_results['issues_found'].append(f"No thread links found for {category}")
                    
                    if len(pagination_links) == 0:
                        analysis_results['recommendations'].append(f"Consider checking pagination for {category}")
                
                else:
                    analysis_results['categories'][category] = {
                        'url': base_url,
                        'accessible': False,
                        'error': 'Could not load page'
                    }
                    analysis_results['issues_found'].append(f"Cannot access {category} forum")
                
                scraper.close()
                
            except Exception as e:
                logger.error(f"Error analyzing {category}: {e}")
                analysis_results['categories'][category] = {
                    'url': base_url,
                    'accessible': False,
                    'error': str(e)
                }
                analysis_results['issues_found'].append(f"Error analyzing {category}: {str(e)}")
        
        # Save analysis results
        analysis_file = self.logs_dir / f"forum_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Forum analysis saved to: {analysis_file}")
        
        # Print summary
        accessible_count = sum(1 for cat in analysis_results['categories'].values() if cat.get('accessible', False))
        total_count = len(analysis_results['categories'])
        
        logger.info(f"Forum Analysis Summary:")
        logger.info(f"  Accessible categories: {accessible_count}/{total_count}")
        logger.info(f"  Issues found: {len(analysis_results['issues_found'])}")
        logger.info(f"  Recommendations: {len(analysis_results['recommendations'])}")
        
        return analysis_results
    
    def rebuild_faiss_indices(self) -> Dict:
        """Rebuild FAISS indices from processed content."""
        logger.info("🔄 Rebuilding FAISS indices...")
        
        rebuild_results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'started',
            'steps': [],
            'errors': []
        }
        
        try:
            # Step 1: Backup existing indices
            logger.info("Step 1: Backing up existing indices...")
            backup_dir = self.indices_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if self.indices_dir.exists():
                shutil.copytree(self.indices_dir, backup_dir)
                rebuild_results['steps'].append(f"Backed up indices to {backup_dir}")
            
            # Step 2: Check for processed content
            processed_dir = self.data_dir / "processed"
            if not processed_dir.exists():
                raise ValueError("No processed content found. Run content processing first.")
            
            # Step 3: Run index building script
            logger.info("Step 2: Building new indices...")
            
            # Check if we have the index building script
            index_script = self.project_root / "src" / "scripts" / "data" / "build_indices.py"
            if not index_script.exists():
                # Create a basic index building script
                self._create_index_building_script()
            
            # Run the index building process
            result = subprocess.run([
                sys.executable, str(index_script)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                rebuild_results['steps'].append("Index building completed successfully")
                rebuild_results['status'] = 'success'
                logger.info("✅ FAISS indices rebuilt successfully")
            else:
                rebuild_results['errors'].append(f"Index building failed: {result.stderr}")
                rebuild_results['status'] = 'failed'
                logger.error(f"❌ Index building failed: {result.stderr}")
            
            # Step 4: Validate new indices
            logger.info("Step 3: Validating new indices...")
            validation_results = self._validate_indices()
            rebuild_results['validation'] = validation_results
            
            if validation_results['valid']:
                logger.info("✅ Index validation passed")
            else:
                logger.warning("⚠️ Index validation issues found")
                rebuild_results['errors'].extend(validation_results['errors'])
        
        except Exception as e:
            logger.error(f"❌ Error rebuilding indices: {e}")
            rebuild_results['status'] = 'failed'
            rebuild_results['errors'].append(str(e))
        
        # Save rebuild results
        rebuild_file = self.logs_dir / f"index_rebuild_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rebuild_file, 'w', encoding='utf-8') as f:
            json.dump(rebuild_results, f, indent=2, ensure_ascii=False)
        
        return rebuild_results
    
    def check_for_updates(self) -> Dict:
        """Check if updates are needed."""
        logger.info("🔍 Checking for updates...")
        
        check_results = {
            'timestamp': datetime.now().isoformat(),
            'updates_needed': False,
            'reasons': [],
            'recommendations': []
        }
        
        # Check using content checker
        if self.content_checker.needs_update():
            check_results['updates_needed'] = True
            check_results['reasons'].append("Content checker detected changes")
        
        # Check time since last update
        last_update = self._get_last_update_time()
        if last_update and (datetime.now() - last_update).days > 7:
            check_results['updates_needed'] = True
            check_results['reasons'].append("More than 7 days since last update")
        
        # Check index health
        index_health = self._check_index_health()
        if not index_health['healthy']:
            check_results['updates_needed'] = True
            check_results['reasons'].append("Index health issues detected")
            check_results['recommendations'].append("Consider rebuilding indices")
        
        # Generate recommendations
        if check_results['updates_needed']:
            check_results['recommendations'].append("Run: python src/scripts/update_manager.py test-news")
            check_results['recommendations'].append("Run: python src/scripts/update_manager.py test-forums")
        
        logger.info(f"Update check complete: {'Updates needed' if check_results['updates_needed'] else 'No updates needed'}")
        
        return check_results
    
    def _should_run_production_update(self, test_results: Dict) -> bool:
        """Determine if production update should run based on test results."""
        if test_results['status'] != 'success':
            return False
        
        # Check if we found significant new content
        min_items_threshold = 5
        if test_results['total_items'] < min_items_threshold:
            return False
        
        # Check time since last production update
        last_production = self._get_last_production_update()
        if last_production and (datetime.now() - last_production).hours < 1:
            return False
        
        return True
    
    def _process_new_content(self, scraping_results: Dict) -> Dict:
        """Process newly scraped content."""
        logger.info("Processing new content...")
        
        processing_results = {
            'new_items_processed': 0,
            'should_rebuild_indices': False,
            'processing_errors': []
        }
        
        try:
            # Count new items
            news_count = len(scraping_results.get('news', []))
            forum_count = sum(len(posts) for posts in scraping_results.get('forums', {}).values())
            total_new = news_count + forum_count
            
            processing_results['new_items_processed'] = total_new
            
            # Determine if we should rebuild indices
            if total_new > 10:  # Threshold for rebuilding
                processing_results['should_rebuild_indices'] = True
                logger.info(f"Found {total_new} new items - scheduling index rebuild")
            
        except Exception as e:
            processing_results['processing_errors'].append(str(e))
            logger.error(f"Error processing new content: {e}")
        
        return processing_results
    
    def _validate_indices(self) -> Dict:
        """Validate FAISS indices."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check if index files exist
            index_files = [
                self.indices_dir / "combined_index.faiss",
                self.indices_dir / "combined_metadata.json"
            ]
            
            for index_file in index_files:
                if not index_file.exists():
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Missing index file: {index_file}")
            
            # Try to load the index
            if validation_results['valid']:
                try:
                    from src.rag.search import get_vector_store_singleton
                    vector_store = get_vector_store_singleton()
                    if hasattr(vector_store, 'documents') and len(vector_store.documents) == 0:
                        validation_results['warnings'].append("Vector store loaded but contains no documents")
                except Exception as e:
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Error loading vector store: {e}")
        
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Validation error: {e}")
        
        return validation_results
    
    def _check_index_health(self) -> Dict:
        """Check health of current indices."""
        health_results = {
            'healthy': True,
            'issues': [],
            'last_modified': None
        }
        
        try:
            index_file = self.indices_dir / "combined_index.faiss"
            if index_file.exists():
                health_results['last_modified'] = datetime.fromtimestamp(index_file.stat().st_mtime)
                
                # Check if index is very old
                if (datetime.now() - health_results['last_modified']).days > 14:
                    health_results['healthy'] = False
                    health_results['issues'].append("Index is older than 14 days")
            else:
                health_results['healthy'] = False
                health_results['issues'].append("Index file does not exist")
        
        except Exception as e:
            health_results['healthy'] = False
            health_results['issues'].append(f"Error checking index health: {e}")
        
        return health_results
    
    def _get_last_update_time(self) -> Optional[datetime]:
        """Get timestamp of last update."""
        try:
            update_files = list(self.scraped_dir.glob("production_scraping_*.json"))
            if update_files:
                latest_file = max(update_files, key=lambda f: f.stat().st_mtime)
                return datetime.fromtimestamp(latest_file.stat().st_mtime)
        except:
            pass
        return None
    
    def _get_last_production_update(self) -> Optional[datetime]:
        """Get timestamp of last production update."""
        return self._get_last_update_time()
    
    def _cleanup_old_files(self):
        """Clean up old scraping files."""
        logger.info("Cleaning up old files...")
        
        # Keep only last 10 scraping results
        for pattern in ["*_scraping_*.json", "*_statistics_*.json", "*_summary_*.json"]:
            files = list(self.scraped_dir.glob(pattern))
            if len(files) > 10:
                files.sort(key=lambda f: f.stat().st_mtime)
                for old_file in files[:-10]:
                    old_file.unlink()
                    logger.info(f"Removed old file: {old_file}")
    
    def _generate_update_report(self, production_results: Dict, processing_results: Dict):
        """Generate comprehensive update report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'update_type': 'production',
            'production_results': production_results,
            'processing_results': processing_results,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if production_results['status'] == 'success':
            report['recommendations'].append("Update completed successfully")
        else:
            report['recommendations'].append("Update failed - check logs for details")
        
        if processing_results['should_rebuild_indices']:
            report['recommendations'].append("FAISS indices were rebuilt")
        
        # Save report
        report_file = self.logs_dir / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Update report saved to: {report_file}")
    
    def _log_scraping_results(self, results: Dict, run_type: str, content_type: str):
        """Log scraping results."""
        if results['status'] == 'success':
            logger.info(f"✅ {run_type.title()} {content_type} scraping completed:")
            logger.info(f"   Total items: {results['total_items']}")
            logger.info(f"   Output directory: {results['output_dir']}")
        else:
            logger.error(f"❌ {run_type.title()} {content_type} scraping failed:")
            logger.error(f"   Error: {results.get('error', 'Unknown error')}")
    
    def _create_index_building_script(self):
        """Create a basic index building script if it doesn't exist."""
        script_content = '''#!/usr/bin/env python3
"""
Basic FAISS Index Builder
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Build FAISS indices from processed content."""
    print("Building FAISS indices...")
    
    try:
        # Import and run index building
        from src.rag.vector_store import FAISSVectorStore
        
        # Create vector store (this will build indices)
        vector_store = FAISSVectorStore()
        
        print(f"✅ Indices built successfully!")
        print(f"   Documents: {len(vector_store.documents)}")
        
    except Exception as e:
        print(f"❌ Error building indices: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        script_path = self.project_root / "src" / "scripts" / "data" / "build_indices.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        script_path.chmod(0o755)
        
        logger.info(f"Created index building script: {script_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="StrunzKnowledge Update Manager")
    parser.add_argument('action', choices=[
        'test-news', 'test-forums', 'test-all',
        'update-news', 'update-forums', 'full-update',
        'analyze-forums', 'rebuild-indices', 'check-updates'
    ], help='Action to perform')
    parser.add_argument('--unlimited', action='store_true', help='Run unlimited scraping')
    parser.add_argument('--force', action='store_true', help='Force update even if not needed')
    
    args = parser.parse_args()
    
    # Initialize update manager
    update_manager = UpdateManager()
    
    try:
        if args.action == 'test-news':
            result = update_manager.run_test_scraping('news')
        elif args.action == 'test-forums':
            result = update_manager.run_test_scraping('forums')
        elif args.action == 'test-all':
            result = update_manager.run_test_scraping('all')
        elif args.action == 'update-news':
            result = update_manager.run_production_update('news', args.unlimited)
        elif args.action == 'update-forums':
            result = update_manager.run_production_update('forums', args.unlimited)
        elif args.action == 'full-update':
            result = update_manager.run_production_update('all', args.unlimited)
        elif args.action == 'analyze-forums':
            result = update_manager.analyze_forum_structure()
        elif args.action == 'rebuild-indices':
            result = update_manager.rebuild_faiss_indices()
        elif args.action == 'check-updates':
            result = update_manager.check_for_updates()
        
        # Print final status
        if result.get('status') == 'success':
            print("\n✅ Operation completed successfully!")
        elif result.get('status') == 'failed':
            print("\n❌ Operation failed!")
            sys.exit(1)
        else:
            print(f"\n📊 Operation completed with status: {result.get('status', 'unknown')}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()