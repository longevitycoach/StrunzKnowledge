# FastMCP Audit Spreadsheet - Issue #6

## Overview
Comprehensive audit of all FastMCP usage in the StrunzKnowledge project for elimination planning.

## Tool Inventory (20 Tools Total)

| # | Tool Name | Location | Line | Function Signature | Complexity | Batch | Dependencies |
|---|-----------|----------|------|-------------------|------------|-------|--------------|
| 1 | `knowledge_search` | enhanced_server.py | 903 | `(query: str, sources: Optional[List[str]] = None)` | Medium | Batch 1 | RAG system |
| 2 | `find_contradictions` | enhanced_server.py | 926 | `(topic: str, include_reasoning: bool = True)` | Complex | Batch 3 | RAG system, analysis |
| 3 | `trace_topic_evolution` | enhanced_server.py | 940 | `(topic: str, start_year: Optional[int] = None)` | Complex | Batch 3 | RAG system, time analysis |
| 4 | `create_health_protocol` | enhanced_server.py | 954 | `(condition: str, user_profile: Optional[Dict] = None)` | Complex | Batch 4 | User profiling, RAG |
| 5 | `compare_approaches` | enhanced_server.py | 969 | `(health_issue: str, alternative_approaches: List[str])` | Medium | Batch 2 | RAG system |
| 6 | `analyze_supplement_stack` | enhanced_server.py | 982 | `(supplements: List[str], health_goals: List[str])` | Complex | Batch 4 | RAG system, analysis |
| 7 | `nutrition_calculator` | enhanced_server.py | 996 | `(age: int, gender: str, ...)` | Medium | Batch 2 | Math calculations |
| 8 | `get_community_insights` | enhanced_server.py | 1013 | `(topic: str, min_engagement: int = 5)` | Medium | Batch 2 | Forum data |
| 9 | `summarize_posts` | enhanced_server.py | 1027 | `(category: str, limit: int = 10)` | Simple | Batch 1 | Forum data |
| 10 | `get_trending_insights` | enhanced_server.py | 1041 | `(days: int = 30, user_role: Optional[str] = None)` | Medium | Batch 2 | Forum data, trending |
| 11 | `analyze_strunz_newsletter_evolution` | enhanced_server.py | 1054 | `(timeframe: str = "all", topic_focus: Optional[str] = None)` | Complex | Batch 3 | Time series analysis |
| 12 | `get_guest_authors_analysis` | enhanced_server.py | 1066 | `(timeframe: str = "all", specialty_focus: Optional[str] = None)` | Medium | Batch 2 | Author analysis |
| 13 | `track_health_topic_trends` | enhanced_server.py | 1078 | `(topic: str, timeframe: str = "5_years")` | Complex | Batch 3 | Trend analysis |
| 14 | `get_health_assessment_questions` | enhanced_server.py | 1091 | `(user_role: Optional[str] = None, assessment_depth: str = "comprehensive")` | Simple | Batch 1 | Question templates |
| 15 | `assess_user_health_profile` | enhanced_server.py | 1105 | `(responses: Dict[str, Any], include_recommendations: bool = True)` | Complex | Batch 4 | User profiling |
| 16 | `create_personalized_protocol` | enhanced_server.py | 1119 | `(user_profile: Dict, primary_concern: Optional[str] = None)` | Complex | Batch 4 | User profiling, protocols |
| 17 | `get_dr_strunz_biography` | enhanced_server.py | 1134 | `(include_achievements: bool = True, include_philosophy: bool = True)` | Simple | Batch 1 | Static content |
| 18 | `get_mcp_server_purpose` | enhanced_server.py | 1146 | `() -> Dict` | Simple | Batch 1 | Static content |
| 19 | `get_vector_db_analysis` | enhanced_server.py | 1155 | `() -> Dict` | Simple | Batch 1 | Vector store info |
| 20 | `get_optimal_diagnostic_values` | enhanced_server.py | 1164 | `(age: int, gender: str, ...)` | Medium | Batch 2 | Health calculations |

## Migration Batches

### Batch 1: Simple Tools (5 tools)
**Complexity**: Low  
**Risk**: Minimal  
**Tools**: knowledge_search, summarize_posts, get_health_assessment_questions, get_dr_strunz_biography, get_mcp_server_purpose, get_vector_db_analysis

### Batch 2: Medium Tools (5 tools)  
**Complexity**: Medium  
**Risk**: Low to Medium  
**Tools**: compare_approaches, nutrition_calculator, get_community_insights, get_trending_insights, get_guest_authors_analysis, get_optimal_diagnostic_values

### Batch 3: Complex Analysis Tools (5 tools)
**Complexity**: High  
**Risk**: Medium  
**Tools**: find_contradictions, trace_topic_evolution, analyze_strunz_newsletter_evolution, track_health_topic_trends

### Batch 4: User Profile Tools (5 tools)
**Complexity**: High  
**Risk**: High (User Profiling Dependency)  
**Tools**: create_health_protocol, analyze_supplement_stack, assess_user_health_profile, create_personalized_protocol

## FastMCP Import Analysis

### Primary Imports
```python
from fastmcp import FastMCP  # Line 16 in enhanced_server.py
```

### FastMCP Initialization
```python
class StrunzKnowledgeMCP:
    def __init__(self):
        # ... other init code ...
        if FASTMCP_AVAILABLE:
            self.app = FastMCP(title="Dr. Strunz Knowledge Base")
            self._register_tools()
```

### Tool Registration Pattern
```python
@self.app.tool()
async def tool_name(parameters):
    """Tool documentation"""
    # Tool implementation
    return result
```

## OAuth Integration Points

### FastMCP Web Server
- **File**: `enhanced_server.py`
- **Method**: `create_fastapi_app()`
- **OAuth Handler**: Uses `claude_ai_oauth_handler.py`
- **Endpoints**: `/`, `/sse`, `/api/organizations/{org_id}/mcp/start-auth/{auth_id}`

## Critical Dependencies

### User Profiling System
- **File**: `src/mcp/user_profiling.py`
- **Usage**: Tools 4, 15, 16 (create_health_protocol, assess_user_health_profile, create_personalized_protocol)
- **Risk**: High - Complex system for personalization

### RAG System
- **Files**: `src/rag/search.py`, `src/rag/vector_store.py`
- **Usage**: Most search and analysis tools
- **Risk**: Medium - Core functionality

### Forum Data Access
- **Usage**: Tools 8, 9, 10 (community and trending insights)
- **Risk**: Low - Data access patterns

## Migration Strategy

### Phase 2A: Batch 1 (Week 3, Day 1-2)
- Migrate 5 simple tools
- Establish Official SDK patterns
- Test with MCP Inspector

### Phase 2A: Batch 2 (Week 3, Day 3-4)  
- Migrate 5 medium complexity tools
- Validate calculation and data tools
- Performance testing

### Phase 2B: Batch 3 (Week 4, Day 1-2)
- Migrate complex analysis tools
- Focus on time series and trend analysis
- Heavy testing required

### Phase 2B: Batch 4 (Week 4, Day 3-4)
- Migrate user profiling tools
- Most risky batch
- Extensive validation needed

## Success Criteria per Batch
- [ ] All tools in batch successfully registered with Official SDK
- [ ] MCP Inspector validates all tool signatures
- [ ] Performance remains equivalent or better
- [ ] No functionality regression
- [ ] Error handling preserved