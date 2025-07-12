#!/usr/bin/env python3
"""
StrunzKnowledge Main Entry Point
===============================

MCP (Model Context Protocol) compliant main entry point for the StrunzKnowledge application.
This file serves as the primary interface for all StrunzKnowledge operations.

Usage:
    python main.py [command] [options]

Commands:
    scrape      - Run content scraping operations
    process     - Process content through Docling OCR
    vector      - Build and manage FAISS vector database
    mcp         - Start MCP server
    analyze     - Analyze scraped content
    test        - Run test suites

Examples:
    python main.py scrape --news --unlimited
    python main.py process --input data/raw --output data/processed
    python main.py mcp --port 8000
    python main.py analyze --generate-report

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
MCP Compliance: Model Context Protocol 2025-06-18
Specification: https://modelcontextprotocol.io/specification/2025-06-18
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src to Python path for MCP compliance
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configure logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup centralized logging for MCP compliance."""
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"strunz_knowledge_{timestamp}.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    
    logger = logging.getLogger("StrunzKnowledge")
    logger.info(f"StrunzKnowledge initialized - Log file: {log_file}")
    return logger


def cmd_scrape(args, logger):
    """Execute scraping operations."""
    logger.info("🕷️  Starting scraping operations")
    
    from scripts.scraping_manager import ScrapingManager
    
    manager = ScrapingManager(
        unlimited=args.unlimited,
        max_pages=args.max_pages,
        use_selenium=args.selenium,
        forum_only=args.forum_only,
        news_only=args.news_only
    )
    
    if args.test:
        logger.info("Running test scraping (limited)")
        results = manager.run_test_scraping()
    else:
        logger.info("Running production scraping")
        results = manager.run_production_scraping()
    
    logger.info(f"Scraping completed: {results.get('total_items', 0)} items")
    return results


def main():
    """Main entry point following MCP standards."""
    parser = argparse.ArgumentParser(
        description="StrunzKnowledge - Comprehensive Dr. Strunz Knowledge Base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape --unlimited --news              # Unlimited news scraping
  %(prog)s scrape --forum-only --max-pages 5     # Limited forum scraping
  %(prog)s analyze --generate-report              # Generate analysis

For more information, visit: https://github.com/longevitycoach/StrunzKnowledge
        """
    )
    
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scraping command
    scrape_parser = subparsers.add_parser('scrape', help='Run content scraping')
    scrape_parser.add_argument('--unlimited', action='store_true', help='Unlimited scraping (no page limits)')
    scrape_parser.add_argument('--max-pages', type=int, help='Maximum pages per category')
    scrape_parser.add_argument('--selenium', action='store_true', default=True, help='Use Selenium for JS content')
    scrape_parser.add_argument('--forum-only', action='store_true', help='Scrape forums only')
    scrape_parser.add_argument('--news-only', action='store_true', help='Scrape news only')
    scrape_parser.add_argument('--test', action='store_true', help='Run test scraping (limited)')
    
    # Analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze content and generate reports')
    analyze_parser.add_argument('--generate-report', action='store_true', help='Generate comprehensive report')
    analyze_parser.add_argument('--content-quality', action='store_true', help='Analyze content quality')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Execute command
    try:
        if args.command == 'scrape':
            return cmd_scrape(args, logger)
        elif args.command == 'analyze':
            from scripts.analysis_manager import AnalysisManager
            manager = AnalysisManager()
            if args.generate_report:
                report = manager.generate_comprehensive_report()
                logger.info(f"Analysis report generated: {report['report_file']}")
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)