# Dr. Strunz Knowledge Base - Claude Code Development Guide

## Content Sources

### 1. Books (13 total)
The following Dr. Ulrich Strunz books have been processed:

| Title | Year | Filename |
|-------|------|----------|
| Fitness drinks | 2002 | Dr.Ulrich-Strunz_Fitness_drinks_2002.pdf |
| Die neue Diaet Das Fitnessbuch | 2010 | Dr.Ulrich-Strunz_Die_neue_Diaet_Das_Fitnessbuch_2010.pdf |
| Das Geheimnis der Gesundheit | 2010 | Dr.Ulrich-Strunz_Das_Geheimnis_der_Gesundheit_2010.pdf |
| Das neue Anti-Krebs-Programm - dem Krebs keine Chance geben  | 2012 | Dr.Ulrich-Strunz_Das_neue_Anti-Krebs-Programm_-_dem_Krebs_keine_Chance_geben__2012.pdf |
| No-Carb-Smoothies | 2015 | Dr.Ulrich-Strunz_No-Carb-Smoothies_2015.pdf |
| Wunder der Heilung | 2015 | Dr.Ulrich-Strunz_Wunder_der_Heilung_2015.pdf |
| Blut - Die Geheimnisse Unseres flussigen Organs | 2016 | Dr.Ulrich-Strunz_Blut_-_Die_Geheimnisse_Unseres_flussigen_Organs_2016.pdf |
| Das Strunz-Low-Carb-Kochbuch | 2016 | Dr.Ulrich-Strunz_Das_Strunz-Low-Carb-Kochbuch_2016.pdf |
| Heilung erfahren | 2019 | Dr.Ulrich-Strunz_Heilung_erfahren_2019.pdf |
| 77 Tipps fuer Ruecken und Gelenke | 2021 | Dr.Ulrich-Strunz_77_Tipps_fuer_Ruecken_und_Gelenke_2021.pdf |
| Das Stress-weg-Buch | 2022 | Dr.Ulrich-Strunz_Das_Stress-weg-Buch_2022.pdf |
| Die Amino-Revolution | 2022 | Dr.Ulrich-Strunz_Die_Amino-Revolution_2022.pdf |
| Der Gen-Trick | 2025 | Dr.Ulrich-Strunz_Der_Gen-Trick_2025.pdf |

### 2. News Articles
- **Total articles**: 6,953 unique articles
- **Date range**: 2004-09-28 to 2025-07-11
- **Base URL**: https://www.strunz.com/news/
- **URL pattern**: https://www.strunz.com/news/[article-slug].html

### 3. Forum Content
- **Total chunks**: 6,400
- **Status**: Limited data available (only showing date 02.05.2020)
- **Note**: Forum scraping appears incomplete and may need to be redone

## Data Processing Details

### Text Chunking
- **News**: ~843 characters per chunk with 200 char overlap
- **Books**: ~1,333 characters per chunk with 300 char overlap
- **Forum**: Variable chunk sizes

### Vector Database
- **Model**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Dimensions**: 384
- **Index Type**: FAISS IndexFlatL2
- **Total Vectors**: 28,938

## Sentence-Transformers Analysis & Testing Results

### Usage Pattern
The MCP server uses sentence-transformers for **both** initial processing AND real-time queries:

1. **Initial Processing**: Document embeddings created during FAISS index building
2. **Runtime Queries**: Each user search encoded in real-time using same model
3. **Model**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
4. **Implementation**: Full integration in `/src/rag/vector_store.py`

### Benefits Demonstrated (Test Results 2025-07-13)
- **Test Success Rate**: 84.2% (16/19 MCP tools)
- **Average Response Time**: 16ms per tool
- **Semantic Search Quality**: Superior to TF-IDF for medical terminology
- **Multilingual Support**: Seamless German/English query processing
- **Real-time Performance**: Query encoding adds minimal latency

