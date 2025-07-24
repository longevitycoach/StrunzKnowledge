# FastMCP to Official MCP SDK Migration Plan

## Overview
This document tracks the migration from FastMCP to the Official MCP SDK for the StrunzKnowledge server.

## Migration Status

### Tool Migration Progress

#### ✅ Batch 1: Simple Tools (Completed)
1. **knowledge_search** - Basic search functionality
2. **find_contradictions** - Topic contradiction analysis
3. **trace_topic_evolution** - Topic evolution tracking
4. **create_health_protocol** - Protocol generation
5. **analyze_supplement_stack** - Supplement analysis
6. **nutrition_calculator** - Nutrition calculations
7. **summarize_posts** - Post summarization
8. **get_health_assessment_questions** - Assessment questions
9. **get_dr_strunz_biography** - Biography information
10. **get_mcp_server_purpose** - Server information
11. **get_vector_db_analysis** - Database analysis

#### ✅ Batch 2: Medium Complexity Tools (Completed)
12. **compare_approaches** - Approach comparison
13. **get_community_insights** - Community insights
14. **get_trending_insights** - Trending analysis
15. **get_guest_authors_analysis** - Guest author analysis
16. **get_optimal_diagnostic_values** - Diagnostic values

#### ✅ Batch 3: Complex Tools (Completed)
17. **analyze_strunz_newsletter_evolution** - Newsletter evolution analysis
18. **track_health_topic_trends** - Health topic trend tracking
19. **assess_user_health_profile** - User profile assessment
20. **create_personalized_protocol** - Personalized protocol creation
21. **get_dr_strunz_info** - Comprehensive Dr. Strunz information

## Tool Details

### Complete Tool List from enhanced_server.py

| # | Tool Name | Parameters | Complexity | Status |
|---|-----------|------------|------------|--------|
| 1 | knowledge_search | query, sources, limit, filters, user_profile | Simple | ✅ |
| 2 | find_contradictions | topic, include_reasoning, time_range | Simple | ✅ |
| 3 | trace_topic_evolution | topic, start_year, end_year, include_events | Simple | ✅ |
| 4 | create_health_protocol | condition, user_profile, severity, include_alternatives | Medium | ✅ |
| 5 | compare_approaches | health_issue, alternative_approaches, criteria | Medium | 🚧 |
| 6 | analyze_supplement_stack | supplements, health_goals, user_profile, check_interactions | Medium | ✅ |
| 7 | nutrition_calculator | age, gender, weight, height, activity_level, health_goals, dietary_preferences | Simple | ✅ |
| 8 | get_community_insights | topic, min_engagement, user_role, time_period | Medium | 🚧 |
| 9 | summarize_posts | category, limit, timeframe, user_profile | Simple | ✅ |
| 10 | get_trending_insights | days, user_role, categories | Medium | 🚧 |
| 11 | analyze_strunz_newsletter_evolution | timeframe, topic_focus | Simple | ✅ |
| 12 | get_guest_authors_analysis | timeframe, specialty_focus | Medium | 🚧 |
| 13 | track_health_topic_trends | topic, timeframe, include_context | Simple | ✅ |
| 14 | get_health_assessment_questions | user_role, assessment_depth | Simple | ✅ |
| 15 | get_structured_recommendations | health_goals, user_profile, priority_order | Complex | ⏳ |
| 16 | get_optimal_diagnostic_values | age, gender, weight, height, athlete, conditions, category | Medium | 🚧 |
| 17 | get_dr_strunz_philosophy | topic, format | Complex | ⏳ |
| 18 | get_dr_strunz_info | info_type | Simple | ✅ |
| 19 | get_mcp_server_purpose | _(none)_ | Simple | ✅ |
| 20 | get_vector_db_analysis | _(none)_ | Simple | ✅ |

## Migration Strategy

### Phase 1: Tool Definition Migration ✅
- Convert FastMCP `@self.app.tool()` decorators to MCP SDK tool definitions
- Update input schemas to MCP SDK format
- Batch tools by complexity for incremental migration

### Phase 2: Handler Implementation ✅
- Create handler methods for each tool
- Map tool names to handler functions
- Ensure parameter compatibility

### Phase 3: Testing & Validation 🚧
- Unit tests for each migrated tool
- Integration tests with actual vector store
- Performance comparison with FastMCP version

### Phase 4: Deployment ⏳
- Replace FastMCP server with SDK version
- Update deployment scripts
- Monitor for issues

## Key Differences

### FastMCP vs Official SDK

| Aspect | FastMCP | Official SDK |
|--------|---------|--------------|
| Tool Definition | Decorator-based | Schema-based |
| Parameter Handling | Function arguments | Dictionary arguments |
| Server Creation | `FastMCP()` | `Server()` + handlers |
| Transport | Built-in HTTP/SSE | stdio/custom |
| Error Handling | Automatic | Manual |

## Implementation Notes

### Tool Schema Format
```python
# FastMCP format
@self.app.tool()
async def tool_name(param1: str, param2: int = 10) -> Dict:
    """Tool description"""
    pass

# Official SDK format
types.Tool(
    name="tool_name",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "integer", "description": "...", "default": 10}
        },
        "required": ["param1"]
    }
)
```

### Handler Pattern
```python
@self.server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    if name == "tool_name":
        return await self._handle_tool_name(arguments)
```

## Next Steps

1. Complete Batch 2 tool handler implementations
2. Implement Batch 3 complex tools
3. Create comprehensive test suite
4. Update deployment configuration
5. Deprecate FastMCP dependencies