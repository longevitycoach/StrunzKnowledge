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
- **Files to update**:
  - `railway-deploy.py` - Main Railway deployment script
  - `src/scripts/deployment/railway_claude_ai_compatible.py` - All version references
  - `src/scripts/deployment/railway_official_mcp_server.py`
  - `src/scripts/deployment/railway_mcp_fixed.py`
  - `src/mcp/claude_compatible_server.py` - All version references
  - `src/mcp/enhanced_server.py`
  - `Dockerfile` (if version is referenced)
  - `README.md` (if version is displayed)
- **Use consistent version format**: `0.7.X` (not `v0.7.X` in code)
- **Verify before committing**: Run `grep -r "0\\.7\\.[0-9]" src/ railway-deploy.py | grep -v test`

## MCP Claude.ai Integration Investigation Plan

### Current Issue Analysis (2025-07-18)
Claude.ai returns "not_available" error when trying to add our MCP server. Investigation reveals:

1. **OAuth Flow Works**: `/oauth/authorize` returns 307 redirect correctly
2. **Tool Execution Works**: `tools/call` method executes properly
3. **Missing Endpoint**: Claude.ai tries to access `/api/organizations/{org_id}/mcp/start-auth/{auth_id}` which doesn't exist on our server

### Root Cause Hypothesis
Claude.ai might be using a proprietary API wrapper around standard MCP, expecting specific endpoints that aren't part of the official MCP specification.

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
# Test with official MCP client
python -m mcp.client connect https://strunz.up.railway.app

# Test OAuth flow manually
curl -X POST https://strunz.up.railway.app/oauth/register \
  -d '{"client_name": "Test Client", "redirect_uris": ["https://claude.ai/callback"]}'

# Monitor Railway logs
railway logs --service strunz-knowledge --tail
```

### Success Criteria
- [ ] Official MCP client can connect and execute tools
- [ ] Claude.ai can discover our server
- [ ] Claude.ai can authenticate (if needed)
- [ ] Claude.ai can list and execute tools
- [ ] No "not_available" errors