### Resource Requirements
| Aspect | Sentence-Transformers | TF-IDF Alternative |
|--------|----------------------|-------------------|
| Memory | ~2GB | ~512MB |
| Startup Time | 10-20s | <2s |
| Search Quality | Excellent semantic matching | Basic keyword matching |
| Dependencies | PyTorch + Transformers | Scikit-learn only |
| Multilingual | Native support | Limited support |

### Production Recommendations
1. **Memory Planning**: Ensure 2GB+ RAM for optimal performance
2. **Health Checks**: Allow 60+ seconds for server startup
3. **Caching Strategy**: Consider embedding caching for frequent queries
4. **Fallback Available**: TF-IDF lightweight embeddings in `src/mcp/lightweight_embeddings.py`

### Test Infrastructure
- **Full Test Suite**: `./src/scripts/testing/test_mcp_jsonrpc.sh` (19 comprehensive tests)
- **Protocol**: JSON-RPC 2.0 over HTTP at `/messages` endpoint
- **Report**: Generated automatically as `TEST_REPORT_v{VERSION}.md` in `docs/test-reports/`
- **Docker Testing**: Always test locally before Railway deployment
- **Comprehensive Tests**: `./src/tests/test_railway_comprehensive.py` for production validation

### MCP Protocol Security
- **Production Server**: Uses `claude_compatible_server.py` with OAuth 2.1 + SSE transport
- **OAuth 2.1 Compliance**: Full authorization flow with dynamic client registration
- **Public Endpoints**: Health check (`/`), SSE (`/sse`), and OAuth endpoints only
- **SSE Endpoint**: Available at `/sse` for Claude.ai integration monitoring
- **Data Protection**: All MCP queries require OAuth authentication

## Release v0.6.3 - Clean MCP SDK Implementation (July 17, 2025)

### 🚀 Major Architecture Decision: Official MCP SDK Migration

**Decision**: Migrated from FastMCP to official MCP SDK for better Claude.ai compatibility and protocol compliance.

**Technical Implementation**:
- **New Primary Server**: `src/mcp/mcp_sdk_clean.py` - Clean implementation with official SDK
- **Protocol Version**: 2025-03-26 (latest MCP specification)
- **Transport**: Stdio only (eliminates web dependency conflicts)
- **Capabilities**: Full prompts support (3 health-focused prompts) + 9 core tools

### 🔧 Railway Deployment Issues Resolved

**Problem**: Railway "Failed to create code snapshot" errors with v0.6.2
**Root Cause**: FastAPI dependencies in MCP SDK server conflicted with Railway's build system
**Solution**: Created clean implementation (`mcp_sdk_clean.py`) without any web framework dependencies

**Deployment Strategy**:
1. **Primary**: Clean MCP SDK server (stdio transport)
2. **Fallback**: FastMCP compatible server (SSE transport)
3. **Emergency**: Enhanced server (basic MCP implementation)

### 🎯 Claude.ai Integration Improvements

**Prompts Capability Added** (Critical for Claude.ai):
- **Health Assessment**: Comprehensive evaluation based on Dr. Strunz methodology
- **Supplement Optimization**: Protocol optimization with safety checks
- **Longevity Protocol**: Anti-aging strategies based on latest research

**Benefits**:
- ✅ Claude.ai shows server as "enabled" (previously disabled)
- ✅ Better protocol compliance and future-proofing
- ✅ Reduced dependency conflicts and deployment issues
- ✅ Enhanced error recovery with graceful fallbacks

### 📊 Server Architecture Comparison

| Aspect | FastMCP (v0.6.1) | Official SDK (v0.6.3) |
|--------|-------------------|------------------------|
| Protocol Compliance | Partial | Full |
| Claude.ai Support | Basic | Complete with prompts |
| Dependencies | FastAPI + SSE | MCP SDK only |
| Railway Deployment | Unreliable | Stable |
| Transport | HTTP/SSE | Stdio |
| Error Handling | Basic | Graceful fallbacks |

### 🚦 Development Guidelines Updated

