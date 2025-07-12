#!/usr/bin/env python3
"""
Analyze Wget Downloads
======================

Analyze the wget downloaded files to understand what content was successfully
retrieved and prepare commands for all 6 forum categories.

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
Status: ANALYSIS
"""

import os
from pathlib import Path
import json
from bs4 import BeautifulSoup
import re

def analyze_wget_fitness_downloads():
    """Analyze the wget downloads for fitness category."""
    
    print("🔍 ANALYZING WGET FITNESS DOWNLOADS")
    print("=" * 80)
    
    wget_dir = Path("wget/www.strunz.com/forum/fitness")
    
    if not wget_dir.exists():
        print("❌ Wget directory not found")
        return {}
    
    analysis = {
        'total_files': 0,
        'thread_files': 0,
        'pagination_files': 0,
        'category_files': 0,
        'sample_threads': [],
        'pagination_pattern': {},
        'content_analysis': {}
    }
    
    # Count and categorize files
    all_files = list(wget_dir.glob("**/*.html"))
    analysis['total_files'] = len(all_files)
    
    print(f"📊 DOWNLOAD STATISTICS:")
    print(f"   Total HTML files: {analysis['total_files']}")
    
    thread_files = []
    pagination_files = []
    category_files = []
    
    for file_path in all_files:
        filename = file_path.name
        
        # Categorize files
        if filename == "fitness.html":
            category_files.append(filename)
        elif "?p=" in filename:
            pagination_files.append(filename)
        elif filename.startswith("fitness?p="):
            pagination_files.append(filename)
        else:
            thread_files.append(filename)
    
    analysis['thread_files'] = len(thread_files)
    analysis['pagination_files'] = len(pagination_files)
    analysis['category_files'] = len(category_files)
    
    print(f"   Thread files: {analysis['thread_files']}")
    print(f"   Pagination files: {analysis['pagination_files']}")
    print(f"   Category files: {analysis['category_files']}")
    
    # Analyze pagination pattern
    category_pages = [f for f in pagination_files if f.startswith("fitness?p=")]
    thread_pages = [f for f in pagination_files if not f.startswith("fitness?p=")]
    
    print(f"   Category pagination: {len(category_pages)}")
    print(f"   Thread pagination: {len(thread_pages)}")
    
    # Extract page numbers to understand depth
    page_numbers = []
    for filename in category_pages:
        match = re.search(r'p=(\d+)', filename)
        if match:
            page_numbers.append(int(match.group(1)))
    
    if page_numbers:
        analysis['pagination_pattern'] = {
            'max_page': max(page_numbers),
            'min_page': min(page_numbers),
            'total_pages': len(set(page_numbers))
        }
        print(f"   Category pages range: {min(page_numbers)} to {max(page_numbers)}")
    
    # Sample thread analysis
    sample_threads = thread_files[:10]
    analysis['sample_threads'] = sample_threads
    
    print(f"\n📝 SAMPLE THREADS:")
    for i, thread in enumerate(sample_threads, 1):
        # Clean up thread name for display
        clean_name = thread.replace('.html', '').replace('-', ' ')
        print(f"   {i:2}. {clean_name[:60]}...")
    
    # Content quality analysis
    print(f"\n🔍 CONTENT QUALITY ANALYSIS:")
    
    # Analyze a few sample files
    sample_files = all_files[:5]
    content_analysis = {}
    
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup.select('script, style'):
                    script.decompose()
                
                text_content = soup.get_text()
                
                file_analysis = {
                    'file_size': len(content),
                    'text_length': len(text_content),
                    'has_javascript_warning': 'JavaScript scheint' in text_content,
                    'forum_indicators': {
                        'kommentar': text_content.lower().count('kommentar'),
                        'beitrag': text_content.lower().count('beitrag'),
                        'antwort': text_content.lower().count('antwort'),
                        'benutzer': text_content.lower().count('benutzer')
                    }
                }
                
                content_analysis[file_path.name] = file_analysis
                
        except Exception as e:
            print(f"   ❌ Error analyzing {file_path.name}: {e}")
    
    analysis['content_analysis'] = content_analysis
    
    # Display content analysis results
    for filename, data in content_analysis.items():
        print(f"   📄 {filename}:")
        print(f"      File size: {data['file_size']:,} bytes")
        print(f"      Text length: {data['text_length']:,} chars")
        print(f"      JavaScript warning: {'Yes' if data['has_javascript_warning'] else 'No'}")
        
        forum_total = sum(data['forum_indicators'].values())
        print(f"      Forum indicators: {forum_total}")
        
        if forum_total > 0:
            print(f"         Details: {data['forum_indicators']}")
    
    return analysis

