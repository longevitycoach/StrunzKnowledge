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

## Project Structure and Development Guidelines

### Project Organization
- **Do not create scripts in the root file**
- **Create scripts in:**
  - `src/scripts/` for main scripts
  - `src/test/` for test scripts
- **Create documentation as markdown (.md) files in the `docs/` folder**

## Test Reports and Development Guidance

### Test Report Guidelines
- **All Test Reports need a comprehensive test coverage of all MCPO capabilities.**
- **Positive and negative tests must be implemented for all roles, use cases, and user journeys.**

### Deployment Guidelines
- Always run all tests locally in docker first, before checking in the code
- Exceptions: documentation and tests do not require docker testing
- Configure Railway to not deploy with tests or documentation changes

### GitHub Release Guidelines
- **MANDATORY**: Every time you create a git tag (e.g., v0.7.5), you MUST create a corresponding GitHub release
- **Command**: Use `gh release create` immediately after pushing tags
- **Format**: Include comprehensive release notes with:
  - Title summarizing the main change
  - What's New/Fixed section
  - Testing evidence or results
  - Technical details of changes
  - Breaking changes (if any)
- **Example**:
  ```bash
  git tag -a v0.7.5 -m "Short description"
  git push origin v0.7.5
  gh release create v0.7.5 --title "v0.7.5: Main Feature" --notes "## What's New..."
  ```

### Release Version Synchronization
- **MANDATORY**: When creating a new release, update version numbers in ALL target systems
- **CRITICAL**: The version shown at https://strunz.up.railway.app/ comes from `src/mcp/claude_compatible_server.py` (health_check function)
- **Automated Update Script**: Use `python src/scripts/update_version.py X.Y.Z` to update all versions
- **Files automatically updated**:
  - `railway-deploy.py` - Main Railway deployment script
  - `src/scripts/deployment/railway_claude_ai_compatible.py` - All version references
  - `src/scripts/deployment/railway_official_mcp_server.py`
  - `src/scripts/deployment/railway_mcp_fixed.py`
  - `src/mcp/claude_compatible_server.py` - All version references (CRITICAL for production endpoint)
  - `src/mcp/enhanced_server.py`
  - `src/mcp/mcp_sdk_clean.py`
- **Manual update if needed**:
  - `Dockerfile` (if version is referenced)
  - `README.md` (if version is displayed)
- **Use consistent version format**: `0.7.X` (not `v0.7.X` in code)
- **Verify before committing**: Run `grep -r "0\\.7\\.[0-9]" src/ railway-deploy.py | grep -v test`

### Docker Package Description Guidelines
- **MANDATORY**: ALWAYS provide descriptions for Docker packages in GitHub Container Registry
- **Location**: Package descriptions are set via Dockerfile LABEL instructions (OCI-compliant)
- **Required Labels in Dockerfile**:
  ```dockerfile
  LABEL org.opencontainers.image.title="StrunzKnowledge MCP Server"
  LABEL org.opencontainers.image.description="Dr. Strunz Knowledge Base MCP Server - A comprehensive health and nutrition knowledge system based on Dr. Ulrich Strunz's work. Provides semantic search across 13 books, 6,953 news articles, and forum content via the Model Context Protocol (MCP) for Claude Desktop and Claude.ai integration."
  LABEL org.opencontainers.image.authors="longevitycoach"
  LABEL org.opencontainers.image.source="https://github.com/longevitycoach/StrunzKnowledge"
  LABEL org.opencontainers.image.documentation="https://github.com/longevitycoach/StrunzKnowledge/blob/main/README.md"
  LABEL org.opencontainers.image.licenses="MIT"
  LABEL org.opencontainers.image.vendor="longevitycoach"
  LABEL org.opencontainers.image.url="https://strunz.up.railway.app"
  LABEL org.opencontainers.image.version="0.7.8"
  ```
- **Update Process**: Update these labels whenever creating a new release
- **Verification**: Check package at https://github.com/longevitycoach/StrunzKnowledge/pkgs/container/strunzknowledge/
- **Cleanup Scripts**: Use `src/scripts/cleanup_dockerhub_versions.sh` to maintain clean registry (keep only latest 5 versions)

## MCP Claude.ai Integration - COMPLETE REWRITE ✅

### Version 2.0.0 Solution (2025-07-28)
Complete rewrite using official MCP Python SDK. All issues resolved.