**Pre-commit Testing** (Enhanced for v0.6.3):
1. **Local Docker Testing**: Always test new server implementations locally
2. **MCP Protocol Validation**: Verify full MCP compliance
3. **Dependency Audit**: Check for minimal dependency footprint
4. **Railway Compatibility**: Test deployment scenarios

**Server Selection Logic**:
```python
# Railway Environment
if is_railway:
    try:
        # Primary: Clean MCP SDK
        from src.mcp.mcp_sdk_clean import main as run_server
        asyncio.run(run_server())
    except Exception:
        # Fallback: FastMCP compatible
        from src.mcp.claude_compatible_server import main as run_server
        asyncio.run(run_server())
```

## SDLC (Software Development Lifecycle) Process

### 1. **Local Development Phase**
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Run scripts locally
python -m src.mcp.enhanced_server  # Local testing
```

### 2. **Pre-Commit Docker Testing** (MANDATORY)
```bash
# Build Docker image locally
docker build -t strunz-mcp:test .

# Run comprehensive local tests
docker run -d --name strunz-test -p 8000:8000 \
  -e RAILWAY_ENVIRONMENT=production \
  -e BASE_URL=http://localhost:8000 \
  strunz-mcp:test

# Test all functionality
./src/scripts/testing/test_mcp_jsonrpc.sh http://localhost:8000
python src/tests/test_railway_comprehensive.py --url http://localhost:8000

# Cleanup
docker stop strunz-test && docker rm strunz-test
```

### 3. **Git Commit Process**
```bash
# Only commit if all Docker tests pass
git add -A
git commit -m "feat: Add OAuth 2.1 compliance and fix tool loading

- Implemented full OAuth 2.1 authorization flow
- Fixed all 20 MCP tools loading with FAISS integration
- Added prompts capability for Claude.ai compatibility
- Enhanced Docker testing process

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### 4. **Railway Deployment** (Automatic)
- **Trigger**: Push to main branch automatically triggers Railway deployment
- **Configuration**: Uses `railway.toml` for deployment settings
- **Build Time**: 5-10 minutes (Docker build + FAISS index reconstruction)
- **Health Check**: `/railway-health` endpoint with 300s timeout

### 5. **Railway Production Testing**
After each deployment to Railway:
```bash
# 1. Health Check
curl -s https://strunz.up.railway.app/ | jq '.version'

# 2. OAuth 2.1 Compliance Check
curl -s https://strunz.up.railway.app/.well-known/oauth-authorization-server | jq '.authorization_endpoint'

# 3. MCP Protocol Test
curl -X POST https://strunz.up.railway.app/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2025-03-26"}, "id": 1}' \
  | jq '.result.capabilities'

# 4. SSE Endpoint Test
./src/scripts/testing/test_sse_endpoint.sh https://strunz.up.railway.app/sse

# 5. Comprehensive Production Test
python src/tests/test_railway_comprehensive.py
```

### 6. **Test Report Generation**
```bash
# Generate test report
./src/scripts/testing/test_mcp_jsonrpc.sh > TEST_REPORT_v{VERSION}.md

# Commit test report
git add docs/test-reports/TEST_REPORT_v{VERSION}.md
git commit -m "docs: Add test report for v{VERSION}"

# Update README.md with latest test report link
# Update version badges and links
```

### 7. **Quality Assurance Checklist**
- [ ] All Docker tests pass locally
- [ ] Railway deployment successful
- [ ] Version number updated correctly
- [ ] OAuth 2.1 endpoints functional
- [ ] All 20 MCP tools working
- [ ] FAISS search operational
- [ ] SSE endpoint for Claude.ai working
- [ ] Test report generated and committed
- [ ] README.md updated with latest links
- [ ] No broken diagrams or links

### Railway Domains
- **Public Domain**: `strunz.up.railway.app` (RAILWAY_PUBLIC_DOMAIN)
- **Private Domain**: `strunz.railway.internal` (RAILWAY_PRIVATE_DOMAIN)
- **Alternative**: `strunz-knowledge-production.up.railway.app`

