#!/bin/bash
# Deploy v7 fix to Railway

echo "🚀 Deploying v7 fix for Claude.ai integration"
echo "============================================"

# Update main.py to use v7
echo "📝 Updating main.py to use v7..."
sed -i '' 's/from src.mcp.sse_server_v4 import app/from src.mcp.sse_server_v7 import app/g' main.py

# Create a git commit
echo "📦 Creating git commit..."
git add src/mcp/sse_server_v7.py
git add main.py
git commit -m "fix: Improve error handling and parameter validation for Claude.ai

- Enhanced error handling with detailed error messages
- Better parameter validation for all tools
- Fixed potential parameter mismatch issues
- Added comprehensive logging for debugging
- Improved graceful error handling
- Version 7.0.0 with stability improvements"

# Push to Railway
echo "🚂 Pushing to Railway..."
git push origin main

echo "✅ Deployment initiated!"
echo ""
echo "Next steps:"
echo "1. Monitor Railway logs: railway logs --service strunz-knowledge"
echo "2. Test in Claude.ai after deployment completes"
echo "3. Check https://strunz.up.railway.app/health"