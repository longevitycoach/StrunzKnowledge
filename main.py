#!/usr/bin/env python3
"""
Main entry point for the Strunz Knowledge Base application.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.main import StrunzKnowledgeScraper
from src.rag.document_processor import DocumentProcessor
from src.mcp.server import run_server

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_command(args):
    """Execute the scraping command."""
    logger.info("Starting web scraping process...")
    scraper = StrunzKnowledgeScraper(output_dir=args.output)
    scraper.scrape_all()
    logger.info("Scraping completed!")


def index_command(args):
    """Build or rebuild the vector index."""
    logger.info("Building vector index...")
    processor = DocumentProcessor()
    stats = processor.process_all_documents(
        processed_dir=args.input,
        use_docling=args.use_docling
    )
    logger.info(f"Indexing completed! Stats: {stats}")


def server_command(args):
    """Start the MCP server."""
    logger.info("Starting MCP server...")
    run_server(host=args.host, port=args.port)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dr. Strunz Knowledge Base Application"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape content from strunz.com')
    scrape_parser.add_argument(
        '--output', '-o',
        default='data/raw',
        help='Output directory for scraped data'
    )
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Build vector index')
    index_parser.add_argument(
        '--input', '-i',
        default='data/processed',
        help='Input directory with processed markdown files'
    )
    index_parser.add_argument(
        '--use-docling',
        action='store_true',
        help='Use Docling for text processing'
    )
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start MCP server')
    server_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Server host'
    )
    server_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Server port'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'scrape': scrape_command,
        'index': index_command,
        'server': server_command
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()