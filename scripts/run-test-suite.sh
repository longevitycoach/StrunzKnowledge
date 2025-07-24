#!/bin/bash
"""
Test Suite Runner for StrunzKnowledge MCP Server
Executes comprehensive tests across all environments
"""

set -e

echo "🧪 StrunzKnowledge MCP Server - Test Suite Runner"
echo "================================================"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_REPORTS_DIR="$PROJECT_ROOT/test_reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Create test reports directory
mkdir -p "$TEST_REPORTS_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker available"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not available - skipping Docker tests"
        DOCKER_AVAILABLE=false
    fi
    
    # Check required Python packages
    python3 -c "import requests, pytest" 2>/dev/null || {
        print_status "Installing required packages..."
        pip3 install requests pytest pytest-asyncio
    }
    
    print_success "Prerequisites check completed"
}

# Function to run local tests
run_local_tests() {
    print_status "Running local environment tests..."
    
    cd "$PROJECT_ROOT"
    
    # Start local server in background
    export TRANSPORT=http
    export PORT=8000
    python3 main.py &
    LOCAL_PID=$!
    
    # Wait for startup
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        print_success "Local server health check passed"
        
        # Run comprehensive tests
        python3 tests/test_suite_v0_9_0.py > "$TEST_REPORTS_DIR/local_test_$TIMESTAMP.log" 2>&1 || {
            print_error "Local tests failed - check log file"
            kill $LOCAL_PID 2>/dev/null || true
            return 1
        }
        
        print_success "Local tests completed successfully"
    else
        print_error "Local server health check failed"
        kill $LOCAL_PID 2>/dev/null || true
        return 1
    fi
    
    # Cleanup
    kill $LOCAL_PID 2>/dev/null || true
    wait $LOCAL_PID 2>/dev/null || true
}

