#!/bin/bash

# Script to list Docker packages and optionally update their descriptions
# Requires gh CLI with read:packages scope

# Configuration
ORG="longevitycoach"
PACKAGE_NAME="strunzknowledge"

echo "Fetching package information for $ORG/$PACKAGE_NAME..."

# Get package details
PACKAGE_INFO=$(gh api "/orgs/$ORG/packages/container/$PACKAGE_NAME" 2>/dev/null)

if [ -z "$PACKAGE_INFO" ]; then
  echo "Package not found or insufficient permissions."
  echo "Please ensure your GitHub token has the 'read:packages' scope."
  exit 1
fi

# Display current package info
echo -e "\n📦 Package Information:"
echo "$PACKAGE_INFO" | jq -r '
  "Name: \(.name)
Type: \(.package_type)
Visibility: \(.visibility)
Created: \(.created_at)
Updated: \(.updated_at)
HTML URL: \(.html_url)"'

# Get all versions
echo -e "\n📋 Package Versions:"
gh api --paginate "/orgs/$ORG/packages/container/$PACKAGE_NAME/versions" | \
  jq -r '.[] | "  - \(.metadata.container.tags[0] // "untagged") (ID: \(.id), Created: \(.created_at))"' | \
  head -20

echo -e "\n(Showing up to 20 most recent versions)"

# Package description update functionality
echo -e "\n📝 Package Description:"
echo "Note: GitHub Container Registry packages don't have editable descriptions via API."
echo "Descriptions are typically set through:"
echo "  1. The Dockerfile LABEL org.opencontainers.image.description"
echo "  2. Repository README that's linked to the package"
echo "  3. GitHub Actions workflow annotations"

echo -e "\nTo add descriptions to your Docker images, update your Dockerfile:"
echo '  LABEL org.opencontainers.image.description="Dr. Strunz Knowledge Base MCP Server"'
echo '  LABEL org.opencontainers.image.source="https://github.com/longevitycoach/StrunzKnowledge"'
echo '  LABEL org.opencontainers.image.authors="longevitycoach"'
echo '  LABEL org.opencontainers.image.title="StrunzKnowledge MCP Server"'