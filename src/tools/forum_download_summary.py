#!/usr/bin/env python3
"""
Forum Download Summary
======================

Analyzes and summarizes all downloaded forum content.

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
Status: PRODUCTION
"""

import os
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

def analyze_forum_downloads():
    """Analyze all downloaded forum content."""
    
    print("📊 STRUNZ FORUM DOWNLOAD ANALYSIS")
    print("=" * 80)
    
    forum_dir = Path("data/raw/forum")
    
    if not forum_dir.exists():
        print("❌ Forum directory not found")
        return
    
    # Collect statistics
    categories = defaultdict(lambda: {
        'threads': 0,
        'pagination': 0,
        'total': 0,
        'sample_threads': []
    })
    
    total_files = 0
    
    # Analyze all HTML files
    for html_file in forum_dir.glob("**/*.html"):
        total_files += 1
        
        # Determine category
        filename = html_file.name
        category = None
        
        # Category mapping
        category_keywords = {
            'fitness': 'fitness',
            'ernaehrung': 'ernährung',
            'gesundheit': 'gesundheit',
            'bluttuning': 'bluttuning',
            'mental': 'mental',
            'infektion-und-praevention': 'infektion_prävention'
        }
        
        for keyword, cat_name in category_keywords.items():
            if keyword in str(html_file):
                category = cat_name
                break
        
        if category:
            categories[category]['total'] += 1
            
            # Classify file type
            if '?p=' in filename or '&p=' in filename:
                categories[category]['pagination'] += 1
            else:
                categories[category]['threads'] += 1
                
                # Store sample thread names
                if len(categories[category]['sample_threads']) < 5:
                    clean_name = filename.replace('.html', '').replace('-', ' ')
                    categories[category]['sample_threads'].append(clean_name[:60])
    
    # Display results
    print(f"\n📁 TOTAL FILES DOWNLOADED: {total_files:,}")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in forum_dir.glob("**/*.html"))
    total_size_mb = total_size / (1024 * 1024)
    print(f"💾 TOTAL SIZE: {total_size_mb:.1f} MB")
    
    print(f"\n📊 BREAKDOWN BY CATEGORY:")
    print("-" * 60)
    
    grand_total_threads = 0
    grand_total_pagination = 0
    
    for category, stats in sorted(categories.items()):
        print(f"\n🏷️  {category.upper()}")
        print(f"   Total files: {stats['total']:,}")
        print(f"   Forum threads: {stats['threads']:,}")
        print(f"   Pagination files: {stats['pagination']:,}")
        
        grand_total_threads += stats['threads']
        grand_total_pagination += stats['pagination']
        
        if stats['sample_threads']:
            print(f"   Sample threads:")
            for i, thread in enumerate(stats['sample_threads'], 1):
                print(f"      {i}. {thread}...")
    
    print(f"\n📈 GRAND TOTALS:")
    print("-" * 60)
    print(f"   Total forum threads: {grand_total_threads:,}")
    print(f"   Total pagination files: {grand_total_pagination:,}")
    print(f"   Total HTML files: {total_files:,}")
    
    # Save summary to JSON
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_files': total_files,
        'total_size_mb': total_size_mb,
        'categories': dict(categories),
        'grand_totals': {
            'threads': grand_total_threads,
            'pagination': grand_total_pagination,
            'total': total_files
        }
    }
    
    summary_file = Path("data/raw/forum_download_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Summary saved to: {summary_file}")
    
    # Next steps
    print(f"\n✅ NEXT STEPS:")
    print("-" * 60)
    print("1. Run Docling processing on all HTML files")
    print("2. Extract text content and metadata")
    print("3. Build FAISS vector database")
    print("4. Test semantic search capabilities")
    print("5. Deploy MCP server with complete knowledge base")
    
    return summary

def check_download_status():
    """Check if downloads are still running."""
    
    print(f"\n🔄 DOWNLOAD STATUS:")
    print("-" * 60)
    
    import subprocess
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        wget_processes = [line for line in result.stdout.split('\n') if 'wget' in line and 'grep' not in line]
        
        if wget_processes:
            print(f"⏳ Active downloads: {len(wget_processes)}")
            for process in wget_processes:
                parts = process.split()
                if len(parts) > 10:
                    url = next((p for p in parts if 'strunz.com' in p), 'Unknown URL')
                    print(f"   - {url}")
        else:
            print("✅ All downloads completed!")
            
    except Exception as e:
        print(f"❌ Error checking downloads: {e}")

if __name__ == "__main__":
    print("🔍 ANALYZING STRUNZ FORUM DOWNLOADS")
    print("=" * 80)
    
    # Check download status
    check_download_status()
    
    # Analyze downloads
    summary = analyze_forum_downloads()
    
    print(f"\n🎯 DOWNLOAD ANALYSIS COMPLETE!")
    print(f"   All forum content is now in: data/raw/forum/")
    print(f"   Ready for Docling processing!")
    
    # Show sample Docling command
    print(f"\n💡 TO PROCESS WITH DOCLING:")
    print("-" * 60)
    print("python -m src.rag.docling_processor --input data/raw/forum --output data/processed/forum")
    print("python -m src.rag.docling_processor --input data/raw/news --output data/processed/news")