# Dr. Strunz Knowledge Base

A comprehensive, searchable knowledge base application that provides intelligent access to Dr. Ulrich Strunz's articles and forum posts through an LLM-powered MCP (Meta-Cognitive Prompting) server.

## Features

- **Web Scraping**: Automated scraping of all content from strunz.com including news and forum posts
- **Text Processing**: Advanced text extraction using Docling OCR for high-fidelity content
- **Vector Search**: FAISS-based semantic search across the entire knowledge base
- **MCP Server**: FastMCP implementation with Server-Sent Events (SSE) for real-time responses
- **RAG System**: Retrieval-Augmented Generation for accurate, source-cited answers
- **German Language Support**: Full UTF-8 encoding and German character support

## Architecture

```
StrunzKnowledge/
├── src/
│   ├── scraper/         # Web scraping and data collection
│   ├── rag/             # Vector store and document processing
│   ├── mcp/             # FastMCP server implementation
│   └── tests/           # Comprehensive test suite
├── data/
│   ├── raw/             # Scraped JSON data
│   └── processed/       # Processed markdown and vector indices
└── config/              # Configuration files
```

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd StrunzKnowledge

# Build and run with Docker Compose
docker-compose up -d

# The MCP server will be available at http://localhost:8000
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper to collect data
python -m src.scraper.main

# Start the MCP server
python -m src.mcp.server
```

## API Endpoints

- `GET /` - Server status and statistics
- `GET /sse?q=<query>` - SSE endpoint for streaming search results
- `POST /index/rebuild` - Rebuild the vector index
- `/mcp/*` - MCP tool endpoints

## MCP Tools

1. **knowledge_search** - Search the knowledge base with optional category and date filters
2. **summarize_posts** - Generate summaries of specific posts
3. **get_latest_insights** - Retrieve the most recent posts from a category
4. **get_most_discussed_topics** - Find posts with the most engagement

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

### Building from Source

```bash
# Build Docker image
docker build -t strunz-knowledge .

# Run container
docker run -p 8000:8000 strunz-knowledge
```

## Deployment

### Railway

The project includes a `railway.toml` configuration for easy deployment:

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the configuration
3. Set any required environment variables in the Railway dashboard
4. Deploy!

### Environment Variables

- `LOG_LEVEL` - Logging level (default: INFO)
- `MCP_SERVER_HOST` - Server host (default: 0.0.0.0)
- `MCP_SERVER_PORT` - Server port (default: 8000)
- `VECTOR_DB_TYPE` - Vector database type (default: faiss)
- `EMBEDDING_MODEL` - Sentence transformer model for embeddings

## Developer Resources

### Web Scraping
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

### RAG Implementation
- [Docling GitHub](https://github.com/docling-project/docling)
- [Quarkus LangChain4j RAG Guide](https://docs.quarkiverse.io/quarkus-langchain4j/dev/rag.html)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence Transformers](https://www.sbert.net/)

### Vector Databases
- [FAISS Tutorial](https://www.pinecone.io/learn/faiss-tutorial/)
- [Vector Database Comparison](https://www.pinecone.io/learn/vector-database/)

### FastMCP
- [FastMCP PyPI](https://pypi.org/project/fastmcp/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### Docker & Deployment
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Railway Documentation](https://docs.railway.app/)
- [Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://realpython.com/pytest-python-testing/)
- [Async Testing with Pytest](https://pytest-asyncio.readthedocs.io/)

## License

This project is for educational and research purposes. Please respect the original content's copyright and Dr. Strunz's intellectual property.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request