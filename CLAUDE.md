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

## Update Information
- News articles can be updated incrementally using wget with -N flag
- Books are manually added to data/books/ directory
- Forum content needs complete re-scraping

## Directory Structure
```
data/
├── books/                    # PDF books
├── raw/
│   ├── news/                # HTML news articles
│   └── forum/               # Forum HTML (incomplete)
├── processed/
│   ├── books/               # Processed book chunks
│   ├── news/                # Processed news chunks
│   └── forum/               # Processed forum chunks
└── faiss_indices/
    ├── books/               # Book vector index
    ├── news/                # News vector index
    ├── forum/               # Forum vector index
    └── combined_index.faiss # Combined searchable index
```

## SDLC (Software Development Lifecycle) Process

### 1. Development Phase

#### Local Development Setup
```bash
# Clone repository
git clone https://github.com/longevitycoach/StrunzKnowledge.git
cd StrunzKnowledge

# Install dependencies
pip install -r requirements.txt

# Run MCP server locally
python -m src.mcp.server
```

#### Key Development Files
- `src/mcp/enhanced_server.py` - Main MCP server with 19 tools
- `src/mcp/user_profiling.py` - User health assessment system
- `src/rag/search.py` - Vector search implementation
- `requirements.txt` - Python dependencies

#### Testing Locally
```bash
# Run all tests
pytest src/tests/ -v

# Test specific MCP functionality
python src/tests/test_enhanced_mcp.py

# Test user profiling
python src/tests/test_user_profiling.py
```

### 2. Version Control Phase

#### Git Workflow
```bash
# Check status
git status

# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "feat: Add comprehensive user profiling system

- Implemented health assessment questionnaire
- Added 3 new MCP tools for personalization
- Enhanced source citations with URLs
- Fixed mermaid diagram syntax errors

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### 3. Deployment Phase

#### Automatic Railway Deployment
1. **Trigger**: Push to main branch automatically triggers deployment
2. **Build Process** (5-7 minutes):
   - Docker image build
   - Dependencies installation
   - FAISS indices copying
   - Environment setup
3. **Startup**: MCP server starts on Railway infrastructure

#### Monitoring Deployment
```bash
# Check deployment status
curl -I https://strunz-knowledge.up.railway.app/

# Expected response when ready:
# HTTP/2 200
# content-type: text/html; charset=utf-8
```

### 4. Production Testing Phase

#### Health Checks
```bash
# Basic health check
curl https://strunz-knowledge.up.railway.app/

# SSE endpoint test
curl https://strunz-knowledge.up.railway.app/sse

# Should see:
# data: {"type": "message", "data": "Connected to Dr. Strunz Knowledge MCP Server"}
```

#### Integration Tests
```bash
# Run production tests locally
python src/tests/test_production_mcp.py

# GitHub Actions (automatic on push)
# Manual trigger: Actions tab > "Integration Tests" > Run workflow
```

### 5. Monitoring & Logging

#### Railway Dashboard
- Memory usage: ~1.2GB baseline (FAISS loaded)
- Response times: <100ms for searches
- CPU spikes during vector operations
- Error logs for debugging

#### Key Metrics
- **Memory**: Monitor for leaks (restart if >2GB)
- **Response Time**: Target <100ms
- **Error Rate**: Should be <1%
- **Uptime**: 99.9% target

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
curl -X POST https://strunz-knowledge.up.railway.app/tools/knowledge_search \
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
   python scripts/split_faiss_index.py
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
