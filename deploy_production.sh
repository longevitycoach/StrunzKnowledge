#!/bin/bash

# Production Deployment Script for StrunzKnowledge
# Complete FastMCP to Official MCP SDK Migration
# Version: 3.0.0

echo "🚀 Starting Production Deployment..."
echo "=================================="

# Set all feature flags for production
export ENABLE_BATCH2_MIGRATION=true
export ENABLE_BATCH3_MIGRATION=true
export ENABLE_BATCH4_MIGRATION=true

echo "✅ Feature flags set:"
echo "  - ENABLE_BATCH2_MIGRATION: $ENABLE_BATCH2_MIGRATION"
echo "  - ENABLE_BATCH3_MIGRATION: $ENABLE_BATCH3_MIGRATION"
echo "  - ENABLE_BATCH4_MIGRATION: $ENABLE_BATCH4_MIGRATION"

# Optional: Set Gemini API key if available
if [ -n "$GOOGLE_GEMINI_API_KEY" ]; then
    echo "✅ Gemini API key detected - AI features will be available"
else
    echo "ℹ️  No Gemini API key - AI features will be disabled"
fi

# Deploy to Railway
echo ""
echo "📦 Deploying to Railway..."
railway up

# Check deployment status
echo ""
echo "🔍 Checking deployment status..."
railway status

echo ""
echo "✅ Production deployment initiated!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Monitor Railway logs: railway logs --tail"
echo "2. Test all 24 tools are working"
echo "3. Verify Claude.ai shows 'Connected'"
echo "4. Monitor for 48 hours before removing feature flags"