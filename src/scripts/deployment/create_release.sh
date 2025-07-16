#!/bin/bash
# Create GitHub release for v0.3.0

VERSION="v0.3.0"
TITLE="Release $VERSION - OAuth 2.1 Authentication & Claude Integration"

# Create git tag
git tag -a $VERSION -m "$TITLE"

# Push tag to GitHub
git push origin $VERSION

# Create release using GitHub CLI
gh release create $VERSION \
  --title "$TITLE" \
  --notes-file docs/RELEASE_NOTES_v0.3.0.md \
  --latest

echo "✅ Release $VERSION created successfully!"
echo "📦 Don't forget to publish the Docker image:"
echo "   docker tag strunz-mcp:latest longevitycoach/strunz-mcp:$VERSION"
echo "   docker push longevitycoach/strunz-mcp:$VERSION"
echo "   docker push longevitycoach/strunz-mcp:latest"