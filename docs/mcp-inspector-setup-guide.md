# MCP Inspector Setup and Usage Guide - Issue #12

## Overview
MCP Inspector is the official testing tool for MCP servers. It provides a web-based interface to test tool discovery, execution, and performance validation.

## Installation
```bash
# Install globally
npm install -g @modelcontextprotocol/inspector

# Verify installation
npx @modelcontextprotocol/inspector --version
```

## Basic Usage

### 1. Start MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```

This will:
- Start a proxy server on localhost:6277
- Start the web interface on localhost:6274
- Generate a session token for authentication
- Open browser automatically

### 2. Connect to StrunzKnowledge Server

#### Option A: Test mcp_sdk_clean.py (Target Server)
```bash
# Terminal 1: Start our target server
python src/mcp/mcp_sdk_clean.py

# Terminal 2: Start MCP Inspector
npx @modelcontextprotocol/inspector python src/mcp/mcp_sdk_clean.py
```

#### Option B: Test enhanced_server.py (Current FastMCP Server)  
```bash
# Terminal 1: Start current server
python src/mcp/enhanced_server.py

# Terminal 2: Connect inspector to enhanced server
npx @modelcontextprotocol/inspector python src/mcp/enhanced_server.py
```

#### Option C: Test Production Server
```bash
# Connect to Railway production
npx @modelcontextprotocol/inspector --url https://strunz.up.railway.app/sse
```

## Performance Baseline Testing

### 1. Tool Discovery Test
**Objective**: Verify all 20 tools are discoverable
**Success Criteria**: All tools appear in Inspector interface

### 2. Individual Tool Testing
**Test each tool with sample inputs:**

#### Batch 1 Tools (Simple)
1. `knowledge_search` - Test with "vitamin D" query
2. `summarize_posts` - Test with "nutrition" category  
3. `get_health_assessment_questions` - Test with default parameters
4. `get_dr_strunz_biography` - Test with all flags
5. `get_mcp_server_purpose` - Test with no parameters
6. `get_vector_db_analysis` - Test with no parameters

#### Batch 2 Tools (Medium)
7. `compare_approaches` - Test health issue comparison
8. `nutrition_calculator` - Test with age/gender parameters
9. `get_community_insights` - Test topic search
10. `get_trending_insights` - Test with time parameters
11. `get_guest_authors_analysis` - Test timeframe analysis
12. `get_optimal_diagnostic_values` - Test with patient parameters

#### Batch 3 Tools (Complex)
13. `find_contradictions` - Test with health topic
14. `trace_topic_evolution` - Test with time parameters
15. `analyze_strunz_newsletter_evolution` - Test timeframe analysis
16. `track_health_topic_trends` - Test trend analysis

#### Batch 4 Tools (User Profile)
17. `create_health_protocol` - Test with condition
18. `analyze_supplement_stack` - Test with supplement list
19. `assess_user_health_profile` - Test with responses
20. `create_personalized_protocol` - Test with user profile

### 3. Performance Metrics Collection

For each tool, measure:
- **Response Time**: Time from request to response
- **Memory Usage**: Peak memory during execution  
- **Success Rate**: Successful executions vs attempts
- **Error Rate**: Failed executions and error types
- **Data Size**: Response payload size

## Baseline Creation Script

