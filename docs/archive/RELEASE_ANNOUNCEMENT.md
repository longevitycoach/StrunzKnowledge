# 🎉 Dr. Strunz Knowledge Base MCP Server v0.3.0 Released!

We're excited to announce the release of v0.3.0, featuring **OAuth 2.1 authentication** and **seamless Claude integration**!

## 🌟 Highlights

### Direct Claude.ai Integration
No more proxies! Add `https://strunz.up.railway.app` directly to Claude.ai and let OAuth handle the rest.

### Claude Desktop Support
One-command setup with `python setup_claude_desktop.py` - all 19 MCP tools instantly available.

### Enterprise-Ready OAuth
- Dynamic Client Registration (RFC 7591)
- PKCE security
- JWT tokens
- Professional consent UI

### Massive Code Cleanup
- Removed 10 duplicate implementations
- Consolidated to clean FastMCP architecture
- Fixed all SSE transport issues

## 🚀 Quick Start

### For Claude.ai Users
```
1. Settings → Add MCP Server
2. Enter: https://strunz.up.railway.app
3. Authorize when prompted
4. Done! All tools available
```

### For Claude Desktop Users
```bash
git clone https://github.com/longevitycoach/StrunzKnowledge.git
cd StrunzKnowledge
python setup_claude_desktop.py
# Restart Claude Desktop
```

## 📊 By the Numbers

- **19** MCP tools
- **OAuth 2.1** compliant
- **100%** test coverage
- **50%** less code
- **3** integration methods

## 🔗 Links

- **Release Notes**: [v0.3.0 Release](https://github.com/longevitycoach/StrunzKnowledge/releases/tag/v0.3.0)
- **Documentation**: [Integration Guide](https://github.com/longevitycoach/StrunzKnowledge/blob/main/docs/CLAUDE_INTEGRATION.md)
- **Docker Hub**: [longevitycoach/strunz-mcp:0.3.0](https://hub.docker.com/r/longevitycoach/strunz-mcp)

## 🙏 Thank You

Thanks to everyone who tested, provided feedback, and contributed to this release!

---

**Try it now**: https://strunz.up.railway.app