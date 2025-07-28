# Claude.ai Integration Solution Guide

## Problem Summary

You're experiencing an error in Claude.ai where the MCP server tools are now visible, but when trying to use them, you get:
```
Error executing tool: KnowledgeSearcher.search() got an unexpected keyword argument 'filter_source'
```

## Root Cause Analysis

1. **Parameter Mismatch**: The `KnowledgeSearcher.search()` method expects a parameter named `sources`, but something (possibly Claude.ai's tool calling mechanism) is passing `filter_source`.

2. **Tool Definition Issue**: The basic `search_knowledge` tool only accepts `query` and `limit` parameters, but Claude.ai might be trying to add additional filtering parameters.

## Immediate Solution

Since v4 is currently working and deployed, here's the quickest fix:

### Option 1: Update Railway Deployment (Recommended)

The v4 implementation already has the correct parameter names. Make sure it's deployed:

```bash
# Verify current deployment
railway logs --service strunz-knowledge | grep "version"

# If not showing v4.0.0, redeploy
git add -A
git commit -m "fix: Ensure v4 implementation is deployed"
git push origin main
```

### Option 2: Use the Correct Tools in Claude.ai

When using the tools in Claude.ai:

1. **For basic search** (use `search_knowledge`):
   - Only provide `query` and optionally `limit`
   - Example: `search_knowledge(query="Vitamin D", limit=10)`

2. **For filtered search** (use `search_knowledge_advanced`):
   - Provide `query`, `content_types` (not `filter_source`), and optionally `limit`
   - Example: `search_knowledge_advanced(query="Vitamin D", content_types=["books"], limit=10)`

## Tool Usage Guide for Claude.ai

### Available Tools and Their Parameters

1. **search_knowledge**
   ```
   Parameters:
   - query: string (required) - Your search query
   - limit: integer (optional, default=10, max=50) - Number of results
   ```

2. **search_knowledge_advanced**
   ```
   Parameters:
   - query: string (required) - Your search query
   - content_types: list[string] (optional) - Filter by ["books", "news", "forum"]
   - limit: integer (optional, default=10, max=50) - Number of results
   ```

3. **get_book_content**
   ```
   Parameters:
   - book_title: string (required) - Book title or partial title
   - page_range: string (optional, default="1-5") - Page range like "10-15"
   ```

4. **search_news**
   ```
   Parameters:
   - query: string (required) - Your search query
   - limit: integer (optional, default=10, max=50) - Number of results
   ```

5. **get_health_stats**
   ```
   Parameters: None - Returns database statistics
   ```

## Debugging Steps

If the issue persists:

1. **Check Tool Exposure in Claude.ai**:
   - Go to your MCP settings in Claude.ai
   - Verify all 5 tools are listed
   - Check if the parameter descriptions match the above

2. **Test Basic Search First**:
   - Try: "Search for information about Vitamin D"
   - Claude.ai should use `search_knowledge` with just the query

3. **Monitor Railway Logs**:
   ```bash
   railway logs --service strunz-knowledge --tail
   ```
   Watch for the exact parameters being passed when Claude.ai calls the tools.

## Enhanced Error Handling (Future Improvement)

The v7 implementation I created includes:
- Better parameter validation
- Detailed error messages
- Graceful handling of unexpected parameters
- Comprehensive logging

To deploy v7 when ready:
```bash
./deploy_v7_fix.sh
```

## Workaround for Current Session

If you need to search with filtering right now in Claude.ai, you can ask:
- "Search for Vitamin D in books only" → Claude should use `search_knowledge_advanced`
- "Search news articles about Omega 3" → Claude should use `search_news`
- "Get statistics about the knowledge base" → Claude should use `get_health_stats`

## Long-term Solution

The issue appears to be a mismatch between what Claude.ai expects and what our tools provide. The v7 implementation addresses this with:

1. **Flexible Parameter Handling**: Ignores unexpected parameters
2. **Better Error Messages**: Clear feedback when something goes wrong
3. **Validation**: Ensures all inputs are properly validated
4. **Logging**: Detailed logs for debugging

## Verification Steps

1. **Check Current Deployment**:
   ```bash
   curl https://strunz.up.railway.app/health | jq .
   ```
   Should show version 4.0.0 or higher.

2. **Test Tool Functionality**:
   In Claude.ai, try these exact prompts:
   - "What are the health statistics of the Strunz knowledge base?"
   - "Search for information about magnesium"
   - "Search for protein information in books only"

3. **Monitor Logs**:
   Keep Railway logs open while testing to see exact error messages.

## Contact Support

If the issue persists after trying these solutions:
1. Check if other MCP servers work in Claude.ai
2. Try removing and re-adding the Strunz server in Claude.ai settings
3. Clear Claude.ai cache/cookies and try again