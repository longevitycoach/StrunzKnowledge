# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Dr. Strunz Knowledge Base application - a comprehensive RAG (Retrieval-Augmented Generation) system that scrapes, processes, and serves content from www.strunz.com through an MCP (Meta-Cognitive Prompting) server.

## Key Commands

### Development Commands
- `python main.py scrape` - Scrape all content from strunz.com
- `python main.py index` - Build the FAISS vector index
- `python main.py server` - Start the FastMCP server
- `pytest` - Run the test suite
- `docker-compose up` - Run the entire application stack

### Testing
- `pytest src/tests/test_mcp_integration.py` - Run MCP integration tests
- `pytest --cov=src` - Run tests with coverage

## Architecture Overview

The application follows a modular architecture with three main components:

1. **Scraper Module** (`src/scraper/`)
   - `base_scraper.py`: Core scraping logic with pagination handling
   - `markdown_generator.py`: Converts JSON to structured markdown
   - Handles German text encoding (UTF-8) properly

2. **RAG Module** (`src/rag/`)
   - `vector_store.py`: FAISS-based vector storage implementation
   - `document_processor.py`: Text chunking and embedding generation
   - `docling_processor.py`: Optional OCR integration
   - Uses sentence-transformers for multilingual embeddings

3. **MCP Module** (`src/mcp/`)
   - `server.py`: FastMCP server with SSE endpoint
   - Implements 4 main tools: knowledge_search, summarize_posts, get_latest_insights, get_most_discussed_topics
   - System prompt enforces citation of sources

## Important Design Decisions

1. **FAISS over AlloyDB**: Chosen for zero cost, better performance for similarity search, and ability to run in-container
2. **Embedding Model**: Using `paraphrase-multilingual-MiniLM-L12-v2` for German language support
3. **Chunking Strategy**: 1000 character chunks with 200 character overlap
4. **Content Organization**: Each category gets its own markdown file with standardized structure
5. **Pagination Handling**: Recursive crawling with visited URL tracking

## Development Notes

- All text processing must handle German special characters (ä, ö, ü, ß)
- The scraper respects rate limits with configurable delays
- Vector index is persisted to disk and loaded on startup
- MCP tools always return structured data with metadata
- The system prompt ensures the LLM only uses knowledge base content