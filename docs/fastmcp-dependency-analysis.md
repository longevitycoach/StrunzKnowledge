# FastMCP Dependency Analysis - Issue #6

## Critical FastMCP Dependencies Identified

### 1. Core Server Implementation
**File**: `src/mcp/enhanced_server.py`
- **Line 16**: `from fastmcp import FastMCP`
- **Line 106**: `self.app = FastMCP("Dr. Strunz Knowledge Base")`
- **Status**: CRITICAL - Core functionality depends on FastMCP

### 2. Production Deployment (ACTIVE)
**File**: `railway-deploy.py`
- **Line 40**: References FastMCP tool extraction fixes
- **Status**: PRODUCTION DEPENDENCY - Currently deployed

**File**: `src/mcp/unified_mcp_server.py`
- **Lines 488-492**: FastMCP FunctionTool extraction logic
- **Lines 543-547**: FastMCP tool handling
- **Status**: PRODUCTION CRITICAL - Root cause of "Disabled" status

### 3. Claude Desktop Integration
**File**: `claude_desktop_stdio_server.py`
- **FastMCP stdio mode handling**
- **Status**: LOCAL INTEGRATION - Affects Claude Desktop users

**File**: `src/scripts/setup/claude_desktop_local_proxy.py`
- **Line 9**: `from fastmcp import FastMCP`
- **Line 12**: `app = FastMCP("Strunz Knowledge Proxy")`
- **Status**: PROXY INTEGRATION - 10 tools defined

### 4. Requirements Files
**Files with FastMCP dependencies**:
- `requirements-prod.txt` (Line 16): `fastmcp==0.1.0`
- `requirements-flexible.txt` (Line 21): `fastmcp>=0.1.0`
- `requirements.txt`: FastMCP explicitly excluded (commented out)

## OAuth Integration Impact

### FastMCP Web Server Integration
**File**: `src/mcp/enhanced_server.py`
- **Method**: `create_fastapi_app()` (Line ~1651)
- **SSE Transport**: FastMCP SSE server integration
- **OAuth Handlers**: Integrates with `claude_ai_oauth_handler.py`

### OAuth Endpoints
- `/`: Health check with FastMCP compatibility
- `/sse`: Server-sent events transport
- `/api/organizations/{org_id}/mcp/start-auth/{auth_id}`: Claude.ai specific

## Testing Infrastructure Impact

### Test Files Using FastMCP (21 files)
1. `test_enhanced_server_init.py` - FastMCP availability testing
2. `test_fastmcp_client.py` - Railway endpoint testing
3. `quick_fastmcp_test.py` - Basic connection testing
4. `test_mcp_sdk.py` - SDK comparison testing
5. `test_fastmcp_local.py` - Local transport testing
6. `fastmcp_comprehensive_test.py` - Full functionality testing
7. `test_unified_server_tools.py` - Tool extraction testing
8. Multiple other test files reference FastMCP patterns

## Migration Risk Assessment

### HIGH RISK Components
1. **unified_mcp_server.py** - Production deployment
2. **enhanced_server.py** - Core server with 20 tools  
3. **OAuth integration** - Complex authentication flow
4. **Tool extraction logic** - FastMCP FunctionTool handling

### MEDIUM RISK Components
1. **Claude Desktop integration** - Local stdio server
2. **Proxy server** - 10 tool definitions
3. **Test infrastructure** - 21 test files affected

### LOW RISK Components
1. **Documentation references** - Easy to update
2. **Requirements files** - Simple dependency removal

## Tool Registration Pattern Analysis

### Current FastMCP Pattern
```python
@self.app.tool()
async def tool_name(parameters):
    """Tool documentation"""
    # Implementation
    return result
```

### Target Official SDK Pattern
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    if name == "tool_name":
        # Implementation 
        return [types.TextContent(type="text", text=json.dumps(result))]
```

## Dependencies Chain Analysis

### User Profiling Tools (4 tools - Batch 4)
- **Files**: `src/mcp/user_profiling.py`
- **Tools**: create_health_protocol, assess_user_health_profile, create_personalized_protocol, analyze_supplement_stack
- **Risk**: HIGHEST - Complex interdependencies

### RAG System Tools (Most tools)
- **Files**: `src/rag/search.py`, `src/rag/vector_store.py`
- **Tools**: knowledge_search, find_contradictions, trace_topic_evolution, etc.
- **Risk**: MEDIUM - Core functionality but established patterns

### Forum Data Tools (3 tools - Batch 2)
- **Tools**: get_community_insights, summarize_posts, get_trending_insights
- **Risk**: LOW - Simple data access patterns

## Critical Path Analysis

### Phase 2A Prerequisites
1. **MCP Inspector setup** (Issue #12) - REQUIRED for validation
2. **Performance baselines** - REQUIRED for comparison
3. **Feature flags implementation** - REQUIRED for rollback

### Phase 2A Implementation Order
1. **Batch 1**: Simple tools (5 tools) - Establish patterns
2. **Batch 2**: Medium tools (5 tools) - Validate patterns  
3. **Batch 3**: Complex tools (5 tools) - Test advanced features
4. **Batch 4**: User profiling (5 tools) - Highest risk last

### Phase 2B Validation Requirements
1. **All 20 tools** functional with Official SDK
2. **OAuth flow** preserved and working
3. **Performance** equal or better than FastMCP
4. **Claude.ai integration** shows "Connected" not "Disabled"

## Success Criteria

### Per-Batch Success Criteria
- [ ] All tools in batch register successfully with Official SDK
- [ ] MCP Inspector validates all tool signatures
- [ ] Performance meets or exceeds FastMCP baseline
- [ ] No functionality regression detected
- [ ] Error handling preserved and improved

### Overall Migration Success  
- [ ] Claude.ai status changes from "Disabled" to "Connected"
- [ ] Local Claude Desktop integration preserved
- [ ] All 20 tools discoverable and executable
- [ ] OAuth authentication flow functional
- [ ] Production deployment stable
- [ ] Test suite updated and passing