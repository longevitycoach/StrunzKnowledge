#!/bin/bash

# Alternative cleanup script using direct GitHub API calls
# This script doesn't rely on gh CLI authentication

# Configuration
ORG="longevitycoach"
PACKAGE_NAME="strunzknowledge"
PACKAGE_TYPE="container"
KEEP_LATEST=5

# GitHub token (passed as argument or environment variable)
GITHUB_TOKEN="${1:-$GITHUB_TOKEN}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Usage: $0 <github_token>"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

echo "=== GitHub Container Registry Cleanup Script (Direct API) ==="
echo "Organization: $ORG"
echo "Package: $PACKAGE_NAME"
echo "Keep Latest: $KEEP_LATEST versions"
echo ""

# Function to make GitHub API calls
github_api() {
    local method="${1:-GET}"
    local endpoint="$2"
    local data="$3"
    
    if [ "$method" = "DELETE" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com$endpoint"
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com$endpoint" | jq .
    fi
}

# Test authentication
echo "Testing GitHub API access..."
USER_INFO=$(github_api GET "/user" | jq -r '.login // empty')
if [ -z "$USER_INFO" ]; then
    echo "Error: Invalid GitHub token or authentication failed"
    exit 1
fi
echo "Authenticated as: $USER_INFO"

# Get package versions
echo -e "\nFetching package versions..."
VERSIONS=$(github_api GET "/orgs/$ORG/packages/$PACKAGE_TYPE/$PACKAGE_NAME/versions?per_page=100")

# Check for errors
if echo "$VERSIONS" | jq -e '.message' >/dev/null 2>&1; then
    ERROR_MSG=$(echo "$VERSIONS" | jq -r '.message')
    echo "Error: $ERROR_MSG"
    
    if echo "$ERROR_MSG" | grep -q "scope"; then
        echo ""
        echo "Your token needs these scopes:"
        echo "  - read:packages"
        echo "  - write:packages (for deletion)"
        echo "  - delete:packages (for deletion)"
        echo ""
        echo "Please create a new token at: https://github.com/settings/tokens/new"
        echo "Select the required scopes and try again."
    fi
    exit 1
fi

# Process versions
TOTAL=$(echo "$VERSIONS" | jq 'length')
echo "Found $TOTAL versions"

if [ "$TOTAL" -eq 0 ]; then
    echo "No versions found"
    exit 0
fi

# Show current versions
echo -e "\nCurrent versions (newest first):"
echo "$VERSIONS" | jq -r 'sort_by(.created_at) | reverse | .[] | "  - \(.metadata.container.tags[0] // "untagged") (ID: \(.id), Created: \(.created_at))"' | head -10

if [ "$TOTAL" -le "$KEEP_LATEST" ]; then
    echo -e "\nOnly $TOTAL versions exist. Keeping all (threshold: $KEEP_LATEST)"
    exit 0
fi

# Identify versions to delete
echo -e "\nAnalyzing versions..."
VERSIONS_TO_DELETE=$(echo "$VERSIONS" | jq "sort_by(.created_at) | reverse | .[$KEEP_LATEST:] | .[] | .id")
DELETE_COUNT=$(echo "$VERSIONS_TO_DELETE" | wc -l | tr -d ' ')

echo "Will keep the latest $KEEP_LATEST versions"
echo "Will delete $DELETE_COUNT older versions"

# Show what will be deleted
echo -e "\nVersions to delete:"
echo "$VERSIONS" | jq -r "sort_by(.created_at) | reverse | .[$KEEP_LATEST:] | .[] | \"  - \(.metadata.container.tags[0] // \"untagged\") (ID: \(.id), Created: \(.created_at))\""

# Confirm
echo ""
read -p "Do you want to proceed with deletion? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deletion cancelled"
    exit 0
fi

# Delete versions
echo -e "\nDeleting old versions..."
DELETED=0
FAILED=0

for VERSION_ID in $VERSIONS_TO_DELETE; do
    # Remove quotes from ID
    VERSION_ID=$(echo "$VERSION_ID" | tr -d '"')
    
    echo -n "Deleting version ID $VERSION_ID... "
    
    RESPONSE=$(github_api DELETE "/orgs/$ORG/packages/$PACKAGE_TYPE/$PACKAGE_NAME/versions/$VERSION_ID" 2>&1)
    
    if [ -z "$RESPONSE" ] || [ "$RESPONSE" = "null" ]; then
        echo "✓ Success"
        ((DELETED++))
    else
        echo "✗ Failed"
        echo "  Error: $RESPONSE"
        ((FAILED++))
    fi
done

echo -e "\nCleanup complete!"
echo "Deleted: $DELETED versions"
if [ "$FAILED" -gt 0 ]; then
    echo "Failed: $FAILED versions"
fi