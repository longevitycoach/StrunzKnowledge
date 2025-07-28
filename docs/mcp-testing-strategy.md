# MCP Testing Strategy

## Overview
This document outlines the comprehensive testing strategy for the StrunzKnowledge MCP (Model Context Protocol) implementation, covering both server and client components.

## Testing Objectives
1. Ensure protocol compliance with MCP specification 2025-11-05
2. Validate all tool functionality and error handling
3. Verify cross-platform compatibility (Claude Desktop, Claude.ai, browser extensions)
4. Maintain 95%+ test coverage for critical paths
5. Performance benchmarks for response times and resource usage

## Testing Layers

### 1. Unit Testing
**Scope**: Individual functions and methods
**Tools**: pytest, unittest
**Coverage Target**: 90%

#### Key Areas:
- Knowledge search algorithms
- Parameter validation
- Error handling functions
- Data transformation utilities
- Authentication flows

#### Example Test Cases:
```python
def test_search_knowledge_validation():
    """Test search parameter validation"""
    # Test empty query
    result = search_knowledge("")
    assert "Error: Query cannot be empty" in result
    
    # Test limit boundaries
    result = search_knowledge("test", limit=100)
    assert len(results) <= 50  # Max limit enforced
```

### 2. Integration Testing
**Scope**: Component interactions
**Tools**: pytest-asyncio, mock servers
**Coverage Target**: 85%

#### Key Areas:
- MCP server initialization
- SSE transport layer
- OAuth flow integration
- Vector store connectivity
- Tool registration and execution

#### Test Scenarios:
1. **Server Startup**
   - Vector store initialization
   - Tool registration
   - Health check endpoints

2. **Client Connection**
   - SSE connection establishment
   - Session management
   - Authentication flows

3. **Tool Execution**
   - Request/response cycle
   - Error propagation
   - Concurrent requests

### 3. End-to-End Testing
**Scope**: Complete user workflows
**Tools**: Playwright, Selenium (for browser extension)
**Coverage Target**: Core user journeys

#### Test Workflows:
1. **Claude Desktop Integration**
   - Server discovery
   - Tool listing
   - Search execution
   - Result formatting

2. **Claude.ai Integration**
   - OAuth flow (if enabled)
   - SSE connection
   - Tool availability
   - Session persistence

3. **Browser Extension**
   - Installation flow
   - Gemini Key setup
   - Website integration
   - Cross-site functionality

### 4. Performance Testing
**Scope**: Response times, resource usage
**Tools**: locust, pytest-benchmark
**Targets**:
- Response time: <200ms for search
- Memory usage: <500MB under load
- Concurrent users: 100+

#### Benchmarks:
1. **Search Performance**
   - Simple queries: <100ms
   - Complex queries: <500ms
   - Concurrent searches: <1s average

2. **Resource Usage**
   - Memory footprint at startup
   - Memory growth under load
   - CPU usage patterns

### 5. Security Testing
**Scope**: Authentication, data protection
**Tools**: OWASP ZAP, custom scripts

#### Focus Areas:
- Input sanitization
- XSS prevention
- CORS configuration
- API key protection
- OAuth flow security

## Test Environments

### Local Development
```yaml
environment: local
transport: stdio
tools: all
data: sample subset
```

### CI/CD Pipeline
```yaml
environment: github-actions
transport: sse
tools: all
data: test fixtures
parallel: true
```

### Staging
```yaml
environment: railway-preview
transport: sse
tools: all
data: production subset
monitoring: enabled
```

### Production
```yaml
environment: railway-production
transport: sse
tools: all
data: full production
monitoring: enabled
alerts: enabled
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: MCP Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements-unified.txt
      - name: Run unit tests
        run: pytest tests/unit -v --cov
      - name: Run integration tests
        run: pytest tests/integration -v
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Pre-commit Hooks
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/unit
        language: system
        pass_filenames: false
      - id: mypy
        name: mypy
        entry: mypy src/
        language: system
        pass_filenames: false
```

## Test Data Management

### Test Fixtures
1. **Sample Books**: 3 books with known content
2. **Sample News**: 100 articles across date ranges
3. **Sample Forum**: 50 posts with various topics
4. **Edge Cases**: Unicode, long texts, special characters

### Data Generation
```python
# Generate test data
python scripts/generate_test_data.py --books 3 --news 100 --forum 50
```

## Monitoring and Reporting

### Test Metrics
1. **Coverage Reports**: Generated with pytest-cov
2. **Performance Reports**: Generated with pytest-benchmark
3. **Security Reports**: OWASP ZAP reports
4. **Compatibility Matrix**: Cross-platform test results

### Dashboard Integration
- GitHub Actions status badges
- CodeCov integration
- Performance trend graphs
- Test failure notifications

## Test Execution Strategy

### Daily Runs
1. Full unit test suite
2. Critical integration tests
3. Smoke tests for E2E

### Weekly Runs
1. Full test suite
2. Performance benchmarks
3. Security scans
4. Cross-browser testing

### Release Testing
1. Full regression suite
2. Performance baselines
3. Security audit
4. User acceptance testing

## Troubleshooting Guide

### Common Issues
1. **Vector Store Initialization**
   - Check FAISS index files
   - Verify memory allocation
   - Review index reconstruction logs

2. **SSE Connection Failures**
   - Verify CORS configuration
   - Check transport mounting
   - Review session management

3. **Tool Registration**
   - Validate tool schemas
   - Check FastMCP configuration
   - Review tool discovery logs

### Debug Commands
```bash
# Run specific test with verbose output
pytest -vvs tests/test_specific.py::test_function

# Run with debugging
pytest --pdb tests/

# Check test coverage gaps
pytest --cov=src --cov-report=html
```

## Future Enhancements

### Planned Improvements
1. **Automated Browser Extension Testing**
   - Selenium Grid integration
   - Cross-browser matrix testing
   - Extension installation automation

2. **Load Testing Enhancement**
   - Distributed load testing
   - Real-world usage patterns
   - Stress test scenarios

3. **AI-Powered Test Generation**
   - Use LLMs to generate test cases
   - Automatic edge case discovery
   - Test scenario expansion

### Research Areas
1. Property-based testing with Hypothesis
2. Mutation testing for quality assessment
3. Chaos engineering for resilience testing

## Appendix

### Test File Structure
```
tests/
├── unit/
│   ├── test_search.py
│   ├── test_tools.py
│   ├── test_auth.py
│   └── test_utils.py
├── integration/
│   ├── test_mcp_server.py
│   ├── test_sse_transport.py
│   └── test_oauth_flow.py
├── e2e/
│   ├── test_claude_desktop.py
│   ├── test_claude_ai.py
│   └── test_browser_extension.py
├── performance/
│   ├── test_search_perf.py
│   └── test_load.py
├── fixtures/
│   ├── sample_data.json
│   └── test_vectors.pkl
└── conftest.py
```

### Useful Resources
- [MCP Specification](https://github.com/anthropics/mcp)
- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)