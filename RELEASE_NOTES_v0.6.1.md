# Release Notes v0.6.1 - Claude.ai Integration Fix

**Release Date**: July 17, 2025  
**Version**: 0.6.1  
**Type**: Hotfix  

## 🐛 Critical Bug Fix

### Fixed Claude.ai Integration
- **Issue**: Claude.ai showed MCP server as disabled
- **Cause**: Missing prompts capability in server initialization
- **Solution**: 
  - Added `prompts` capability declaration to initialize response
  - Implemented `prompts/list` method returning empty array
  - Updated server version to 0.6.1 across all responses

## 🔧 Technical Details

### Changes Made
1. **Server Initialization** (`/messages` - initialize):
   ```json
   "capabilities": {
     "tools": { "listChanged": false },
     "prompts": { "listChanged": false }  // Added
   }
   ```

2. **New Method Implementation** (`/messages` - prompts/list):
   ```json
   {
     "jsonrpc": "2.0",
     "method": "prompts/list",
     "result": { "prompts": [] }
   }
   ```

### Files Modified
- `src/mcp/claude_compatible_server.py` - Added prompts capability and handler

## ✅ Test Results
- **Docker Build**: Success
- **Local Testing**: All tests passing
- **MCP Initialize**: Returns prompts capability ✅
- **Prompts List**: Returns empty array ✅
- **Version**: Correctly shows 0.6.1 ✅

## 🚀 Deployment
This hotfix will be automatically deployed to Railway upon push to main branch.

## 📝 Notes
This is a critical fix that enables Claude.ai integration. The MCP 2025-03-26 protocol requires both tools and prompts capabilities to be declared for full compatibility.

---

*🤖 Generated with [Claude Code](https://claude.ai/code)*