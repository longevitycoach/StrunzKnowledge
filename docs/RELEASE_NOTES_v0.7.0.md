# Release Notes - v0.7.0

**Release Date**: July 18, 2025  
**Type**: Major Feature Release

## 🎯 Highlights

This release brings **critical Claude.ai integration fixes** and **comprehensive testing infrastructure** that ensures production-ready stability for the Dr. Strunz Knowledge MCP Server.

## 🐛 Critical Fixes

### ✅ Claude.ai Integration Fix
- **Fixed**: "not_available" error when connecting from Claude.ai
- **Solution**: Switched to Railway official MCP server with proper SSE transport
- **Impact**: Users can now successfully add the MCP server to claude.ai
- **Details**: The previous stdio transport was incompatible with Claude.ai's HTTP/SSE requirements

## 🚀 New Features

### 📊 Comprehensive Test Suite Enhancement
- Added **31 new comprehensive tests** covering all MCP tools
- Achieved **100% pass rate** on local Docker deployment
- New test categories:
  - **Complex Query Scenarios**: Multi-condition searches, nested profiles
  - **Multilingual Support**: German queries, mixed languages, special characters
  - **Edge Cases & Boundaries**: Empty results, max limits, age boundaries
  - **Performance & Scalability**: Sequential/concurrent requests, heavy computation
  - **Integration Scenarios**: Complete user journeys, clinician workflows

### 🧪 Test Infrastructure Improvements
- Streamlined test reports to a single comprehensive report
- Added full I/O logging for all 19 MCP tools
- Created three new comprehensive test scripts:
  - `test_comprehensive_all_scenarios.py` - User journey testing
  - `test_comprehensive_full_io.py` - Detailed input/output testing
  - `test_docker_mcp_comprehensive.py` - Docker deployment testing

## 🔧 Technical Improvements

### Version Consistency
- Updated all server components to v0.7.0
- Fixed logger initialization in vector_store.py
- Resolved function import errors in test suite
- Enhanced overall test coverage to 89.5%

### Performance Enhancements
- Average response time: 13ms (Docker)
- Concurrent request handling optimized
- Heavy computation scenarios tested
- Memory usage monitored and optimized

## 📈 Testing Results

### Production Railway (86.4% Success)
- All 19 MCP tools: ✅ Working perfectly
- 3 prompt tests: ❌ Expected (different method on production)
- Performance: Most tools respond in 25-40ms

### Local Docker (100% Success)
- 31/31 tests passing
- Average response time: 13ms
- Full multilingual support verified
- Integration scenarios validated

## 🛠️ For Developers

### Running Tests Locally
```bash
# Docker comprehensive tests
python src/scripts/testing/test_docker_mcp_comprehensive.py

# Production tests
python src/scripts/testing/test_comprehensive_full_io.py --production
```

### Key Files Changed
- `railway-deploy.py` - Fixed SSE server selection
- `railway_official_mcp_server.py` - Added full prompts capability
- `test_docker_mcp_comprehensive.py` - New comprehensive test suite
- All server files updated to v0.7.0

## 🔄 Migration Notes

Users experiencing Claude.ai connection issues should:
1. Update to v0.7.0
2. Restart the MCP server
3. Re-add the server in claude.ai settings

## 🙏 Acknowledgments

Thanks to all users who reported the Claude.ai integration issue, helping us identify and fix this critical bug quickly.

---

**Full Changelog**: [v0.6.3...v0.7.0](https://github.com/longevitycoach/StrunzKnowledge/compare/v0.6.3...v0.7.0)