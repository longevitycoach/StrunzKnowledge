#!/usr/bin/env python3
"""
Check Download Status - Shows current state of downloaded content
"""

from pathlib import Path

def check_status():
    """Check and display current download status"""
    
    print("=== StrunzKnowledge Download Status ===\n")
    
    # Check forum files
    forum_dir = Path("data/raw/forum")
    if forum_dir.exists():
        categories = {}
        total_forum = 0
        
        for html_file in forum_dir.rglob("*.html"):
            total_forum += 1
            # Get category from path
            rel_path = html_file.relative_to(forum_dir)
            
            # Determine proper category
            if "/" in str(rel_path):
                category = str(rel_path).split("/")[0]
            else:
                # Root level file - try to determine category from filename
                filename = html_file.name
                if "fitness" in filename:
                    category = "fitness"
                elif "ernaehrung" in filename:
                    category = "ernaehrung"
                elif "gesundheit" in filename:
                    category = "gesundheit"
                elif "bluttuning" in filename:
                    category = "bluttuning"
                elif "mental" in filename:
                    category = "mental"
                elif "infektion" in filename:
                    category = "infektion-und-praevention"
                else:
                    category = "other"
            
            categories[category] = categories.get(category, 0) + 1
        
        print("📚 FORUM CONTENT:")
        print(f"   Total files: {total_forum}")
        if categories:
            print("   By category:")
            for cat, count in sorted(categories.items()):
                print(f"     - {cat}: {count} files")
    else:
        print("❌ No forum content found")
    
    print()
    
    # Check news files
    news_dir = Path("data/raw/news")
    if news_dir.exists():
        news_files = list(news_dir.glob("*.html"))
        archive_files = [f for f in news_files if "archiv" in f.name]
        article_files = [f for f in news_files if "archiv" not in f.name]
        
        print("📰 NEWS CONTENT:")
        print(f"   Total files: {len(news_files)}")
        print(f"   Archive pages: {len(archive_files)}")
        print(f"   News articles: {len(article_files)}")
        
        if len(article_files) < 1000:
            print(f"   ⚠️  Warning: Expected ~7,000 articles, found {len(article_files)}")
    else:
        print("❌ No news content found")
    
    print()
    
    # Check for delta updates
    delta_dir = Path("data/raw/delta")
    if delta_dir.exists():
        delta_packages = list(delta_dir.glob("delta_*"))
        if delta_packages:
            print("🔄 DELTA UPDATES:")
            print(f"   Packages: {len(delta_packages)}")
            latest = max(delta_packages, key=lambda p: p.name)
            print(f"   Latest: {latest.name}")
    
    # Check metadata
    metadata_file = Path("data/update_metadata.json")
    if metadata_file.exists():
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
        if "last_run" in metadata:
            print(f"\n📅 Last update: {metadata['last_run']}")
    
    print("\n=== Summary ===")
    total_files = total_forum + len(news_files) if 'total_forum' in locals() else len(news_files) if 'news_files' in locals() else 0
    print(f"Total HTML files: {total_files}")
    
    if total_files == 0:
        print("\n⚠️  No content downloaded yet!")
        print("Run these commands to download content:")
        print("  python src/tools/wget_forum_downloader.py")
        print("  python src/tools/wget_news_simple.py")

if __name__ == "__main__":
    check_status()