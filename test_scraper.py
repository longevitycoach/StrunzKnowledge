#!/usr/bin/env python3
"""Quick test scraper to get sample content for Docling preparation."""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import time

def scrape_sample_content():
    """Scrape a limited sample of content for testing."""
    
    # Create output directory
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_url = "https://www.strunz.com"
    
    # Test with just first page of news and one forum category
    urls_to_test = [
        ("news", f"{base_url}/news.html"),
        ("forum_fitness", f"{base_url}/forum/fitness")
    ]
    
    all_data = {}
    
    for category, url in urls_to_test:
        print(f"\nScraping {category} from {url}...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract sample content
            items = []
            
            # Try different selectors
            article_selectors = [
                'article',
                '.news-item', 
                '.artikel',
                'div[class*="news"]',
                '.forum-post',
                '.post'
            ]
            
            found_items = False
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  Found {len(elements)} items with selector: {selector}")
                    found_items = True
                    
                    for idx, elem in enumerate(elements[:5]):  # Just first 5 items
                        item = {
                            'id': f"{category}_{idx}",
                            'category': category,
                            'title': '',
                            'content': '',
                            'date': None,
                            'source_url': url
                        }
                        
                        # Extract title
                        for title_sel in ['h1', 'h2', 'h3', '.title', '.headline']:
                            title_elem = elem.select_one(title_sel)
                            if title_elem:
                                item['title'] = title_elem.get_text(strip=True)
                                break
                        
                        # Extract content
                        content_text = elem.get_text(separator='\n', strip=True)
                        item['content'] = content_text[:1000]  # First 1000 chars
                        
                        # Extract date
                        for date_sel in ['.date', '.datum', 'time']:
                            date_elem = elem.select_one(date_sel)
                            if date_elem:
                                item['date'] = date_elem.get_text(strip=True)
                                break
                        
                        items.append(item)
                    
                    break
            
            if not found_items:
                print(f"  No items found, saving page structure...")
                # Save page structure for analysis
                items.append({
                    'id': f"{category}_page",
                    'category': category,
                    'title': soup.title.string if soup.title else 'No title',
                    'content': soup.get_text()[:2000],
                    'date': datetime.now().isoformat(),
                    'source_url': url,
                    'html_sample': str(soup.prettify()[:1000])
                })
            
            all_data[category] = items
            
            # Save individual category file
            with open(output_dir / f"{category}_sample.json", 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            print(f"  Saved {len(items)} items to {category}_sample.json")
            
            time.sleep(1)  # Be polite
            
        except Exception as e:
            print(f"  Error scraping {category}: {e}")
            all_data[category] = []
    
    # Save combined data
    with open(output_dir / "sample_data.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # Generate summary
    print("\n" + "="*60)
    print("Scraping Summary:")
    for category, items in all_data.items():
        print(f"  {category}: {len(items)} items")
    print("="*60)
    
    return all_data

if __name__ == "__main__":
    scrape_sample_content()