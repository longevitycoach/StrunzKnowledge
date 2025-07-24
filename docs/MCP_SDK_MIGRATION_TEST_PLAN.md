# MCP SDK Migration Test Plan

## Overview
This test plan ensures comprehensive validation of all 20 tools migrated from FastMCP to the Official MCP SDK.

## Test Environment Setup

### Prerequisites
1. **MCP SDK Installation**
   ```bash
   pip install mcp
   ```

2. **Vector Store Initialization**
   - Ensure FAISS index is loaded
   - Verify embeddings are available

3. **Test Modes**
   - **Local Testing**: Direct function calls
   - **MCP Protocol Testing**: Via stdio transport
   - **Integration Testing**: With Claude Desktop
   - **Production Testing**: Railway deployment

## Tool Categories and Test Coverage

### Category 1: Search & Analysis Tools (6 tools)
1. **knowledge_search**
2. **find_contradictions**
3. **trace_topic_evolution**
4. **analyze_strunz_newsletter_evolution**
5. **track_health_topic_trends**
6. **get_vector_db_analysis**

### Category 2: Protocol & Recommendation Tools (5 tools)
7. **create_health_protocol**
8. **analyze_supplement_stack**
9. **nutrition_calculator**
10. **create_personalized_protocol**
11. **get_optimal_diagnostic_values**

### Category 3: Community & Insights Tools (4 tools)
12. **get_community_insights**
13. **summarize_posts**
14. **get_trending_insights**
15. **get_guest_authors_analysis**

### Category 4: Assessment & Profile Tools (3 tools)
16. **get_health_assessment_questions**
17. **assess_user_health_profile**
18. **compare_approaches**

### Category 5: Information Tools (2 tools)
19. **get_dr_strunz_info**
20. **get_mcp_server_purpose**

## Test Cases

### TC-001: Tool Discovery
**Objective**: Verify all tools are properly exposed
```python
# Test script: test_tool_discovery.py
async def test_tool_discovery():
    server = StrunzKnowledgeServer()
    tools = await server.list_tools()
    assert len(tools) == 20
    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "knowledge_search", "find_contradictions", "trace_topic_evolution",
        "create_health_protocol", "analyze_supplement_stack", "nutrition_calculator",
        "summarize_posts", "get_health_assessment_questions", "get_dr_strunz_biography",
        "get_mcp_server_purpose", "get_vector_db_analysis", "compare_approaches",
        "get_community_insights", "get_trending_insights", "get_guest_authors_analysis",
        "get_optimal_diagnostic_values", "analyze_strunz_newsletter_evolution",
        "track_health_topic_trends", "assess_user_health_profile", 
        "create_personalized_protocol", "get_dr_strunz_info"
    ]
    for tool in expected_tools:
        assert tool in tool_names
```

### TC-002: Parameter Validation
**Objective**: Verify input schema validation
```python
# Test each tool with:
1. Valid parameters
2. Missing required parameters
3. Invalid parameter types
4. Extra parameters
```

### TC-003: Search Tools Testing
```python
# Test cases for knowledge_search
test_cases = [
    {
        "name": "knowledge_search",
        "args": {"query": "vitamin d optimal levels"},
        "validate": lambda r: "60-80 ng/ml" in str(r)
    },
    {
        "name": "find_contradictions",
        "args": {"topic": "protein intake"},
        "validate": lambda r: "contradiction" in str(r).lower()
    },
    {
        "name": "trace_topic_evolution",
        "args": {"topic": "mitochondria"},
        "validate": lambda r: "evolution" in str(r).lower()
    }
]
```

### TC-004: Protocol Generation Testing
```python
# Test protocol tools
test_cases = [
    {
        "name": "create_health_protocol",
        "args": {
            "condition": "fatigue",
            "age": 45,
            "gender": "male",
            "activity_level": "moderate"
        },
        "validate": lambda r: all(k in str(r) for k in ["nutrition", "supplements", "movement"])
    },
    {
        "name": "nutrition_calculator",
        "args": {"weight": 70, "goal": "performance"},
        "validate": lambda r: "protein" in str(r).lower()
    }
]
```

### TC-005: Error Handling
**Test error scenarios**:
1. Vector store unavailable
2. Invalid tool names
3. Malformed arguments
4. Network timeouts
5. Resource limits

### TC-006: Performance Testing
```python
# Measure response times
import time

async def test_performance():
    start_times = {}
    end_times = {}
    
    for tool_name in tool_list:
        start = time.time()
        result = await server.call_tool(tool_name, test_args[tool_name])
        end = time.time()
        
        assert (end - start) < 5.0  # 5 second timeout
        print(f"{tool_name}: {end - start:.2f}s")
```

### TC-007: Integration Testing
1. **Claude Desktop Integration**
   ```bash
   # Run server in stdio mode
   python src/mcp/mcp_sdk_clean.py
   
   # Configure Claude Desktop with path
   # Test all tools via Claude interface
   ```

2. **HTTP Transport Testing**
   ```bash
   # If HTTP transport is added
   curl -X POST http://localhost:8000/tools/knowledge_search \
     -d '{"query": "vitamin d"}'
   ```

### TC-008: Prompt Testing
**Test all 3 prompts**:
1. health_assessment
2. supplement_optimization
3. longevity_protocol

### TC-009: Concurrent Access
```python
# Test multiple simultaneous tool calls
async def test_concurrent():
    tasks = []
    for i in range(10):
        task = server.call_tool("knowledge_search", {"query": f"test {i}"})
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    assert len(results) == 10
```

### TC-010: Production Validation
1. Deploy to Railway
2. Test via production URL
3. Monitor logs for errors
4. Validate all tools work

