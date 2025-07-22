#!/bin/bash

# Script to clean up old Docker package versions from GitHub Container Registry
# Requires gh CLI with read:packages, write:packages, and delete:packages scopes

# Configuration
ORG="longevitycoach"
PACKAGE_NAME="strunzknowledge"
KEEP_LATEST=5  # Number of latest versions to keep

echo "=== GitHub Container Registry Cleanup Script ==="
echo "Organization: $ORG"
echo "Package: $PACKAGE_NAME"
echo "Keep Latest: $KEEP_LATEST versions"
echo ""

# Test authentication first
echo "Testing GitHub API access..."
if ! gh api user >/dev/null 2>&1; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

echo "Fetching package versions for $ORG/$PACKAGE_NAME..."

# Get all versions sorted by created date (newest first)
VERSIONS=$(gh api --paginate "/orgs/$ORG/packages/container/$PACKAGE_NAME/versions" 2>&1)

# Check if we got an error
if echo "$VERSIONS" | grep -q "HTTP 4"; then
    echo "Error accessing package versions. Details:"
    echo "$VERSIONS"
    echo ""
    echo "Please ensure:"
    echo "1. Your GitHub token has these scopes: read:packages, write:packages, delete:packages"
    echo "2. The package name is correct: $PACKAGE_NAME"
    echo "3. The organization is correct: $ORG"
    exit 1
fi

# Process the versions
PROCESSED_VERSIONS=$(echo "$VERSIONS" | jq -s 'flatten | map(select(.id != null)) | sort_by(.created_at) | reverse')

if [ "$PROCESSED_VERSIONS" = "[]" ] || [ -z "$PROCESSED_VERSIONS" ]; then
    echo "No versions found for package $PACKAGE_NAME"
    exit 0
fi

# Count total versions
TOTAL=$(echo "$PROCESSED_VERSIONS" | jq 'length')
echo "Found $TOTAL versions"

# Show all versions
echo -e "\nAll versions (newest first):"
echo "$PROCESSED_VERSIONS" | jq -r '.[] | "  - \(.metadata.container.tags[0] // "untagged") (ID: \(.id), Created: \(.created_at))"' | head -10
if [ "$TOTAL" -gt 10 ]; then
    echo "  ... and $((TOTAL - 10)) more"
fi

if [ "$TOTAL" -le "$KEEP_LATEST" ]; then
    echo -e "\nOnly $TOTAL versions exist. Keeping all (threshold: $KEEP_LATEST)"
    exit 0
fi

# Get versions to delete (all except the latest N)
TO_DELETE=$(echo "$PROCESSED_VERSIONS" | jq ".[$KEEP_LATEST:]")
DELETE_COUNT=$(echo "$TO_DELETE" | jq 'length')

echo -e "\nWill keep the latest $KEEP_LATEST versions:"
echo "$PROCESSED_VERSIONS" | jq -r ".[:$KEEP_LATEST] | .[] | \"  ✓ Keep: \(.metadata.container.tags[0] // \"untagged\") (created: \(.created_at))\""

echo -e "\nWill delete $DELETE_COUNT older versions:"
echo "$TO_DELETE" | jq -r '.[] | "  ✗ Delete: \(.metadata.container.tags[0] // "untagged") (ID: \(.id), created: \(.created_at))"'

# Confirm deletion
echo ""
read -p "Do you want to proceed with deletion? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deletion cancelled"
    exit 0
fi

# Delete old versions
echo -e "\nDeleting old versions..."
DELETED=0
FAILED=0

echo "$TO_DELETE" | jq -r '.[] | .id' | while read -r VERSION_ID; do
    VERSION_TAG=$(echo "$TO_DELETE" | jq -r ".[] | select(.id == $VERSION_ID) | .metadata.container.tags[0] // \"untagged\"")
    echo -n "Deleting version $VERSION_TAG (ID: $VERSION_ID)... "
    
    if gh api --method DELETE "/orgs/$ORG/packages/container/$PACKAGE_NAME/versions/$VERSION_ID" >/dev/null 2>&1; then
        echo "✓ Success"
        ((DELETED++))
    else
        echo "✗ Failed"
        ((FAILED++))
    fi
done

echo -e "\nCleanup complete!"
echo "Deleted: $DELETED versions"
if [ "$FAILED" -gt 0 ]; then
    echo "Failed: $FAILED versions"
fi