def create_wget_commands_for_all_categories():
    """Create wget commands for all 6 forum categories."""
    
    print(f"\n\n🚀 CREATING WGET COMMANDS FOR ALL CATEGORIES")
    print("=" * 80)
    
    # Forum categories mapping
    categories = {
        'fitness': 'fitness',
        'gesundheit': 'gesundheit', 
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    base_command = """wget --recursive --level=5 --page-requisites --html-extension --convert-links --domains=strunz.com,www.strunz.com --no-parent --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" --wait=1 --random-wait --accept-regex=".*{category}.*" --reject-regex=".*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/{url_name}"""
    
    commands = {}
    
    print("📋 WGET COMMANDS FOR ALL CATEGORIES:")
    print("-" * 60)
    
    for category_key, url_name in categories.items():
        command = base_command.format(category=url_name, url_name=url_name)
        commands[category_key] = command
        
        print(f"\n🏷️  {category_key.upper()} ({url_name}):")
        print(f"   Command:")
        print(f"   {command}")
    
    # Save commands to file
    commands_file = Path("wget_commands_all_categories.txt")
    
    with open(commands_file, 'w', encoding='utf-8') as f:
        f.write("# WGET COMMANDS FOR ALL STRUNZ FORUM CATEGORIES\n")
        f.write("# Generated: 2025-07-11\n")
        f.write("# Author: Matthias Buchhorn\n")
        f.write("# Project: StrunzKnowledgeMCP\n\n")
        
        for category_key, url_name in categories.items():
            f.write(f"# {category_key.upper()} ({url_name})\n")
            command = base_command.format(category=url_name, url_name=url_name)
            f.write(f"{command}\n\n")
    
    print(f"\n💾 Commands saved to: {commands_file}")
    
    return commands

def create_batch_download_script():
    """Create a batch script to download all categories."""
    
    print(f"\n📜 CREATING BATCH DOWNLOAD SCRIPT")
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
# Download All Strunz Forum Categories
# ===================================
# 
# Batch script to download all forum categories using wget
# Author: Matthias Buchhorn
# Project: StrunzKnowledgeMCP
# 

echo "🚀 Starting Strunz Forum Download - All Categories"
echo "=================================================="

# Base wget command template
BASE_CMD="wget --recursive --level=5 --page-requisites --html-extension --convert-links --domains=strunz.com,www.strunz.com --no-parent --user-agent=\\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\\" --wait=1 --random-wait"

# Note: fitness is already downloaded
echo "✅ Fitness category already downloaded"

'''
    
    for category_key, url_name in categories.items():
        script_content += f'''
echo ""
echo "📥 Downloading {category_key.upper()} ({url_name})"
echo "{'='*50}"

$BASE_CMD --accept-regex=".*{url_name}.*" --reject-regex=".*\\.(exe|zip|rar|tar|gz|pdf|doc|docx|xls|xlsx|ppt|pptx|mp3|mp4|avi|mov|wmv|flv|swf)$" https://www.strunz.com/forum/{url_name}

if [ $? -eq 0 ]; then
    echo "✅ {category_key.upper()} download completed successfully"
else
    echo "❌ {category_key.upper()} download failed"
fi
'''
    
    script_content += '''
echo ""
echo "🏁 All downloads completed!"
echo "=========================="

# Show download summary
echo ""
echo "📊 DOWNLOAD SUMMARY:"
find wget -name "*.html" | wc -l | xargs echo "   Total HTML files:"
du -sh wget | cut -f1 | xargs echo "   Total size:"
'''
    
    script_file = Path("download_all_forums.sh")
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_file, 0o755)
    
    print(f"✅ Batch script created: {script_file}")
    print(f"   To run: ./{script_file}")
    
    return script_file

def show_next_steps():
    """Show recommended next steps."""
    
    print(f"\n\n✅ NEXT STEPS RECOMMENDATION")
    print("=" * 80)
    
    steps = [
        "1. Review wget fitness analysis results above",
        "2. Run batch download script: ./download_all_forums.sh", 
        "3. Wait for all downloads to complete (may take 30-60 minutes)",
        "4. Analyze all downloaded content for forum posts and comments",
        "5. Process content through Docling OCR pipeline",
        "6. Build comprehensive FAISS vector database",
        "7. Test MCP server with complete forum knowledge base"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n💡 ADVANTAGES OF WGET APPROACH:")
    advantages = [
        "✅ Successfully bypasses JavaScript requirements",
        "✅ Downloads complete thread structures with pagination", 
        "✅ Respects robots.txt and implements delays",
        "✅ Gets actual forum content (not just error messages)",
        "✅ Scalable to all forum categories",
        "✅ Creates local backup of all forum data"
    ]
    
    for advantage in advantages:
        print(f"   {advantage}")

if __name__ == "__main__":
    print("🔍 WGET DOWNLOAD ANALYSIS")
    print("=" * 80)
    
    # Analyze existing fitness downloads
    fitness_analysis = analyze_wget_fitness_downloads()
    
    # Create commands for all categories
    all_commands = create_wget_commands_for_all_categories()
    
    # Create batch download script
    batch_script = create_batch_download_script()
    
    # Show next steps
    show_next_steps()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Fitness files analyzed: {fitness_analysis.get('total_files', 0)}")
    print(f"   Commands created for: {len(all_commands)} categories")
    print(f"   Batch script ready: {batch_script}")
    
    print(f"\n🚀 Ready to download all forum categories!")