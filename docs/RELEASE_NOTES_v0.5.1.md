# Release Notes - v0.5.1

**Release Date:** July 16, 2025  
**Version:** 0.5.1  
**Type:** Patch Release

## 🐛 Bug Fixes

### Fixed Vector Store Loading Issue
- **Problem**: FAISS vector store failed to load with KeyError: 'id'
- **Solution**: Added backward compatibility for old metadata format
- **Impact**: Search functionality is now fully restored

### Technical Details
The vector store was expecting documents to have an 'id' field, but the actual metadata structure had:
- 'text' field instead of 'content'
- No 'id' field (now auto-generated as doc_0, doc_1, etc.)
- Title stored separately

## 🔧 Improvements

### 1. Enhanced Error Handling
- Added detailed traceback logging for debugging
- Improved error messages for vector store issues
- Graceful fallbacks when indices are missing

### 2. Backward Compatibility
- Supports both old and new metadata formats
- No data migration required
- Seamless upgrade from previous versions

### 3. Multiple Path Support
- Searches for indices in multiple locations
- Better flexibility for different deployment scenarios

## 📊 Test Results

- **OAuth Endpoints**: ✅ 100% working (regression tested)
- **Vector Store**: ✅ Fixed and operational
- **MCP Tools**: ✅ All 20 tools tested and functional
- **Docker Build**: ✅ Successful
- **Railway Deployment**: ✅ Live and healthy

## 🚀 Deployment

```bash
# Docker
docker pull longevitycoach/strunz-mcp:0.5.1

# Railway
Automatic deployment on push to main branch
```

## 📝 Upgrade Notes

This is a backward-compatible patch release. No action required for existing deployments other than updating to the new version.

## 🙏 Acknowledgments

Thanks to the early testers who reported the vector store loading issue, enabling a quick fix.

---

**Next Release**: v0.6.0 (planned) - New features and enhancements