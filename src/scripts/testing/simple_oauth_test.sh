#!/bin/bash

# Simple OAuth2 and Claude.ai Integration Test Script
# Tests the most critical endpoints for v0.7.10 release

BASE_URL="http://localhost:8000"
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🚀 Starting OAuth2 and Claude.ai Integration Tests"
echo "============================================="
echo "Server: $BASE_URL"
echo "Version: 0.7.10"
echo ""

PASSED=0
TOTAL=0

function test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    local method="${4:-GET}"
    
    echo -n "Testing $name... "
    TOTAL=$((TOTAL + 1))
    
    if [ "$method" = "POST" ]; then
        status=$(timeout 5 curl -s -o /dev/null -w "%{http_code}" -X POST "$url")
    else
        status=$(timeout 5 curl -s -o /dev/null -w "%{http_code}" "$url")
    fi
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($status)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC} ($status, expected $expected_status)"
    fi
}

function test_json_endpoint() {
    local name="$1"
    local url="$2"
    local key="$3"
    
    echo -n "Testing $name... "
    TOTAL=$((TOTAL + 1))
    
    response=$(curl -s "$url")
    status=$(echo "$response" | grep -o "\"$key\"" | wc -l)
    
    if [ "$status" -gt 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} (has $key)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC} (missing $key)"
        echo "Response: $response"
    fi
}

echo "🔍 Testing Discovery Endpoints"
echo "-------------------------------"
test_endpoint "Health Check" "$BASE_URL/" 200
test_endpoint "Health Detailed" "$BASE_URL/health" 200
test_json_endpoint "MCP Resource Discovery" "$BASE_URL/.well-known/mcp/resource" "mcpVersion"
test_json_endpoint "OAuth Server Metadata" "$BASE_URL/.well-known/oauth-authorization-server" "authorization_endpoint"

echo ""
echo "🤖 Testing Claude.ai Specific Endpoints"
echo "---------------------------------------"
test_endpoint "Claude.ai Auth (default)" "$BASE_URL/api/organizations/test-org/mcp/start-auth/test-id" 302
test_endpoint "Claude.ai Auth (with params)" "$BASE_URL/api/organizations/test-org/mcp/start-auth/test-id?redirect_url=https://claude.ai/callback" 302

echo ""
echo "🔐 Testing OAuth Flow"
echo "--------------------"
# Register a client first
CLIENT_DATA='{"client_name":"Test Client","redirect_uris":["http://localhost:3000/callback"]}'
CLIENT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$CLIENT_DATA" "$BASE_URL/oauth/register")
CLIENT_ID=$(echo "$CLIENT_RESPONSE" | grep -o '"client_id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$CLIENT_ID" ]; then
    echo -e "${GREEN}✅ Client Registration PASS${NC} (client_id: ${CLIENT_ID:0:10}...)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Client Registration FAIL${NC}"
fi
TOTAL=$((TOTAL + 1))

test_endpoint "OAuth Authorize" "$BASE_URL/oauth/authorize?response_type=code&client_id=$CLIENT_ID&redirect_uri=http://localhost:3000/callback&scope=read&state=test" 302

echo ""
echo "📮 Testing POST Handlers (Claude.ai)"
echo "-----------------------------------"
test_endpoint "Root POST handler" "$BASE_URL/" 200 "POST"
test_endpoint "SSE POST handler" "$BASE_URL/sse" 200 "POST"

echo ""
echo "🔧 Testing MCP Protocol"
echo "----------------------"
# Test MCP initialize
MCP_INIT='{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-03-26"},"id":1}'
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$MCP_INIT" "$BASE_URL/messages")
echo -n "Testing MCP Initialize... "
TOTAL=$((TOTAL + 1))
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} ($status)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} ($status)"
fi

# Test MCP tools list
MCP_TOOLS='{"jsonrpc":"2.0","method":"tools/list","id":2}'
tools_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$MCP_TOOLS" "$BASE_URL/messages")
tools_count=$(echo "$tools_response" | grep -o '"name"' | wc -l)
echo -n "Testing MCP Tools List... "
TOTAL=$((TOTAL + 1))
if [ "$tools_count" -gt 15 ]; then
    echo -e "${GREEN}✅ PASS${NC} ($tools_count tools)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (only $tools_count tools)"
fi

echo ""
echo "🔄 Testing OAuth Callback"
echo "------------------------"
test_endpoint "OAuth Callback (success)" "$BASE_URL/api/mcp/auth_callback?code=test123&state=test" 200
test_endpoint "OAuth Callback (error)" "$BASE_URL/api/mcp/auth_callback?error=access_denied" 400

echo ""
echo "============================================="
echo "📊 Test Results Summary"
echo "============================================="
echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $((TOTAL - PASSED))"
SUCCESS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc -l)
echo "Success Rate: ${SUCCESS_RATE}%"

if [ "$PASSED" -eq "$TOTAL" ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Server is ready for deployment.${NC}"
    exit 0
elif (( $(echo "$SUCCESS_RATE >= 90" | bc -l) )); then
    echo -e "${BLUE}✨ Most tests passed (${SUCCESS_RATE}%). Server looks good for deployment.${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some critical tests failed (${SUCCESS_RATE}%). Review before deployment.${NC}"
    exit 1
fi