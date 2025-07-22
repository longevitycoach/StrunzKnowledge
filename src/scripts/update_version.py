#!/usr/bin/env python3
"""
Update version numbers across all deployment files
Usage: python src/scripts/update_version.py 0.7.8
"""

import sys
import re
from pathlib import Path

def update_version(new_version: str):
    """Update version in all deployment files"""
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("   Expected format: X.Y.Z (e.g., 0.7.8)")
        sys.exit(1)
    
    # Files to update with their specific patterns
    files_to_update = [
        # Main deployment files
        ('railway-deploy.py', r'v\d+\.\d+\.\d+'),
        ('src/scripts/deployment/railway_claude_ai_compatible.py', r'"version": "\d+\.\d+\.\d+"'),
        ('src/scripts/deployment/railway_claude_ai_compatible.py', r'version="\d+\.\d+\.\d+"'),
        ('src/scripts/deployment/railway_claude_ai_compatible.py', r'v\d+\.\d+\.\d+'),
        
        # Other deployment scripts
        ('src/scripts/deployment/railway_official_mcp_server.py', r'\d+\.\d+\.\d+'),
        ('src/scripts/deployment/railway_mcp_fixed.py', r'\d+\.\d+\.\d+'),
        
        # Core server files
        ('src/mcp/claude_compatible_server.py', r'"version": "\d+\.\d+\.\d+"'),
        ('src/mcp/enhanced_server.py', r'"version": "\d+\.\d+\.\d+"'),
        ('src/mcp/mcp_sdk_clean.py', r'\d+\.\d+\.\d+'),
    ]
    
    updated_files = []
    
    for file_path, pattern in files_to_update:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            content = path.read_text()
            original_content = content
            
            # Update version patterns
            if 'version' in pattern:
                # For JSON-style version strings
                new_content = re.sub(
                    r'"version": "\d+\.\d+\.\d+"',
                    f'"version": "{new_version}"',
                    content
                )
                new_content = re.sub(
                    r'version="\d+\.\d+\.\d+"',
                    f'version="{new_version}"',
                    new_content
                )
            elif 'v' in pattern:
                # For v-prefixed versions
                new_content = re.sub(
                    r'v\d+\.\d+\.\d+',
                    f'v{new_version}',
                    content
                )
            else:
                # For plain version numbers
                new_content = re.sub(
                    r'\d+\.\d+\.\d+',
                    new_version,
                    content
                )
            
            if new_content != original_content:
                path.write_text(new_content)
                updated_files.append(file_path)
                print(f"✅ Updated: {file_path}")
            else:
                print(f"ℹ️  No changes: {file_path}")
                
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    print(f"\n📝 Summary:")
    print(f"   Updated {len(updated_files)} files to version {new_version}")
    
    if updated_files:
        print(f"\n🔍 Verify changes with:")
        print(f'   grep -r "{new_version}" src/scripts/deployment/ src/mcp/ railway-deploy.py | grep -v test')
        print(f"\n💡 Next steps:")
        print(f"   1. Review changes: git diff")
        print(f"   2. Commit: git commit -am 'chore: Update version to {new_version}'")
        print(f"   3. Tag: git tag -a v{new_version} -m 'Release v{new_version}'")
        print(f"   4. Push: git push origin main --tags")
        print(f"   5. Create release: gh release create v{new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/scripts/update_version.py NEW_VERSION")
        print("Example: python src/scripts/update_version.py 0.7.8")
        sys.exit(1)
    
    new_version = sys.argv[1]
    update_version(new_version)