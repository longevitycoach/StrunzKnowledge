#!/usr/bin/env python3
"""Analyze the HTML structure of Strunz website to improve scraping."""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

def analyze_page_structure(url):
    """Analyze the HTML structure of a page."""
    print(f"\nAnalyzing: {url}")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for main content areas
        print("\n1. Main content containers:")
        for selector in ['main', '#content', '.content', '.main-content', '#main']:
            elements = soup.select(selector)
            if elements:
                print(f"   Found {len(elements)} '{selector}' elements")
        
        # Look for article/post structures
        print("\n2. Article/Post structures:")
        article_selectors = [
            'article',
            '.post',
            '.news-item',
            '.artikel',
            'div[class*="artikel"]',
            'div[class*="post"]',
            '.blog-post',
            '.entry'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"   Found {len(elements)} '{selector}' elements")
                # Analyze first element
                first_elem = elements[0]
                print(f"   Sample classes: {first_elem.get('class', [])}")
                print(f"   Sample text (50 chars): {first_elem.get_text(strip=True)[:50]}...")
        
        # Look for specific Strunz content
        print("\n3. Looking for Strunz-specific content:")
        
        # Check for news items by looking for date patterns
        all_text = soup.get_text()
        import re
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
        dates_found = re.findall(date_pattern, all_text)
        print(f"   Found {len(dates_found)} date patterns (DD.MM.YYYY)")
        
        # Look for headlines
        print("\n4. Headlines found:")
        for tag in ['h1', 'h2', 'h3']:
            headlines = soup.find_all(tag)
            if headlines:
                print(f"   {tag}: {len(headlines)} found")
                for h in headlines[:3]:
                    print(f"      - {h.get_text(strip=True)[:60]}...")
        
        # Save page sample for manual inspection
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        sample_file = output_dir / f"page_structure_{url.split('/')[-1].replace('.', '_')}.html"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify()[:10000])  # First 10k chars
        print(f"\n5. Saved HTML sample to: {sample_file}")
        
        # Try to find actual news content
        print("\n6. Attempting to extract actual content:")
        
        # Method 1: Look for links to individual articles
        article_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/news/' in href or '/artikel/' in href or '/blog/' in href:
                article_links.append((a.get_text(strip=True), href))
        
        if article_links:
            print(f"   Found {len(article_links)} potential article links")
            for title, link in article_links[:5]:
                print(f"      - {title[:50]}... -> {link}")
        
        # Method 2: Look for specific content patterns
        content_divs = soup.find_all('div', class_=re.compile('content|artikel|post|entry'))
        if content_divs:
            print(f"\n   Found {len(content_divs)} content divs")
            for div in content_divs[:2]:
                text = div.get_text(strip=True)
                if len(text) > 100:  # Only meaningful content
                    print(f"      Content preview: {text[:200]}...")
        
        return soup
        
    except Exception as e:
        print(f"Error analyzing page: {e}")
        return None

# Analyze main pages
urls = [
    "https://www.strunz.com/news.html",
    "https://www.strunz.com/forum/fitness"
]

for url in urls:
    analyze_page_structure(url)