## Test Execution Plan

### Phase 1: Unit Testing (Local)
- [ ] Run tool discovery tests
- [ ] Test each tool individually
- [ ] Validate parameter schemas
- [ ] Check error handling

### Phase 2: Integration Testing
- [ ] Test with Claude Desktop
- [ ] Test prompt functionality
- [ ] Test concurrent access
- [ ] Performance benchmarking

### Phase 3: System Testing
- [ ] Deploy to Docker
- [ ] Test in Railway staging
- [ ] Full end-to-end testing
- [ ] Load testing

### Phase 4: Acceptance Testing
- [ ] User acceptance scenarios
- [ ] Real-world queries
- [ ] Documentation validation
- [ ] Performance validation

## Test Automation Script

Create `src/tests/test_mcp_sdk_migration.py`:
```python
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.mcp_sdk_clean import StrunzKnowledgeServer
import mcp.types as types

class TestMCPSDKMigration:
    def __init__(self):
        self.server = StrunzKnowledgeServer()
        self.passed = 0
        self.failed = 0
        
    async def run_all_tests(self):
        print("=== MCP SDK Migration Test Suite ===\n")
        
        # Test tool discovery
        await self.test_tool_discovery()
        
        # Test each tool
        await self.test_all_tools()
        
        # Test error handling
        await self.test_error_handling()
        
        # Print summary
        total = self.passed + self.failed
        print(f"\n=== Test Summary ===")
        print(f"Total: {total}")
        print(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"Failed: {self.failed}")
        
    async def test_tool_discovery(self):
        try:
            tools = await self.server.list_tools()
            assert len(tools) == 20
            print("✅ Tool Discovery: All 20 tools found")
            self.passed += 1
        except Exception as e:
            print(f"❌ Tool Discovery: {e}")
            self.failed += 1
            
    async def test_all_tools(self):
        # Define test cases for each tool
        test_cases = [
            ("knowledge_search", {"query": "vitamin d"}),
            ("find_contradictions", {"topic": "protein"}),
            ("trace_topic_evolution", {"topic": "longevity"}),
            ("create_health_protocol", {"condition": "fatigue", "age": 40, "gender": "male"}),
            ("analyze_supplement_stack", {"supplements": ["vitamin d", "magnesium"]}),
            ("nutrition_calculator", {"weight": 70, "goal": "maintenance"}),
            ("get_community_insights", {"topic": "sleep"}),
            ("summarize_posts", {"category": "nutrition"}),
            ("get_trending_insights", {"days": 30}),
            ("analyze_strunz_newsletter_evolution", {"timeframe": "all"}),
            ("get_guest_authors_analysis", {"timeframe": "all"}),
            ("track_health_topic_trends", {"topic": "mitochondria"}),
            ("get_health_assessment_questions", {"user_role": "patient"}),
            ("get_dr_strunz_biography", {"include_achievements": True}),
            ("get_mcp_server_purpose", {}),
            ("get_vector_db_analysis", {}),
            ("compare_approaches", {"health_issue": "diabetes", "alternative_approaches": ["keto", "vegan"]}),
            ("get_optimal_diagnostic_values", {"age": 40, "gender": "male"}),
            ("assess_user_health_profile", {"responses": {"energy": 6, "sleep": 7}}),
            ("create_personalized_protocol", {"user_profile": {"age": 40, "goals": ["energy"]}}),
            ("get_dr_strunz_info", {"info_type": "all"})
        ]
        
        for tool_name, args in test_cases:
            try:
                result = await self.server.call_tool(tool_name, args)
                assert result is not None
                assert len(result) > 0
                print(f"✅ {tool_name}: Success")
                self.passed += 1
            except Exception as e:
                print(f"❌ {tool_name}: {e}")
                self.failed += 1
                
    async def test_error_handling(self):
        # Test unknown tool
        try:
            await self.server.call_tool("unknown_tool", {})
            print("❌ Error Handling: Should have raised error for unknown tool")
            self.failed += 1
        except ValueError:
            print("✅ Error Handling: Correctly rejected unknown tool")
            self.passed += 1
        except Exception as e:
            print(f"❌ Error Handling: Unexpected error: {e}")
            self.failed += 1

if __name__ == "__main__":
    tester = TestMCPSDKMigration()
    asyncio.run(tester.run_all_tests())
```

## Success Criteria

### Functional Requirements
- [ ] All 20 tools are discoverable
- [ ] All tools execute without errors
- [ ] Parameter validation works correctly
- [ ] Error messages are informative
- [ ] Response formats match expected schemas

### Performance Requirements
- [ ] Tool responses < 5 seconds
- [ ] Memory usage stable
- [ ] No memory leaks
- [ ] Concurrent access supported

### Integration Requirements
- [ ] Works with Claude Desktop
- [ ] Works in production (Railway)
- [ ] Works in Docker containers
- [ ] Prompts function correctly

### Documentation Requirements
- [ ] All tools documented
- [ ] Migration guide complete
- [ ] Test results documented
- [ ] Known issues tracked

## Test Report Template

```markdown
# MCP SDK Migration Test Report

**Date**: [Date]
**Version**: 0.8.0
**Tester**: [Name]

## Executive Summary
- Total Tools Tested: 20
- Pass Rate: X%
- Critical Issues: [Count]
- Performance: [Average response time]

## Detailed Results

### Tool Testing Results
| Tool Name | Status | Response Time | Notes |
|-----------|--------|---------------|-------|
| knowledge_search | ✅ Pass | 0.3s | |
| ... | | | |

### Integration Testing
- Claude Desktop: [Status]
- Railway Production: [Status]
- Docker: [Status]

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
- [Action items]
```