### Docker Publishing (Optional)
For Docker Hub publishing after releases:
```bash
# 1. Tag release image
docker tag strunz-mcp:latest longevitycoach/strunz-mcp:v{VERSION}

# 2. Push to registry (requires Docker Hub account)
docker push longevitycoach/strunz-mcp:v{VERSION}
docker push longevitycoach/strunz-mcp:latest

# 3. Verify on Docker Hub
# Check https://hub.docker.com/r/longevitycoach/strunz-mcp
```

**Note**: Docker Hub publishing is optional since Railway builds directly from Git.

## Version Management

### Current Version: 0.6.3
- **Features**: Clean MCP SDK implementation, 9 core tools + 3 prompts, FAISS search, full protocol compliance
- **Primary Server**: `src/mcp/mcp_sdk_clean.py` (official SDK)
- **Fallback Server**: `src/mcp/claude_compatible_server.py` (FastMCP)
- **Compatibility**: Claude.ai ready with prompts capability

### Version Update Process
1. **Update version in code**: `src/mcp/mcp_sdk_clean.py` and `src/mcp/claude_compatible_server.py`
2. **Update changelog**: Document changes in commit message
3. **Test thoroughly**: Run full Docker test suite
4. **Deploy and verify**: Check Railway deployment version
5. **Generate test report**: Create `TEST_REPORT_v{VERSION}.md`
6. **Update README**: Link to latest test report

## Update Information
- News articles can be updated incrementally using wget with -N flag
- Books are manually added to data/books/ directory
- Forum content needs complete re-scraping

## Directory Structure

### Root Directory
```
├── main.py                   # Main entry point (detects Railway vs local)
├── Dockerfile               # Container configuration
├── railway.toml             # Railway deployment settings
├── requirements*.txt        # Python dependencies
├── CLAUDE.md               # This file - project documentation
└── README.md               # Public documentation
```

### Data Directory (`data/`)
```
data/
├── books/                   # PDF books (13 books, copyright protected)
├── raw/
│   ├── news/               # HTML news articles (6,953 articles)
│   └── forum/              # Forum HTML files (6,400 chunks)
├── processed/
│   ├── books/              # Processed book chunks (JSON)
│   ├── news/               # Processed news chunks (JSON)
│   └── forum/              # Processed forum chunks (JSON)
├── faiss_indices/
│   └── chunks/             # Split indices for GitHub (<40MB each)
│       ├── combined_index.faiss.part* # Index chunks
│       ├── combined_metadata.json.part* # Metadata chunks
│       └── reconstruct_*.py # Reconstruction scripts
└── analysis/               # Content analysis reports
```

### Source Code (`src/`)
```
src/
├── mcp/                    # MCP servers (4 files)
│   ├── claude_compatible_server.py  # Production OAuth 2.1 server
│   ├── enhanced_server.py           # Enhanced MCP with 20 tools
│   ├── oauth_provider.py            # OAuth 2.1 implementation
│   └── user_profiling.py            # Health assessment system
├── rag/                    # RAG system (11 files)
│   ├── search.py          # Singleton vector search
│   ├── vector_store.py    # FAISS vector store
│   ├── book_processor.py  # Book content processing
│   ├── news_processor.py  # News content processing
│   ├── forum_processor.py # Forum content processing
│   ├── html_processor.py  # HTML processing utilities
│   ├── enhanced_html_processor.py # Enhanced HTML processing
│   ├── document_processor.py # Document processing
│   ├── docling_processor.py # Docling integration
│   ├── pdf_processor.py   # PDF processing utilities
│   ├── build_index.py     # Index construction
│   └── update_combined_index.py # Index updates
├── scripts/               # Utilities and deployment (46 files)
│   ├── deployment/        # Server deployment scripts (3 files)
│   ├── testing/          # Test scripts (35 files)
│   ├── analysis/         # Analysis tools (2 files)
│   ├── data/             # Data processing utilities (2 files)
│   ├── setup/            # Setup scripts (2 files)
│   └── *.py              # Individual utilities (2 files)
├── tests/                 # Test suites (5 files)
│   ├── test_railway_comprehensive.py # Production tests
│   ├── test_enhanced_mcp.py # Enhanced MCP tests
│   ├── test_oauth_endpoints.py # OAuth testing
│   ├── test_production_mcp.py # Production validation
│   └── test_vector_store_singleton.py # Singleton tests
└── prompts/              # MCP prompt definitions
```

