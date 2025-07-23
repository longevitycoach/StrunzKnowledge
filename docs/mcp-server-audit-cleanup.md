# MCP Server Implementation Audit - Issue #19

## Current State Analysis

### MCP Server Files in `src/mcp/`

| File | Status | Purpose | Action |
|------|--------|---------|--------|
| `__init__.py` | EMPTY | Package marker | **KEEP** |
| `mcp_sdk_clean.py` | ACTIVE | **TARGET**: Pure Official SDK implementation | **KEEP** - Primary server |
| `enhanced_server.py` | ACTIVE | Tool logic with FastMCP wrappers | **KEEP** - Until FastMCP removal |
| `unified_mcp_server.py` | DEPRECATED | Complex FastMCP extraction logic | **REMOVE** - Part of technical debt |
| `claude_compatible_server.py` | ACTIVE | Claude.ai OAuth compatibility | **EVALUATE** - Check if needed |
| `official_mcp_server.py` | UNKNOWN | Unknown purpose/usage | **EVALUATE** - Check usage |
| `claude_ai_oauth_handler.py` | ACTIVE | OAuth handling for Claude.ai | **KEEP** - If used by main servers |
| `oauth_provider.py` | ACTIVE | OAuth provider implementation | **KEEP** - If used by main servers |
| `mcp_input_parser.py` | UTILITY | Input parsing utilities | **EVALUATE** - Check if used |
| `user_profiling.py` | FEATURE | User profiling functionality | **EVALUATE** - Check if used |
| `lightweight_embeddings.py` | FEATURE | Embedding functionality | **EVALUATE** - Check if used |

### Templates Directory
| File | Status | Action |
|------|--------|--------|
| `templates/oauth_consent.html` | ACTIVE | OAuth UI template | **KEEP** |

## Cleanup Plan

### Phase 1: File Usage Analysis
1. **Identify active imports** - Check which files are imported/used
2. **Check deployment scripts** - See which servers are deployed
3. **Review main.py** - Check server selection logic
4. **Check railway-deploy.py** - Confirm deployment server

### Phase 2: Safe Removal
1. **Confirmed for removal:**
   - `unified_mcp_server.py` - FastMCP wrapper (technical debt)
   
2. **Requires evaluation:**
   - `official_mcp_server.py` - Check if duplicate of mcp_sdk_clean.py
   - `claude_compatible_server.py` - May be obsolete after OAuth resolution
   - `mcp_input_parser.py` - Check usage in active servers
   - `user_profiling.py` - Check if used in current implementation
   - `lightweight_embeddings.py` - Check if used in current implementation

### Phase 3: Documentation Update
1. Update imports in remaining files
2. Update SCRIPTS.md to reflect removed servers
3. Update README.md if it references removed servers
4. Update deployment documentation

## Usage Analysis Results

### Active Servers (KEEP)
1. **`mcp_sdk_clean.py`** - PRIMARY target, used in main.py (Railway & local)
2. **`enhanced_server.py`** - Used as fallback in main.py (local), many test files
3. **`claude_compatible_server.py`** - Fallback in main.py (Railway), deployment scripts
4. **`unified_mcp_server.py`** - USED IN PRODUCTION! railway-deploy.py line 36

### Utility Files (EVALUATE)
1. **`claude_ai_oauth_handler.py`** - May be used by servers for OAuth
2. **`oauth_provider.py`** - May be used by servers for OAuth
3. **`user_profiling.py`** - Imported by enhanced_server.py line 126
4. **`lightweight_embeddings.py`** - Imported by vector_store.py line 21
5. **`mcp_input_parser.py`** - Used in test files

### Unknown Status
1. **`official_mcp_server.py`** - No direct imports found, may be obsolete

## CRITICAL FINDING
- **`unified_mcp_server.py` is CURRENTLY DEPLOYED in production via railway-deploy.py**
- Cannot remove until FastMCP elimination is complete
- This is the root cause of "Disabled" status in Claude.ai

## Revised Cleanup Plan

### Phase 1: Safe Removals Only
1. **`official_mcp_server.py`** - Appears to be duplicate/obsolete
2. **Deprecated test files** - Clean up old test scripts
3. **Documentation cleanup** - Remove outdated docs

### Phase 2: Post-FastMCP Elimination
1. **`unified_mcp_server.py`** - Remove after migration complete
2. **`enhanced_server.py`** - Clean FastMCP wrappers, keep tool logic
3. **Dependency cleanup** - Remove FastMCP from requirements.txt

## Immediate Actions
1. ✅ Document current usage
2. Remove `official_mcp_server.py` if truly unused
3. Clean up deprecated scripts and documentation
4. Update SCRIPTS.md with current state
5. Prepare for Phase 2 FastMCP work

## Expected Outcome
- **Reduced technical debt** (partial - major cleanup after FastMCP removal)
- **Clearer documentation**
- **Updated script inventory**
- **Ready for FastMCP elimination in Phase 2**