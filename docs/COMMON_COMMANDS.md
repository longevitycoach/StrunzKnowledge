# Common Commands Reference

## Railway CLI Commands

### Logs and Monitoring
```bash
# View recent logs (most common)
railway logs --service strunz-knowledge | tail -100

# View live logs
railway logs --service strunz-knowledge --follow

# View deployment logs
railway logs --deployment

# View build logs
railway logs --build

# Check service status
railway status

# List deployments
railway deployments

# Get deployment details (JSON format)
railway deployments --json
```

### Service Management
```bash
# Redeploy the service
railway redeploy

# Link to a project
railway link

# Switch environment
railway environment

# List services
railway service

# View service details
railway service --service strunz-knowledge
```

### Variables and Configuration
```bash
# List environment variables
railway variables

# Set an environment variable
railway variables set KEY=value

# Delete an environment variable
railway variables delete KEY

# View Railway configuration
railway whoami
```

### Deployment Commands
```bash
# Deploy current directory
railway up

# Deploy with specific service
railway up --service strunz-knowledge

# Cancel deployment
railway down
```

## Curl Commands for Testing MCP Server

### Health Check
```bash
# Basic health check
curl -s https://strunz.up.railway.app/

# Pretty print health check
curl -s https://strunz.up.railway.app/ | python3 -m json.tool
```

### SSE Endpoint Testing
```bash
# Test SSE endpoint availability
curl -I https://strunz.up.railway.app/sse \
  -H "Authorization: Bearer demo"

# Test SSE connection (will hang if working)
curl -N https://strunz.up.railway.app/sse \
  -H "Authorization: Bearer demo" \
  -H "Accept: text/event-stream"
```

### MCP Protocol Testing

#### Initialize Session
```bash
# Note: These won't work directly with SSE, but show the MCP protocol structure

# Initialize MCP session (example structure)
cat << 'EOF' | python3 -c "
import httpx
import json
import sys

request = json.load(sys.stdin)
headers = {
    'Authorization': 'Bearer demo',
    'Content-Type': 'application/json'
}

# This would need SSE client implementation
print('Request structure:', json.dumps(request, indent=2))
"
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  },
  "id": 1
}
EOF
```

### Tool Testing with Python Scripts

#### Simple Knowledge Search
```python
# save as test_search.py
import httpx
import json

async def test_search():
    url = "https://strunz.up.railway.app/sse"
    headers = {
        "Authorization": "Bearer demo",
        "Content-Type": "application/json"
    }
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "knowledge_search",
            "arguments": {
                "query": "Vitamin D",
                "limit": 5
            }
        },
        "id": 1
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=request)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")

# Run with: python3 -c "import asyncio; from test_search import test_search; asyncio.run(test_search())"
```

### Quick Test Commands

```bash
# Test if server is up
curl -s -o /dev/null -w "%{http_code}" https://strunz.up.railway.app/

# Get server version
curl -s https://strunz.up.railway.app/ | jq -r '.version'

# Get MCP protocol version
curl -s https://strunz.up.railway.app/ | jq -r '.protocol_version'

# Check available endpoints
curl -s https://strunz.up.railway.app/ | jq '.endpoints'

# Test with timeout
curl -m 5 -s https://strunz.up.railway.app/ || echo "Timeout or error"
```

### Performance Testing

```bash
# Measure response time
time curl -s https://strunz.up.railway.app/ > /dev/null

# Get detailed timing
curl -w "\n\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://strunz.up.railway.app/

# Test with multiple requests
for i in {1..5}; do
  echo "Request $i:"
  time curl -s https://strunz.up.railway.app/ > /dev/null
done
```

### Docker Testing (Local)

```bash
# Run locally with Docker
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e RAILWAY_PUBLIC_DOMAIN=localhost \
  -e RAILWAY_ENVIRONMENT=production \
  ghcr.io/longevitycoach/strunzknowledge:latest

# Test local Docker instance
curl -s http://localhost:8000/

# Test with authorization
curl -s http://localhost:8000/sse \
  -H "Authorization: Bearer demo"
```

### Debugging Commands

```bash
# Check response headers
curl -I https://strunz.up.railway.app/

# Verbose output
curl -v https://strunz.up.railway.app/ 2>&1 | grep -E "^[<>]"

# Check SSL certificate
curl -v https://strunz.up.railway.app/ 2>&1 | grep -A 5 "SSL certificate"

# Test with different user agents
curl -H "User-Agent: MCP-Client/1.0" https://strunz.up.railway.app/
```

### Railway CLI Troubleshooting

```bash
# Check if logged in
railway whoami

# Re-login if needed
railway login

# Check project configuration
railway status

# Force redeploy
railway up --force

# View environment info
railway environment

# Check for errors in last 200 lines
railway logs --service strunz-knowledge | tail -200 | grep -i error

# Monitor deployment in real-time
watch -n 5 'railway status && echo "" && railway deployments --json | head -20'
```

## Common Workflows

### 1. Check Deployment Health
```bash
# Full health check workflow
railway status
curl -s https://strunz.up.railway.app/ | jq '.'
railway logs --service strunz-knowledge | tail -50
```

### 2. Debug Timeout Issues
```bash
# Check recent errors
railway logs --service strunz-knowledge | grep -i timeout | tail -20

# Test response times
time curl -s https://strunz.up.railway.app/ > /dev/null

# Monitor logs during test
railway logs --service strunz-knowledge --follow &
# Run your test
# Kill log monitoring: fg then Ctrl+C
```

### 3. Deploy New Version
```bash
# Check current version
curl -s https://strunz.up.railway.app/ | jq -r '.version'

# Deploy new version
git push origin main
railway up

# Monitor deployment
railway logs --deployment --follow

# Verify new version
curl -s https://strunz.up.railway.app/ | jq -r '.version'
```

## Environment Variables Reference

```bash
# Common Railway environment variables
RAILWAY_PUBLIC_DOMAIN=strunz.up.railway.app
RAILWAY_ENVIRONMENT=production
PORT=8000

# MCP Server specific
CLAUDE_AI_SKIP_OAUTH=true
ENABLE_BATCH2_MIGRATION=true
TRANSPORT=sse

# Set them via CLI
railway variables set VARIABLE_NAME=value
```

## Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Railway shortcuts
alias rlog='railway logs --service strunz-knowledge | tail -100'
alias rlogf='railway logs --service strunz-knowledge --follow'
alias rstatus='railway status'
alias rdeploy='railway up'
alias rredeploy='railway redeploy'

# MCP testing shortcuts
alias mcp-health='curl -s https://strunz.up.railway.app/ | jq'
alias mcp-version='curl -s https://strunz.up.railway.app/ | jq -r .version'
alias mcp-test='curl -I https://strunz.up.railway.app/sse -H "Authorization: Bearer demo"'
```