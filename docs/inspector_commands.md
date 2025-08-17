# MCP Inspector Commands for Local Development

## 🌐 Web UI Method (Easiest)

The MCP Inspector web UI is running at:
```
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=db5a5f60c40c3bd00f3daa3d00429a8e0227eae870a6ed738db4ce763119d78d
```

**Configuration in Web UI:**
- **Transport**: stdio
- **Command**: python
- **Args**: ["src/mcp/mcp_sdk_clean.py"]
- **Working Directory**: /Users/ma3u/projects/StrunzKnowledge
- **Environment Variables**: 
  - LOG_LEVEL=DEBUG
  - VECTOR_DB_TYPE=faiss

## 📋 What to Test in Inspector

1. **Connection**: Does it connect successfully?
2. **Server Info**: Check name, version, capabilities
3. **Tools**: List all available tools (should see 24)
4. **Tool Execution**: Test individual tools
5. **Resources**: Check if resources are available
6. **Prompts**: View available prompts

## 🔍 Key Things to Verify

### Capabilities Check
Your local v1.11.0 should show:
- ✅ `tools`: Tool calling capability
- ✅ `prompts`: Prompt templates
- ✅ `experimental`: Advanced features
- ❓ `resources`: This is what we're testing for Claude.ai

### Tools Count
Should show **24 tools** including:
- get_mcp_server_purpose
- knowledge_search
- create_health_protocol
- analyze_supplement_stack
- etc.

### Version Comparison
- Local: v1.11.0 (latest development)
- Railway: v1.0.0 (needs update)

## 🚨 Troubleshooting

If connection fails:
1. Make sure you're in the right directory
2. Check Python path is correct
3. Verify dependencies are installed
4. Try running the server manually first:
   ```bash
   python src/mcp/mcp_sdk_clean.py
   ```

## 🎯 Testing Goals

Use the Inspector to verify:
1. **All tools work correctly**
2. **Resource capability is reported**
3. **Protocol compliance**
4. **Error handling**

This will help us understand what Claude.ai expects vs what we're providing!