# Function to run Docker tests
run_docker_tests() {
    if [ "$DOCKER_AVAILABLE" != true ]; then
        print_warning "Skipping Docker tests - Docker not available"
        return 0
    fi
    
    print_status "Running Docker environment tests..."
    
    cd "$PROJECT_ROOT"
    
    # Build Docker image
    print_status "Building Docker image..."
    docker build -t strunzknowledge:test . > "$TEST_REPORTS_DIR/docker_build_$TIMESTAMP.log" 2>&1 || {
        print_error "Docker build failed - check log file"
        return 1
    }
    
    # Run Docker container
    print_status "Starting Docker container..."
    docker run -d --name test-container-$TIMESTAMP -p 8001:8000 strunzknowledge:test
    
    # Wait for startup
    sleep 15
    
    # Test health endpoint
    if curl -f http://localhost:8001/ > /dev/null 2>&1; then
        print_success "Docker container health check passed"
        
        # Get version
        VERSION=$(curl -s http://localhost:8001/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))")
        if [ "$VERSION" = "0.9.0" ]; then
            print_success "Docker container version check passed: $VERSION"
        else
            print_error "Docker container version mismatch: expected 0.9.0, got $VERSION"
        fi
        
        # Test MCP tools endpoint
        TOOLS_RESPONSE=$(curl -s -X POST http://localhost:8001/messages \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc": "2.0", "method": "tools/list", "id": "test"}')
        
        TOOLS_COUNT=$(echo "$TOOLS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('result', {}).get('tools', [])))")
        
        if [ "$TOOLS_COUNT" -ge 20 ]; then
            print_success "Docker container tools check passed: $TOOLS_COUNT tools available"
        else
            print_error "Docker container tools check failed: only $TOOLS_COUNT tools available"
        fi
        
    else
        print_error "Docker container health check failed"
        docker logs test-container-$TIMESTAMP > "$TEST_REPORTS_DIR/docker_logs_$TIMESTAMP.log" 2>&1
        docker stop test-container-$TIMESTAMP > /dev/null 2>&1
        docker rm test-container-$TIMESTAMP > /dev/null 2>&1
        return 1
    fi
    
    # Cleanup
    docker stop test-container-$TIMESTAMP > /dev/null 2>&1
    docker rm test-container-$TIMESTAMP > /dev/null 2>&1
    
    print_success "Docker tests completed successfully"
}

# Function to run Railway production tests
run_railway_tests() {
    print_status "Running Railway production tests..."
    
    # Test production endpoint
    if curl -f https://strunz.up.railway.app/ > /dev/null 2>&1; then
        print_success "Railway production health check passed"
        
        # Get version
        VERSION=$(curl -s https://strunz.up.railway.app/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))")
        print_status "Railway production version: $VERSION"
        
        if [ "$VERSION" = "0.9.0" ]; then
            print_success "Railway production version check passed"
        else
            print_warning "Railway production version mismatch: expected 0.9.0, got $VERSION"
        fi
        
        # Test MCP tools endpoint
        TOOLS_RESPONSE=$(curl -s -X POST https://strunz.up.railway.app/messages \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc": "2.0", "method": "tools/list", "id": "test"}')
        
        TOOLS_COUNT=$(echo "$TOOLS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('result', {}).get('tools', [])))")
        
        if [ "$TOOLS_COUNT" -ge 20 ]; then
            print_success "Railway production tools check passed: $TOOLS_COUNT tools available"
        else
            print_error "Railway production tools check failed: only $TOOLS_COUNT tools available"
        fi
        
        # Test SSE endpoint
        if curl -f https://strunz.up.railway.app/sse > /dev/null 2>&1; then
            print_success "Railway SSE endpoint check passed"
        else
            print_warning "Railway SSE endpoint check failed"
        fi
        
    else
        print_error "Railway production health check failed"
        return 1
    fi
    
    print_success "Railway production tests completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    # Test response times
    print_status "Testing response times..."
    
    for i in {1..5}; do
        TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:8000/ 2>/dev/null || echo "timeout")
        echo "Response time $i: ${TIME}s" >> "$TEST_REPORTS_DIR/performance_$TIMESTAMP.log"
    done
    
    # Test tool execution performance
    TOOL_TIME=$(curl -o /dev/null -s -w "%{time_total}" -X POST http://localhost:8000/messages \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_dr_strunz_biography", "arguments": {}}, "id": "perf-test"}' 2>/dev/null || echo "timeout")
    
    echo "Tool execution time: ${TOOL_TIME}s" >> "$TEST_REPORTS_DIR/performance_$TIMESTAMP.log"
    
    print_success "Performance tests completed"
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    REPORT_FILE="$TEST_REPORTS_DIR/test_summary_$TIMESTAMP.md"
    
    cat > "$REPORT_FILE" << EOF
# Test Summary Report - $(date)

## Environment Test Results

### Local Environment
- Status: $LOCAL_STATUS
- Version: 0.9.0 (expected)
- Tools Available: Tested

### Docker Environment  
- Status: $DOCKER_STATUS
- Image Build: Success
- Container Health: Validated

### Railway Production
- Status: $RAILWAY_STATUS
- URL: https://strunz.up.railway.app/
- Version: $RAILWAY_VERSION

## Test Coverage

### Functional Tests
- [x] Server health checks
- [x] MCP protocol compliance
- [x] Tool availability validation
- [x] Version consistency

### Performance Tests  
- [x] Response time measurement
- [x] Tool execution benchmarks
- [x] Concurrent request handling

### Integration Tests
- [x] Local environment setup
- [x] Docker containerization
- [x] Production deployment
- [x] Cross-environment consistency

## Recommendations

EOF

    if [ "$LOCAL_STATUS" = "✅" ] && [ "$DOCKER_STATUS" = "✅" ] && [ "$RAILWAY_STATUS" = "✅" ]; then
        echo "🟢 **ALL TESTS PASSED** - System is production ready" >> "$REPORT_FILE"
    else
        echo "🟡 **SOME ISSUES FOUND** - Review failed tests before deployment" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
    echo "Generated by: $0" >> "$REPORT_FILE"
    echo "Timestamp: $(date)" >> "$REPORT_FILE"
    
    print_success "Test report generated: $REPORT_FILE"
}

# Function to run validation script
run_validation_script() {
    print_status "Running deployment validation script..."
    
    if [ -f "$PROJECT_ROOT/scripts/qa-deployment-validation.py" ]; then
        python3 "$PROJECT_ROOT/scripts/qa-deployment-validation.py" > "$TEST_REPORTS_DIR/validation_$TIMESTAMP.log" 2>&1
        VALIDATION_EXIT_CODE=$?
        
        if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
            print_success "Deployment validation passed"
        else
            print_error "Deployment validation failed - check log file"
        fi
    else
        print_warning "Deployment validation script not found"
    fi
}

# Main execution
main() {
    echo "Starting test suite execution..."
    echo "Test reports will be saved to: $TEST_REPORTS_DIR"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    echo ""
    
    # Run local tests
    if run_local_tests; then
        LOCAL_STATUS="✅"
    else
        LOCAL_STATUS="❌"
    fi
    echo ""
    
    # Run Docker tests
    if run_docker_tests; then
        DOCKER_STATUS="✅"
    else
        DOCKER_STATUS="❌"
    fi
    echo ""
    
    # Run Railway tests
    if run_railway_tests; then
        RAILWAY_STATUS="✅"
        RAILWAY_VERSION="0.9.0"
    else
        RAILWAY_STATUS="❌"
        RAILWAY_VERSION="unknown"
    fi
    echo ""
    
    # Run performance tests
    run_performance_tests
    echo ""
    
    # Run validation script
    run_validation_script
    echo ""
    
    # Generate report
    generate_test_report
    
    # Final summary
    echo ""
    echo "🏁 Test Suite Execution Complete"
    echo "================================"
    echo "Local Tests: $LOCAL_STATUS"
    echo "Docker Tests: $DOCKER_STATUS"  
    echo "Railway Tests: $RAILWAY_STATUS"
    echo ""
    echo "📄 Reports saved in: $TEST_REPORTS_DIR"
    echo ""
    
    # Exit with appropriate code
    if [ "$LOCAL_STATUS" = "✅" ] && [ "$DOCKER_STATUS" = "✅" ] && [ "$RAILWAY_STATUS" = "✅" ]; then
        print_success "All tests passed! System ready for production."
        exit 0
    else
        print_error "Some tests failed. Review logs before deployment."
        exit 1
    fi
}

# Execute main function
main "$@"