#!/bin/bash

# Railway Token Setup Script
# 
# To get your Railway API token:
# 1. Go to https://railway.app/account/tokens
# 2. Create a new token
# 3. Copy the token
# 4. Run this script with: source setup_railway_token.sh
#
# Then enter your token when prompted

echo "Railway Token Setup"
echo "==================="
echo ""
echo "Please enter your Railway API token:"
echo "(Get it from https://railway.app/account/tokens)"
echo ""
read -s RAILWAY_TOKEN

export RAILWAY_TOKEN=$RAILWAY_TOKEN

echo ""
echo "Testing Railway connection..."
railway whoami

if [ $? -eq 0 ]; then
    echo "✅ Successfully connected to Railway!"
    echo ""
    echo "You can now use Railway CLI commands like:"
    echo "  railway logs"
    echo "  railway status"
    echo "  railway up"
else
    echo "❌ Failed to connect. Please check your token."
fi