### Documentation (`docs/`)
```
docs/
├── SCRIPTS.md            # Complete scripts documentation
├── DEPLOYMENT_CHECKLIST.md # Production deployment guide
├── test-reports/         # Test execution reports
│   ├── TEST_REPORT_v0.5.4.md # Latest test report
│   └── *_TEST_REPORT*.md     # Historical reports
└── RELEASE_NOTES_v*.md   # Version release notes
```

### Configuration (`config/`)
```
config/
├── docker/               # Docker configurations
│   ├── docker-compose.yml
│   └── docker-compose.staging.yml
└── mcp-inspector/        # MCP Inspector test configs
    ├── sse-config.json   # SSE transport config
    └── stdio-config.json # stdio transport config
```

### Key Files
- **Health Check**: `railway.toml` → `/railway-health` endpoint
- **Version**: `src/mcp/claude_compatible_server.py` → Search for "0.5.4"
- **Tools**: `src/mcp/enhanced_server.py` → 20 MCP tools
- **OAuth**: `src/mcp/oauth_provider.py` → Full OAuth 2.1 implementation
- **Search**: `src/rag/search.py` → Singleton FAISS vector search
- **Tests**: `src/tests/test_railway_comprehensive.py` → Production validation

## Summary

The StrunzKnowledge project provides a comprehensive MCP (Model Context Protocol) server that makes Dr. Ulrich Strunz's health knowledge accessible to AI assistants like Claude. With full OAuth 2.1 compliance, 20 specialized tools, and FAISS-powered semantic search across 43,373 documents, it represents a complete implementation of modern AI-assisted health consultation.

**Current Status**: Production-ready with v0.6.3 deployed on Railway with clean MCP SDK
**Integration**: Claude.ai compatible with prompts capability and stdio transport
**Coverage**: 13 books, 6,953 news articles, 6,400 forum discussions
**Tools**: 9 core MCP tools + 3 health prompts covering search, analysis, protocols, and personalization
**Security**: Full OAuth 2.1 authorization with dynamic client registration

## MCP Tools Quick Reference

### Information Tools (3)
- `get_dr_strunz_biography()` - Comprehensive bio
- `get_mcp_server_purpose()` - Server explanation
- `get_vector_db_analysis()` - Database statistics

### Search & Analysis Tools (3)
- `knowledge_search()` - Semantic search
- `find_contradictions()` - Conflict analysis
- `trace_topic_evolution()` - Historical tracking

### Protocol Tools (3)
- `create_health_protocol()` - Treatment plans
- `analyze_supplement_stack()` - Stack optimization
- `nutrition_calculator()` - Nutrition planning

### Community Tools (3)
- `get_community_insights()` - Forum wisdom
- `summarize_posts()` - Content summaries
- `get_trending_insights()` - Current trends

### Newsletter Tools (3)
- `analyze_strunz_newsletter_evolution()` - 20-year analysis
- `get_guest_authors_analysis()` - Editorial approach
- `track_health_topic_trends()` - Topic tracking

### User Profiling Tools (3)
- `get_health_assessment_questions()` - Questionnaire
- `assess_user_health_profile()` - Profile creation
- `create_personalized_protocol()` - Custom protocols

### Comparison Tool (1)
- `compare_approaches()` - Method comparison

## Common Tasks

