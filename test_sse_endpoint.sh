#!/bin/bash

# Test SSE endpoint functionality
# Usage: ./test_sse_endpoint.sh [URL]

SSE_URL="${1:-http://localhost:8000/sse}"
TIMEOUT=10

echo "Testing SSE endpoint: $SSE_URL"
echo "Listening for $TIMEOUT seconds..."
echo ""

# Test SSE connection with timeout
output=$(timeout $TIMEOUT curl -s -N \
    -H "Accept: text/event-stream" \
    -H "Cache-Control: no-cache" \
    "$SSE_URL" 2>&1)

exit_code=$?

if [ $exit_code -eq 124 ]; then
    # Timeout reached - this is expected for SSE
    echo "✓ SSE connection established successfully"
    echo ""
    echo "Events received:"
    echo "$output" | grep -E "^(event:|data:)" | head -20
    
    # Check if we got the connection event
    if echo "$output" | grep -q "event: connected"; then
        echo ""
        echo "✓ Initial connection event received"
    else
        echo ""
        echo "✗ No connection event received"
        exit 1
    fi
    
    # Check if we got valid JSON data
    if echo "$output" | grep "^data:" | head -1 | cut -d' ' -f2- | jq . > /dev/null 2>&1; then
        echo "✓ Valid JSON data format"
    else
        echo "✗ Invalid JSON data format"
        exit 1
    fi
    
    echo ""
    echo "SSE endpoint test PASSED"
    exit 0
elif [ $exit_code -eq 0 ]; then
    # Connection closed before timeout
    echo "✗ SSE connection closed unexpectedly"
    echo "Response: $output"
    exit 1
else
    # Other error
    echo "✗ Failed to connect to SSE endpoint (exit code: $exit_code)"
    echo "Error: $output"
    exit 1
fi