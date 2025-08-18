#!/bin/bash

echo "🔍 Monitoring Railway Deployment..."
echo "=================================="

while true; do
    echo -n "$(date '+%H:%M:%S') - "
    
    # Check the version
    VERSION=$(curl -s https://strunz.up.railway.app/health 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    TOOLS=$(curl -s https://strunz.up.railway.app/health 2>/dev/null | grep -o '"tools_count":[0-9]*' | cut -d':' -f2)
    
    if [ "$VERSION" = "3.0.0" ]; then
        echo "✅ Deployment successful! Version $VERSION with $TOOLS tools"
        break
    elif [ -z "$VERSION" ]; then
        echo "⏳ Service unavailable (deployment in progress...)"
    else
        echo "⏳ Still on version $VERSION with $TOOLS tools (waiting for 3.0.0...)"
    fi
    
    sleep 10
done

echo ""
echo "🎉 Deployment Complete!"
echo "Version: $VERSION"
echo "Tools: $TOOLS"
echo "URL: https://strunz.up.railway.app/"