### Adding New MCP Tools
1. Define in `enhanced_server.py`
2. Implement logic with source citations
3. Update tool count in `get_mcp_server_purpose()`
4. Add tests
5. Deploy

### Updating Content
1. Process new content (scraper)
2. Generate embeddings
3. Update FAISS index
4. Test search quality
5. Deploy new index

### Fixing Issues
1. Check Railway logs
2. Run production tests
3. Fix with local tests
4. Deploy through SDLC
5. Verify in production

## Performance Tips

### Vector Search
- Batch queries when possible
- Use k=10-20 for best results
- Cache frequent queries
- Monitor query times

### Memory Management
- FAISS uses ~1.2GB
- Monitor for growth
- Restart if needed
- Optimize indices monthly

## Troubleshooting

### Common Issues
1. **Deployment Fails**: Check requirements.txt
2. **Search Quality**: Verify embeddings
3. **Memory Issues**: Check for loops
4. **Slow Responses**: Review query complexity

### Debug Commands
```bash
# Check logs
railway logs

# Test specific tool
curl -X POST https://strunz.up.railway.app/tools/knowledge_search \
  -H "Content-Type: application/json" \
  -d '{"query": "Vitamin D"}'
```

## Security Notes
- No API keys in code
- Use environment variables
- Sanitize all inputs
- Rate limit endpoints
- No PII in logs

## Maintenance Schedule

### Daily
- Monitor error logs
- Check response times

### Weekly  
- Update newsletter content
- Process forum posts
- Review metrics

### Monthly
- Reindex for optimization
- Update dependencies
- Performance review
- Backup data

## GitHub File Size Management

### File Size Rules
- **GitHub limit**: 100 MB per file (warning at 50 MB)
- **Our approach**: Split files larger than 40 MB into chunks
- **FAISS indices**: Stored as chunks in `data/faiss_indices/chunks/`
- **Reconstruction**: Automatic during Docker build

### Managing Large Files
1. **Check file sizes** before committing:
   ```bash
   find . -type f -size +40M -exec ls -lh {} \;
   ```

2. **Split large files** using provided script:
   ```bash
   python src/scripts/data/split_faiss_index.py
   ```

3. **Always commit chunks**, never the full files:
   - ✅ `data/faiss_indices/chunks/*.part*`
   - ❌ `data/faiss_indices/combined_index.faiss`

4. **Monitor repository size**:
   ```bash
   git count-objects -vH
   ```

### Protected Directories (Never Commit)
- `data/books/` - PDF books (copyright)
- `data/raw/` - Scraped HTML content
- `data/processed/` - Processed text chunks
- Full FAISS index files (use chunks instead)

## Development Best Practices

### CI/CD Checklist
- **Always run a second test-run against the local container docker deployment before checkin to Github and deploy to railways.**
- **Use the full MCP Server - NO MINIMAL Server, always full functions!**
- **Please always make an integration with FAISS vector DB and with real content**
- **Please always test locally with docker**

### Important Rules
1. **Source Citations**: Always add specific source citations to all MCP tool responses
   - Books: Include chapter and page numbers
   - News: Include article dates and URLs  
   - Forum: Include thread IDs
   
2. **Testing Protocol**: 
   - Build Docker image locally
   - Run comprehensive tests
   - Verify SSE endpoint works
   - Check memory usage < 512MB for Railway

3. **Script Organization**: All scripts under `src/scripts/`
   - deployment/ - Server scripts
   - testing/ - Test scripts
   - analysis/ - Analysis tools
   - data/ - Data utilities

## Related Documentation

### Essential Docs
- [Scripts Guide](docs/SCRIPTS.md) - All scripts documentation
- [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md) - Production deployment steps
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Directory organization
- [Release Notes](docs/RELEASE_NOTES_v0.2.0.md) - Latest release information

### Test Reports
- [Latest Test Report](docs/test-reports/MCP_FULL_SERVER_TEST_REPORT.md) - v0.2.0 test results
- [All Test Reports](docs/test-reports/) - Historical test documentation