### Architecture Changes

1. **Official MCP SDK Implementation**:
   - Removed all custom FastAPI/SSE implementations
   - Using `mcp` Python package for server logic
   - Clean separation of concerns (server vs transport)

2. **Transport Layer**:
   - STDIO transport for Claude Desktop (mcp_server_clean.py)
   - SSE/HTTP transport for Claude.ai (sse_server.py with Starlette)
   - Unified main.py entry point handles both transports

3. **Key Files**:
   - `src/mcp/mcp_server_clean.py` - Core MCP server using official SDK
   - `src/mcp/sse_server.py` - SSE transport wrapper
   - `main.py` - Unified entry point
   - `test_sse_flow.py` - SSE testing script
   - `src/tests/test_mcp_comprehensive.py` - Full test suite
   - `src/tests/test_mcp_inspector.py` - MCP Inspector compatibility tests

### Solution Summary (2025-07-22)
Claude.ai integration is now fully functional with OAuth 2.1 support and all 8 tools exposed.

### Key Fixes Implemented:

1. **OAuth Flow Implementation**:
   - Added `/api/organizations/{org_id}/mcp/start-auth/{auth_id}` endpoint
   - Implemented OAuth callback handler at `/api/mcp/auth_callback`
   - Added POST handlers for `/` and `/sse` endpoints
   - Support for both simplified (no OAuth) and full OAuth modes

2. **Tool Exposure Fix**:
   - Fixed FastMCP FunctionTool extraction issue
   - All 20 tools now properly exposed via `tool_info.fn` attribute
   - 97% test success rate (32/33 tests passing)

3. **Authentication Modes**:
   - **Simplified Mode** (Default): `CLAUDE_AI_SKIP_OAUTH=true`
   - **Full OAuth Mode**: Complete OAuth 2.1 flow with Dynamic Client Registration

### OAuth Flow Diagram:
```
Claude.ai → MCP Discovery → Start Auth → Skip OAuth (default) → Connected
                                      ↓
                                Full OAuth → Authorize → Callback → Token → Connected
```

### Implementation Details:

#### 1. Claude.ai Start Auth Endpoint
```python
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(org_id: str, auth_id: str, redirect_url: Optional[str] = Query(None)):
    # Store client info
    client_id = f"claude_{auth_id[:16]}"
    
    # Check if OAuth should be skipped
    if os.environ.get("CLAUDE_AI_SKIP_OAUTH", "false").lower() == "true":
        return JSONResponse({
            "status": "success",
            "auth_not_required": True,
            "server_url": "https://strunz.up.railway.app"
        })
    
    # Otherwise redirect to OAuth flow
    return RedirectResponse(url=oauth_url, status_code=302)
```

#### 2. OAuth Callback Handler
```python
@app.get("/api/mcp/auth_callback")
async def claude_ai_oauth_callback(code: str = Query(None), state: str = Query(None)):
    # Return success HTML with postMessage for iframe communication
    return HTMLResponse(f'''
        <script>
            if (window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'mcp-oauth-success',
                    code: '{code}',
                    state: '{state}'
                }}, '*');
            }}
        </script>
        <h1>✓ Successfully Connected!</h1>
    ''')
```

### Previous Issue Analysis (2025-07-18)
Claude.ai was returning "not_available" error due to:
1. Missing Claude.ai specific endpoints
2. 405 Method Not Allowed on POST to `/`
3. FastMCP FunctionTool wrapper preventing tool exposure

### Testing Plan

#### Phase 1: Official MCP Client Testing
1. **Install Official Python MCP SDK**
   ```bash
   pip install mcp
   ```

2. **Create Test Client Script**
   - Use official MCP client to connect to our server
   - Test OAuth2 authentication flow
   - Verify tool listing and execution
   - Document any missing endpoints or methods

3. **Test Transport Types**
   - SSE (Server-Sent Events) - Currently implemented
   - HTTP/REST - Currently implemented
   - stdio - Used by Claude Desktop (local only)
   - WebSocket - Not implemented

#### Phase 2: Claude.ai Specific Requirements
1. **Analyze Claude.ai Requests**
   - Monitor all incoming requests from Claude.ai
   - Document the exact API flow Claude.ai expects
   - Identify proprietary endpoints like `/api/organizations/.../mcp/start-auth/...`