### performance_baseline.py
```python
#!/usr/bin/env python3
"""
Performance Baseline Creation Script for MCP Inspector
Creates baseline metrics for all 20 tools before FastMCP elimination
"""

import asyncio
import json
import time
import psutil
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class PerformanceBaseline:
    def __init__(self):
        self.results = {}
        self.baseline_date = datetime.now().isoformat()
    
    async def test_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Test a single tool and collect performance metrics."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Import and test the server
            from src.mcp.enhanced_server import StrunzKnowledgeMCP
            server = StrunzKnowledgeMCP()
            
            # Execute tool (would need actual tool execution logic)
            # This is a template - actual implementation depends on server interface
            result = {"status": "success", "test": "placeholder"}
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "response_time_ms": (end_time - start_time) * 1000,
                "memory_usage_mb": (end_memory - start_memory) / 1024 / 1024,
                "status": "success",
                "result_size": len(str(result)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "response_time_ms": (end_time - start_time) * 1000,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_baselines(self):
        """Run baseline tests for all 20 tools."""
        
        # Tool test definitions
        tool_tests = [
            # Batch 1 - Simple Tools
            ("knowledge_search", {"query": "vitamin D"}),
            ("summarize_posts", {"category": "nutrition", "limit": 5}),
            ("get_health_assessment_questions", {"user_role": "patient"}),
            ("get_dr_strunz_biography", {"include_achievements": True}),
            ("get_mcp_server_purpose", {}),
            ("get_vector_db_analysis", {}),
            
            # Batch 2 - Medium Tools  
            ("compare_approaches", {"health_issue": "diabetes", "alternative_approaches": ["keto", "Mediterranean"]}),
            ("nutrition_calculator", {"age": 35, "gender": "male", "activity_level": "moderate"}),
            ("get_community_insights", {"topic": "supplements", "min_engagement": 3}),
            ("get_trending_insights", {"days": 30}),
            ("get_guest_authors_analysis", {"timeframe": "1_year"}),
            ("get_optimal_diagnostic_values", {"age": 35, "gender": "male"}),
            
            # Batch 3 - Complex Tools
            ("find_contradictions", {"topic": "cholesterol", "include_reasoning": True}),
            ("trace_topic_evolution", {"topic": "intermittent fasting", "start_year": 2020}),
            ("analyze_strunz_newsletter_evolution", {"timeframe": "2_years"}),
            ("track_health_topic_trends", {"topic": "vitamin D", "timeframe": "3_years"}),
            
            # Batch 4 - User Profile Tools  
            ("create_health_protocol", {"condition": "fatigue"}),
            ("analyze_supplement_stack", {"supplements": ["vitamin D", "magnesium"], "health_goals": ["energy"]}),
            ("assess_user_health_profile", {"responses": {"age": 35, "symptoms": ["fatigue"]}}),
            ("create_personalized_protocol", {"user_profile": {"age": 35, "goals": ["energy"]}})
        ]
        
        print(f"🧪 Running baseline tests for {len(tool_tests)} tools...")
        
        for tool_name, parameters in tool_tests:
            print(f"Testing {tool_name}...")
            result = await self.test_tool(tool_name, parameters)
            self.results[tool_name] = result
        
        # Save results
        baseline_file = f"docs/baselines/performance_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(baseline_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(baseline_file, 'w') as f:
            json.dump({
                "baseline_date": self.baseline_date,
                "server_type": "enhanced_server_fastmcp",
                "total_tools": len(tool_tests),
                "results": self.results
            }, f, indent=2)
        
        print(f"✅ Baseline saved to {baseline_file}")
        return baseline_file

if __name__ == "__main__":
    baseline = PerformanceBaseline()
    asyncio.run(baseline.run_all_baselines())
```

## Integration with Migration Process

### Pre-Migration Baseline
1. **Run baseline on enhanced_server.py** (FastMCP version)
2. **Document all 20 tool responses** and performance metrics
3. **Create reference dataset** for comparison

### Per-Batch Validation  
1. **Migrate batch of 5 tools** to Official SDK
2. **Run MCP Inspector tests** on migrated tools
3. **Compare performance** against baseline
4. **Validate functionality** matches exactly
5. **Check for regressions** before proceeding

### Post-Migration Validation
1. **Full 20-tool test suite** with MCP Inspector
2. **Performance comparison** with baseline
3. **Claude.ai integration test** (should show "Connected")
4. **Stress testing** with concurrent requests

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure MCP server is running before starting Inspector
   - Check port conflicts (default: 6274, 6277)

2. **Tools Not Appearing**
   - Verify server implements MCP protocol correctly
   - Check tool registration in server code

3. **Authentication Errors**
   - Use generated session token
   - Or set DANGEROUSLY_OMIT_AUTH=true for testing

4. **Performance Issues**
   - Monitor memory usage during testing
   - Use smaller test datasets for initial validation

### Environment Setup
```bash
# Set environment variables for testing
export MCP_SERVER_URL="http://localhost:8000"
export MCP_INSPECTOR_PORT="6274"
export DANGEROUSLY_OMIT_AUTH="true"  # For development only
```

## Success Criteria

### MCP Inspector Setup Complete
- [ ] MCP Inspector installed and functional
- [ ] Can connect to enhanced_server.py (FastMCP)
- [ ] Can connect to mcp_sdk_clean.py (Official SDK)
- [ ] All 20 tools discoverable in interface
- [ ] Performance baseline created for all tools

### Ready for Phase 2 Migration
- [ ] Baseline metrics documented
- [ ] Validation workflow established  
- [ ] Automated testing scripts created
- [ ] Integration with batch migration process confirmed