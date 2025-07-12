#!/usr/bin/env python3
"""
Wget Forum Downloader - Updated for Clean Structure
===================================================

Creates wget commands that output directly to data/raw/forum and only
download forum content (no other site content).

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
Status: PRODUCTION
"""

import os
from pathlib import Path
import subprocess

def create_updated_wget_commands():
    """Create updated wget commands for clean data structure."""
    
    print("🔧 CREATING UPDATED WGET COMMANDS")
    print("=" * 80)
    
    # Forum categories - only the 5 remaining (fitness already downloaded)
    categories = {
        'gesundheit': 'gesundheit', 
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    # Base directory for downloads
    base_dir = Path("data/raw/forum")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {base_dir}")
    
    # Base wget command - only forum content
    base_cmd = [
        "wget",
        "--recursive",
        "--level=5", 
        "--page-requisites",
        "--html-extension",
        "--convert-links",
        "--domains=strunz.com,www.strunz.com",
        "--no-parent",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "--wait=1",
        "--random-wait",
        "--directory-prefix=data/raw/forum",  # Output to data/raw/forum
        "--no-host-directories",              # Don't create www.strunz.com subdirectory
        "--cut-dirs=1"                       # Remove /forum from path structure
    ]
    
    commands = {}
    
    print("\n📋 UPDATED WGET COMMANDS:")
    print("-" * 60)
    
    for category_key, url_name in categories.items():
        print(f"\n🏷️  {category_key.upper()} ({url_name}):")
        
        # Create category-specific command
        cmd = base_cmd.copy()
        cmd.extend([
            f"--accept-regex=.*{url_name}.*",
            "--reject-regex=.*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$",
            f"https://www.strunz.com/forum/{url_name}"
        ])
        
        commands[category_key] = cmd
        
        # Display command
        cmd_str = " ".join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
        print(f"   Command: {cmd_str}")
    
    return commands

def create_forum_download_script():
    """Create script to download remaining forum categories."""
    
    print(f"\n📜 CREATING FORUM DOWNLOAD SCRIPT")
    print("-" * 60)
    
    categories = {
        'gesundheit': 'gesundheit', 
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    script_content = '''#!/bin/bash
#
# Download Remaining Strunz Forum Categories
# =========================================
#
# Downloads all remaining forum categories to data/raw/forum
# Author: Matthias Buchhorn
# Project: StrunzKnowledgeMCP
#

echo "🚀 Downloading Remaining Strunz Forum Categories"
echo "=============================================="

# Ensure output directory exists
mkdir -p data/raw/forum

echo "📁 Output directory: data/raw/forum"
echo ""

'''
    
    for category_key, url_name in categories.items():
        script_content += f'''
echo "📥 Downloading {category_key.upper()} ({url_name})"
echo "{'='*50}"

wget \\
    --recursive \\
    --level=5 \\
    --page-requisites \\
    --html-extension \\
    --convert-links \\
    --domains=strunz.com,www.strunz.com \\
    --no-parent \\
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \\
    --wait=1 \\
    --random-wait \\
    --directory-prefix=data/raw/forum \\
    --no-host-directories \\
    --cut-dirs=1 \\
    --accept-regex=".*{url_name}.*" \\
    --reject-regex=".*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" \\
    https://www.strunz.com/forum/{url_name}

if [ $? -eq 0 ]; then
    echo "✅ {category_key.upper()} download completed successfully"
else
    echo "❌ {category_key.upper()} download failed"
fi

echo ""
'''
    
    script_content += '''
echo "🏁 All forum downloads completed!"
echo "================================"

# Show download summary
echo ""
echo "📊 DOWNLOAD SUMMARY:"
echo "   Forum files:"
find data/raw/forum -name "*.html" | wc -l | xargs echo "     HTML files:"
du -sh data/raw/forum | cut -f1 | xargs echo "     Total size:"

echo ""
echo "📁 Directory structure:"
ls -la data/raw/forum/

echo ""
echo "✅ Ready for Docling processing!"
'''
    
    script_file = Path("src/tools/download_remaining_forums.sh")
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_file, 0o755)
    
    print(f"✅ Download script created: {script_file}")
    print(f"   To run: ./src/tools/download_remaining_forums.sh")
    
    return script_file

def analyze_current_forum_content():
    """Analyze what forum content we currently have."""
    
    print(f"\n📊 CURRENT FORUM CONTENT ANALYSIS")
    print("-" * 60)
    
    forum_dir = Path("data/raw/forum")
    
    if not forum_dir.exists():
        print("❌ No forum directory found")
        return
    
    # Count files by category
    categories = {}
    total_files = 0
    
    for html_file in forum_dir.glob("**/*.html"):
        total_files += 1
        
        # Determine category from path
        path_parts = html_file.parts
        if len(path_parts) >= 4:  # data/raw/forum/category/file.html
            category = path_parts[3]
            categories[category] = categories.get(category, 0) + 1
    
    print(f"📋 CURRENT CONTENT:")
    print(f"   Total files: {total_files}")
    
    if categories:
        print(f"   By category:")
        for category, count in sorted(categories.items()):
            print(f"     {category}: {count} files")
    else:
        print("   No categorized content found")
    
    # Check if we have the fitness content we moved
    fitness_files = list(forum_dir.glob("**/fitness*.html"))
    if fitness_files:
        print(f"   Fitness files: {len(fitness_files)}")
    
    return {
        'total_files': total_files,
        'categories': categories,
        'fitness_files': len(fitness_files)
    }

def show_next_steps():
    """Show next steps for forum processing."""
    
    print(f"\n✅ NEXT STEPS")
    print("=" * 80)
    
    steps = [
        "1. Run: ./src/tools/download_remaining_forums.sh",
        "2. Wait for all forum categories to download",
        "3. Verify all forum HTML files are in data/raw/forum/",
        "4. Run Docling processing on data/raw/forum/ and data/raw/news/",
        "5. Build FAISS vector database from processed content",
        "6. Test MCP server with complete knowledge base"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n📁 CLEAN PROJECT STRUCTURE:")
    structure = [
        "data/raw/",
        "  ├── forum/          # All forum HTML files (wget output)",
        "  ├── news/           # 30 news HTML files (ready for Docling)",
        "  └── robots.txt      # Site robots.txt",
        "src/",
        "  ├── tools/          # All analysis and download scripts",
        "  ├── scraper/        # Core scraping modules",
        "  ├── rag/            # Docling and vector processing", 
        "  └── mcp/            # MCP server implementation"
    ]
    
    for line in structure:
        print(f"   {line}")

if __name__ == "__main__":
    print("🔧 WGET FORUM DOWNLOADER - UPDATED")
    print("=" * 80)
    
    # Create updated commands
    commands = create_updated_wget_commands()
    
    # Analyze current content
    current_content = analyze_current_forum_content()
    
    # Create download script
    script_file = create_forum_download_script()
    
    # Show next steps
    show_next_steps()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Current files: {current_content.get('total_files', 0)}")
    print(f"   Categories ready: {len(current_content.get('categories', {}))}")
    print(f"   Download script: {script_file}")
    print(f"   Output location: data/raw/forum/")
    
    print(f"\n🚀 Ready to download remaining forum categories!")