#!/bin/bash
"""
Force Railway Deployment Script
Ensures Railway picks up the latest v0.9.0 unified architecture
"""

set -e

echo "🚀 Force Railway Deployment Script"
echo "=================================="

echo "📊 Current Status Check..."
CURRENT_VERSION=$(curl -s https://strunz.up.railway.app/ | jq -r '.version')
echo "Production Version: $CURRENT_VERSION"
echo "Target Version: 0.9.0"

if [ "$CURRENT_VERSION" = "0.9.0" ]; then
    echo "✅ Production already running v0.9.0"
    exit 0
fi

echo "🔄 Triggering Railway Deployment..."

# Method 1: Empty commit to force rebuild
echo "Method 1: Empty commit trigger..."
git commit --allow-empty -m "chore: Force Railway deployment for v0.9.0

Railway is stuck on v0.8.0 due to build cache issues.
This empty commit forces a fresh deployment.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main

echo "⏳ Waiting 60 seconds for Railway to detect changes..."
sleep 60

# Check if deployment started
NEW_VERSION=$(curl -s https://strunz.up.railway.app/ | jq -r '.version')
echo "Version after empty commit: $NEW_VERSION"

if [ "$NEW_VERSION" = "0.9.0" ]; then
    echo "✅ Success! Railway deployed v0.9.0"
    
    # Run validation
    echo "🧪 Running deployment validation..."
    python scripts/qa-deployment-validation.py
    
    exit 0
fi

echo "⚠️ Empty commit didn't trigger deployment. Trying alternative methods..."

# Method 2: Update a timestamp file
echo "Method 2: Timestamp file update..."
echo "# Last deployment: $(date)" > .railway-deploy-timestamp
git add .railway-deploy-timestamp
git commit -m "chore: Update deployment timestamp to force Railway rebuild"
git push origin main

echo "⏳ Waiting another 60 seconds..."
sleep 60

NEW_VERSION=$(curl -s https://strunz.up.railway.app/ | jq -r '.version')
echo "Version after timestamp update: $NEW_VERSION"

if [ "$NEW_VERSION" = "0.9.0" ]; then
    echo "✅ Success! Railway deployed v0.9.0"
    
    # Run validation
    echo "🧪 Running deployment validation..."
    python scripts/qa-deployment-validation.py
    
    exit 0
fi

echo "❌ Railway deployment stuck. Manual intervention required."
echo ""
echo "🛠️ Manual Steps Required:"
echo "1. Check Railway dashboard for build status"
echo "2. Consider clearing build cache in Railway settings"
echo "3. Verify Dockerfile and railway.toml configuration"
echo "4. Check for any deployment errors in Railway logs"
echo ""
echo "Railway Dashboard: https://railway.app/dashboard"

exit 1