2. **Implement Missing Endpoints**
   - Add Claude.ai specific endpoints if needed
   - Maintain compatibility with standard MCP

#### Phase 3: Authentication Investigation
1. **OAuth2 vs API Key**
   - Claude.ai might expect API key authentication
   - Test if OAuth2 is actually used or just for show

2. **Discovery Endpoints**
   - Verify `.well-known/mcp/resource` format
   - Check if additional discovery endpoints are needed

### Implementation Strategy

#### Option 1: Add Claude.ai Compatibility Layer
```python
# Add Claude.ai specific endpoints
@app.get("/api/organizations/{org_id}/mcp/start-auth/{auth_id}")
async def claude_ai_start_auth(org_id: str, auth_id: str):
    # Redirect to standard OAuth flow
    return RedirectResponse("/oauth/authorize?...")
```

#### Option 2: Use Different Transport
- Claude.ai might only work with stdio transport (local)
- HTTP/SSE might be for different use cases

#### Option 3: Contact Anthropic Support
- The "not_available" error might indicate server registration issue
- May need to register our server with Anthropic

### Testing Commands

```bash
# Test SSE endpoint locally
python test_sse_flow.py

# Run comprehensive MCP test suite
python src/tests/test_mcp_comprehensive.py

# Test MCP Inspector compatibility
python src/tests/test_mcp_inspector.py

# Monitor Railway logs
railway logs --service strunz-knowledge
```

### Success Criteria (v2.0.0) ✅
- [x] SSE transport working with session management
- [x] All 8 tools properly exposed with complete schemas
- [x] MCP Inspector can connect and execute tools
- [x] Railway deployment successful
- [x] No "not_available" errors
- [x] Protocol version 2025-11-05 compliance

## Development Notes and Warnings

### SDK and Library Guidance
- **Dont use FastMCP use the official MCP SDK for Python**: https://github.com/modelcontextprotocol/python-sdk

## CLI Commands and Deployment Guidance

### Railway CLI Commands
- **Check Build Errors**: `railway logs --service strunz-knowledge`
- **Check Deployment Errors**: `railway logs --deployment`
- **Run Specific Service Logs**: `railway logs --service <service-name>`
- **Check Latest Release Endpoint**:
  - Local: `http://localhost:3000`
  - Docker: `http://localhost:8080`
  - Railway Production: `https://strunz.up.railway.app`
```

## BMAD Method Integration (Brownfield Approach)

### Overview
This project follows the BMAD (Business Methodology for AI Development) method for brownfield projects. BMAD is an agentic AI development framework that uses specialized AI agents for planning, architecture, and development phases.

### BMAD Implementation for StrunzKnowledge

#### 1. Agentic Planning Phase
- **Analyst Agent**: Reviews existing codebase and documentation
- **PM Agent**: Creates/updates PRDs based on current state
- **Architect Agent**: Designs solutions respecting existing architecture

#### 2. Context-Engineered Development
- **Scrum Master Agent**: Transforms plans into detailed development stories
- Stories embed full context including:
  - Current implementation details
  - Technical debt considerations
  - Migration path specifications
  - Testing requirements

#### 3. Brownfield-Specific Considerations
- **Existing Documentation**: See `docs/brownfield-architecture/` and `docs/brownfield-prd/`
- **Technical Debt**: Documented in `docs/brownfield-architecture/technical-debt-issues.md`
- **Migration Strategy**: FastMCP to Official MCP SDK (Epic #1)
- **Incremental Approach**: Apply BMAD to specific components/epics

### BMAD Workflow for This Project

1. **Before Starting Work**:
   - Review brownfield documentation in `docs/brownfield-*`
   - Understand current architecture and technical debt
   - Check related GitHub issues and project board

2. **During Development**:
   - Follow hyper-detailed story specifications
   - Maintain context consistency across changes
   - Update brownfield documentation as needed
   - Create GitHub issues for discovered problems

3. **Testing & Validation**:
   - Follow comprehensive test coverage requirements
   - Validate against existing functionality
   - Ensure no regression in Claude.ai integration

### References
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD
- YouTube Masterclass: [Link to be added]
- Project Board: https://github.com/orgs/longevitycoach/projects/2

## Memories and Best Practices

### Workflow Recommendations
- **ALWAYS check context7 before you search to the internet**