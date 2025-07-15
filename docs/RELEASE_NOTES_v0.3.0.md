# Release Notes - v0.3.0

**Release Date:** July 15, 2025  
**Version:** 0.3.0  
**Codename:** "Claude Integration"

## 🎯 Release Highlights

Dr. Strunz Knowledge Base MCP Server v0.3.0 brings revolutionary OAuth 2.1 authentication, enabling direct integration with Claude.ai without any local proxy requirements. This release also includes comprehensive Claude Desktop support, massive code cleanup, and extensive testing infrastructure.

## 🚀 What's New

### 1. OAuth 2.1 Authentication System

We've implemented a complete OAuth 2.1 provider that enables Claude.ai to connect directly to the Railway deployment:

- **Dynamic Client Registration (RFC 7591)**: Claude.ai can automatically register as a client
- **OAuth Discovery**: Standard-compliant metadata endpoint at `/.well-known/oauth-authorization-server`
- **PKCE Support**: Enhanced security with Proof Key for Code Exchange
- **JWT Tokens**: Secure, time-limited access tokens with refresh capability
- **Professional Consent Screen**: Clean UI for user authorization

**Impact**: Users can now add `https://strunz.up.railway.app` directly to Claude.ai, which will handle the OAuth flow automatically.

### 2. Claude Desktop Integration

For users who prefer Claude Desktop or don't have access to remote servers:

- **Local STDIO Proxy**: Converts Claude Desktop's STDIO protocol to HTTP requests
- **Automated Setup**: One-command setup with `python setup_claude_desktop.py`
- **Full Tool Access**: All 19 MCP tools available through the proxy
- **Zero Configuration**: Automatically configures Claude Desktop

**Usage**:
```bash
python setup_claude_desktop.py
# Restart Claude Desktop
# Done! All tools available
```

### 3. Enhanced Testing Infrastructure

Comprehensive testing suite for reliability:

- **Docker Testing**: Full container testing with SSE support
- **FastAgent Compatibility**: Tests using FastAgent-style MCP client
- **OAuth Flow Testing**: Complete OAuth 2.1 flow verification
- **MCP Inspector Support**: Protocol-level testing and debugging
- **Automated Test Reports**: Summary generation for all test runs

### 4. Major Code Cleanup

Significant codebase optimization:

- **Removed 10 Duplicate Files**: Eliminated redundant server implementations
- **Consolidated Architecture**: Single, clean FastMCP-based implementation
- **Fixed SSE Transport**: Proper FastMCP SSE configuration
- **Improved Error Handling**: Graceful fallbacks throughout

## 📊 Technical Specifications

### OAuth 2.1 Compliance

| Feature | Status | RFC |
|---------|--------|-----|
| Dynamic Client Registration | ✅ Implemented | RFC 7591 |
| Authorization Server Metadata | ✅ Implemented | RFC 8414 |
| PKCE | ✅ Implemented | RFC 7636 |
| Bearer Tokens | ✅ Implemented | RFC 6750 |
| Refresh Tokens | ✅ Implemented | RFC 6749 |

### Performance Metrics

- **OAuth Response Time**: < 100ms
- **Token Validation**: < 10ms
- **SSE Connection**: Instant
- **Memory Usage**: ~1.2GB (with FAISS loaded)
- **Docker Image Size**: ~1.5GB

### Security Features

- **CORS Protection**: Configured for Claude.ai domains only
- **Token Expiration**: 1 hour (configurable)
- **Refresh Token Lifetime**: 1 week
- **HTTPS Only**: Enforced in production
- **No Hardcoded Secrets**: Environment-based configuration

## 🔧 Breaking Changes

None! This release maintains full backward compatibility while adding new features.

## 🐛 Bug Fixes

1. **Fixed Claude.ai Connection Error**: Resolved "MCP error -32000: Connection closed"
2. **Fixed FAISS Index Loading**: Corrected path and file naming issues
3. **Fixed FastMCP SSE Parameters**: Removed unsupported host/port parameters
4. **Fixed Vector Store Initialization**: Proper error handling for missing indices
5. **Fixed Docker Port Conflicts**: Resolved duplicate port binding issues

## 📦 Installation & Upgrade

### Docker Deployment
```bash
docker pull longevitycoach/strunz-mcp:0.3.0
docker run -p 8000:8000 longevitycoach/strunz-mcp:0.3.0
```

### Railway Deployment
Automatic deployment on push to main branch. OAuth endpoints available at:
- https://strunz.up.railway.app/.well-known/oauth-authorization-server
- https://strunz.up.railway.app/oauth/authorize
- https://strunz.up.railway.app/oauth/token

### Local Development
```bash
git pull origin main
pip install -r requirements.txt
python main.py
```

## 🎯 Use Cases

### For Claude.ai Users
1. Open Claude.ai settings
2. Add MCP server: `https://strunz.up.railway.app`
3. Complete OAuth authorization
4. Access all 19 MCP tools directly

### For Claude Desktop Users
1. Run `python setup_claude_desktop.py`
2. Restart Claude Desktop
3. Tools appear automatically
4. No manual configuration needed

### For Developers
1. Clone the repository
2. Use `test_oauth_flow.py` for OAuth testing
3. Use `test_with_fast_agent.py` for MCP testing
4. Implement custom OAuth clients using our endpoints

## 📚 Documentation Updates

- **CLAUDE_INTEGRATION.md**: Complete integration guide
- **CHANGELOG.md**: Detailed change history
- **README.md**: Updated with OAuth information
- **Testing Guides**: Comprehensive test documentation

## 🙏 Credits

- **OAuth Implementation**: Based on OAuth 2.1 draft specifications
- **FastMCP Framework**: Excellent MCP protocol support
- **Community Feedback**: Invaluable testing and suggestions

## 📈 What's Next (v0.4.0 Preview)

- **Multi-language Support**: English interface for international users
- **Advanced Caching**: Redis integration for faster responses
- **Webhook Support**: Real-time updates for content changes
- **Admin Dashboard**: Web interface for server management
- **Extended OAuth Scopes**: Granular permission control

## 🔗 Resources

- **GitHub Repository**: [https://github.com/longevitycoach/StrunzKnowledge](https://github.com/longevitycoach/StrunzKnowledge)
- **Docker Hub**: [https://hub.docker.com/r/longevitycoach/strunz-mcp](https://hub.docker.com/r/longevitycoach/strunz-mcp)
- **Railway Deployment**: [https://strunz.up.railway.app](https://strunz.up.railway.app)
- **Issue Tracker**: [GitHub Issues](https://github.com/longevitycoach/StrunzKnowledge/issues)

## 📝 Migration Guide

No migration required! v0.3.0 is fully backward compatible. However, to take advantage of new features:

1. **Enable OAuth**: No action needed - automatically available
2. **Update Claude Desktop**: Run the new setup script
3. **Test OAuth Flow**: Use `test_oauth_flow.py` to verify

## ⚠️ Known Issues

1. **FAISS Indices**: Must be reconstructed during Docker build
2. **Memory Usage**: ~1.2GB baseline due to vector embeddings
3. **Claude.ai Plans**: Remote server support may require specific Claude.ai plan

## 📞 Support

- **Documentation**: See `/docs` directory
- **Issues**: [GitHub Issues](https://github.com/longevitycoach/StrunzKnowledge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/longevitycoach/StrunzKnowledge/discussions)

---

**Thank you for using Dr. Strunz Knowledge Base MCP Server!**

*This release represents months of development and testing. We're excited to see how you'll use these new features to access Dr. Strunz's health knowledge through AI interfaces.*