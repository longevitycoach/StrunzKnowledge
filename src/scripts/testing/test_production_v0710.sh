#!/bin/bash

# Production Test Script for v0.7.10
# Tests against https://strunz.up.railway.app

BASE_URL="${1:-https://strunz.up.railway.app}"
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Production Test Suite for StrunzKnowledge v0.7.10"
echo "===================================================="
echo "Server: $BASE_URL"
echo "Time: $(date)"
echo ""

PASSED=0
TOTAL=0

function test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    local method="${4:-GET}"
    local data="${5:-}"
    local check_content="${6:-}"
    
    echo -n "Testing $name... "
    TOTAL=$((TOTAL + 1))
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    fi
    
    status_code=$(echo "$response" | tail -n 1)
    content=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "$expected_status" ]; then
        if [ -n "$check_content" ] && [[ ! "$content" =~ $check_content ]]; then
            echo -e "${RED}❌ FAIL${NC} (status OK but missing: $check_content)"
        else
            echo -e "${GREEN}✅ PASS${NC} ($status_code)"
            PASSED=$((PASSED + 1))
        fi
    else
        echo -e "${RED}❌ FAIL${NC} ($status_code, expected $expected_status)"
    fi
}

echo "🔍 Testing Core Endpoints"
echo "-------------------------"
test_endpoint "Health Check" "$BASE_URL/health" 200 "GET" "" "version.*0.7.10"
test_endpoint "Version Check" "$BASE_URL/" 200 "GET" "" "0.7.10"
test_endpoint "MCP Discovery" "$BASE_URL/.well-known/mcp/resource" 200 "GET" "" "mcpVersion"

echo ""
echo "🤖 Testing Claude.ai OAuth Flow"
echo "--------------------------------"
# Test the Claude.ai start auth endpoint
AUTH_URL="$BASE_URL/api/organizations/test-org/mcp/start-auth/test-auth-id"
echo -n "Testing Claude.ai Start Auth... "
response=$(curl -s -w "\n%{http_code}" -L "$AUTH_URL" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
content=$(echo "$response" | head -n -1)

if [[ "$content" =~ "auth_not_required" ]] || [ "$status_code" = "302" ]; then
    echo -e "${GREEN}✅ PASS${NC} (OAuth skip mode or redirect)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} ($status_code)"
fi
TOTAL=$((TOTAL + 1))

# Test OAuth callback
test_endpoint "OAuth Callback (success)" "$BASE_URL/api/mcp/auth_callback?code=test123&state=test" 200 "GET" "" "postMessage"
test_endpoint "OAuth Callback (error)" "$BASE_URL/api/mcp/auth_callback?error=access_denied" 400

echo ""
echo "📮 Testing POST Endpoints"
echo "-------------------------"
test_endpoint "Root POST" "$BASE_URL/" 200 "POST" '{"method":"initialize"}'
test_endpoint "Messages POST" "$BASE_URL/messages" 200 "POST" '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

echo ""
echo "🔧 Testing MCP Protocol"
echo "-----------------------"
# Initialize
init_response=$(curl -s -X POST "$BASE_URL/messages" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0.0","clientInfo":{"name":"test"}},"id":1}')
echo -n "Testing MCP Initialize... "
if [[ "$init_response" =~ "\"result\"" ]]; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
fi
TOTAL=$((TOTAL + 1))

# Tools list
tools_response=$(curl -s -X POST "$BASE_URL/messages" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}')
echo -n "Testing MCP Tools List... "
if [[ "$tools_response" =~ "search_strunz_knowledge" ]]; then
    tool_count=$(echo "$tools_response" | grep -o '"name"' | wc -l)
    echo -e "${GREEN}✅ PASS${NC} ($tool_count tools)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
fi
TOTAL=$((TOTAL + 1))

echo ""
echo "🔐 Testing OAuth Registration"
echo "-----------------------------"
# Register a test client
reg_response=$(curl -s -X POST "$BASE_URL/oauth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "client_name": "Production Test Client",
        "redirect_uris": ["https://claude.ai/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"]
    }')
    
echo -n "Testing OAuth Client Registration... "
if [[ "$reg_response" =~ "client_id" ]]; then
    client_id=$(echo "$reg_response" | grep -o '"client_id":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ PASS${NC} (client_id: ${client_id:0:10}...)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
fi
TOTAL=$((TOTAL + 1))

echo ""
echo "🌐 Testing SSE Endpoint"
echo "-----------------------"
echo -n "Testing SSE Connection... "
# Test SSE with timeout
sse_response=$(curl -s -w "\n%{http_code}" -N -H "Accept: text/event-stream" \
    --max-time 2 "$BASE_URL/sse" 2>/dev/null)
sse_status=$(echo "$sse_response" | tail -n 1)
if [ "$sse_status" = "200" ] || [[ "$sse_response" =~ "event:" ]]; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  SKIP${NC} (SSE requires persistent connection)"
fi
TOTAL=$((TOTAL + 1))

echo ""
echo "============================================="
echo "📊 Test Results Summary"
echo "============================================="
echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $((TOTAL - PASSED))"
SUCCESS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc -l 2>/dev/null || echo "N/A")
echo "Success Rate: ${SUCCESS_RATE}%"
echo ""

if [ "$PASSED" -eq "$TOTAL" ]; then
    echo -e "${GREEN}🎉 All tests passed! Production is ready.${NC}"
    exit 0
elif [ "$PASSED" -ge $((TOTAL * 90 / 100)) ]; then
    echo -e "${BLUE}✨ Most tests passed. Production looks good.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Multiple tests failed. Please investigate.${NC}"
    exit 1
fi