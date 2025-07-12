#!/usr/bin/env python3
"""
Analyze the reindexed forum data
"""

import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def analyze_forum_data():
    """Analyze the processed forum data."""
    # Load the processed forum data
    forum_file = Path("data/processed/forum/forum_documents_20250712_211416.json")
    
    with open(forum_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"\n=== FORUM REINDEXING ANALYSIS ===")
    print(f"Total documents/chunks: {len(documents)}")
    
    # Analyze categories
    categories = Counter()
    authors = Counter()
    dates = []
    posts_with_likes = 0
    total_likes = 0
    user_posts = defaultdict(int)
    
    for doc in documents:
        meta = doc.get('metadata', {})
        
        # Category
        if 'category' in meta:
            categories[meta['category']] += 1
        
        # Post author
        if 'post_author' in meta:
            authors[meta['post_author']] += 1
            user_posts[meta['post_author']] += 1
        
        # Dates
        if 'post_date' in meta and meta['post_date']:
            dates.append(meta['post_date'])
        
        # Likes
        if 'post_likes' in meta and meta['post_likes'] > 0:
            posts_with_likes += 1
            total_likes += meta['post_likes']
    
    print(f"\n=== CATEGORIES ===")
    for category, count in categories.most_common():
        print(f"  - {category}: {count} chunks")
    
    print(f"\n=== TEMPORAL COVERAGE ===")
    if dates:
        print(f"  - Date range: {min(dates)} to {max(dates)}")
        print(f"  - Total dated posts: {len(dates)}")
        
        # Year distribution
        years = Counter()
        for date in dates:
            year = date[:4]
            years[year] += 1
        
        print(f"\n  Year distribution:")
        for year, count in sorted(years.items(), reverse=True)[:10]:
            print(f"    - {year}: {count} posts")
    
    print(f"\n=== USER ACTIVITY ===")
    print(f"  - Unique authors: {len(authors)}")
    print(f"  - Posts with likes: {posts_with_likes}")
    print(f"  - Total likes: {total_likes}")
    
    print(f"\n  Top 20 contributors:")
    for author, count in authors.most_common(20):
        print(f"    - {author}: {count} posts")
    
    # Sample post content
    print(f"\n=== SAMPLE POSTS ===")
    sample_count = 0
    for doc in documents:
        if 'post_author' in doc.get('metadata', {}) and sample_count < 3:
            meta = doc['metadata']
            print(f"\nPost by {meta.get('post_author', 'Unknown')} on {meta.get('post_date', 'Unknown date')}:")
            print(f"  Category: {meta.get('category', 'Unknown')}")
            print(f"  Likes: {meta.get('post_likes', 0)}")
            print(f"  Content preview: {doc['text'][:150]}...")
            sample_count += 1

if __name__ == "__main__":
    analyze_forum_data()