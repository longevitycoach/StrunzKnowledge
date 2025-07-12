#!/usr/bin/env python3
"""
Improved Strunz website scraper that extracts actual article content.
Optimized for Docling processing with structured HTML output.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StrunzContentScraper:
    def __init__(self, output_dir: str = "data/raw", max_articles: int = 10):
        self.base_url = "https://www.strunz.com"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_articles = max_articles
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; StrunzKnowledgeBot/1.0)'
        })
        
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article content."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            article = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'title': '',
                'date': '',
                'author': 'Dr. Ulrich Strunz',
                'content_html': '',
                'content_text': '',
                'category': self._determine_category(url)
            }
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('h2', class_='page-title')
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
            
            # Extract date
            date_patterns = [
                r'(\d{1,2}\.\d{1,2}\.\d{4})',
                r'(\d{4}-\d{2}-\d{2})'
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, soup.get_text())
                if date_match:
                    article['date'] = date_match.group(1)
                    break
            
            # Extract main content
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                'div[class*="content"]',
                'main'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, nav, .navigation, .social-share'):
                        unwanted.decompose()
                    
                    # Save both HTML and text versions
                    article['content_html'] = str(content_elem)
                    article['content_text'] = content_elem.get_text(separator='\n', strip=True)
                    
                    if len(article['content_text']) > 100:  # Valid content
                        break
            
            return article if article['content_text'] else None
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None
    
    def _determine_category(self, url: str) -> str:
        """Determine article category from URL."""
        if '/news/' in url:
            return 'News'
        elif '/forum/fitness' in url:
            return 'Forum: Fitness'
        elif '/forum/gesundheit' in url:
            return 'Forum: Gesundheit'
        elif '/forum/ernaehrung' in url:
            return 'Forum: Ernährung'
        elif '/forum/bluttuning' in url:
            return 'Forum: Bluttuning'
        elif '/forum/mental' in url:
            return 'Forum: Mental'
        elif '/forum/infektion' in url:
            return 'Forum: Prävention'
        return 'Unknown'
    
    def scrape_article_list(self, list_url: str) -> List[str]:
        """Extract article URLs from a listing page."""
        try:
            response = self.session.get(list_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            article_urls = []
            
            # Different patterns for news vs forum
            if '/forum/' in list_url:
                # Forum pages have different structure
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/forum/' in href and '/t/' in href:  # Forum threads
                        full_url = href if href.startswith('http') else self.base_url + href
                        if full_url not in article_urls:
                            article_urls.append(full_url)
            else:
                # News pages
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/news/' in href and href.endswith('.html'):
                        full_url = href if href.startswith('http') else self.base_url + href
                        if full_url not in article_urls:
                            article_urls.append(full_url)
            
            return article_urls[:self.max_articles] if self.max_articles else article_urls
            
        except Exception as e:
            logger.error(f"Error scraping article list {list_url}: {e}")
            return []
    
    def scrape_category(self, category_name: str, category_url: str):
        """Scrape all articles from a category."""
        logger.info(f"Scraping category: {category_name}")
        
        # Get article URLs
        article_urls = self.scrape_article_list(category_url)
        logger.info(f"Found {len(article_urls)} articles in {category_name}")
        
        # Scrape each article
        articles = []
        for idx, url in enumerate(article_urls):
            logger.info(f"Scraping article {idx+1}/{len(article_urls)}: {url}")
            
            article = self.scrape_article(url)
            if article:
                articles.append(article)
                
                # Save individual article for Docling
                self._save_article_for_docling(article, category_name, idx)
            
            time.sleep(1)  # Be polite
        
        # Save category summary
        self._save_category_summary(category_name, articles)
        
        return articles
    
    def _save_article_for_docling(self, article: Dict, category: str, index: int):
        """Save article in optimal format for Docling processing."""
        # Create category directory
        category_dir = self.output_dir / "docling_input" / category.replace(' ', '_').lower()
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as structured HTML for best Docling results
        html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="{article['author']}">
    <meta name="date" content="{article['date']}">
    <meta name="category" content="{category}">
    <title>{article['title']}</title>
</head>
<body>
    <article>
        <header>
            <h1>{article['title']}</h1>
            <p class="metadata">
                <span class="date">{article['date']}</span> | 
                <span class="author">{article['author']}</span> | 
                <span class="category">{category}</span>
            </p>
        </header>
        <div class="content">
            {article['content_html']}
        </div>
    </article>
</body>
</html>"""
        
        # Save HTML file
        filename = f"{index+1:03d}_{self._sanitize_filename(article['title'])}.html"
        filepath = category_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Saved article for Docling: {filepath}")
    
    def _save_category_summary(self, category: str, articles: List[Dict]):
        """Save category summary in JSON and Markdown."""
        # JSON summary
        summary_data = {
            'category': category,
            'scraped_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'articles': articles
        }
        
        json_path = self.output_dir / f"{category.replace(' ', '_').lower()}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        # Markdown summary for quick review
        md_path = self.output_dir / f"{category.replace(' ', '_').lower()}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {category}\n\n")
            f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Articles: {len(articles)}\n\n")
            
            for article in articles:
                f.write(f"## {article['title']}\n")
                f.write(f"- Date: {article['date']}\n")
                f.write(f"- URL: {article['url']}\n")
                f.write(f"- Content Length: {len(article['content_text'])} characters\n\n")
                f.write(f"{article['content_text'][:500]}...\n\n")
                f.write("---\n\n")
    
    def _sanitize_filename(self, title: str) -> str:
        """Create safe filename from title."""
        # Remove special characters
        safe_title = re.sub(r'[^\w\s-]', '', title)
        # Replace spaces with underscores
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        # Limit length
        return safe_title[:50].strip('_')
    
    def scrape_all(self):
        """Scrape all categories."""
        categories = [
            ("News", f"{self.base_url}/news.html"),
            # Add more categories as needed
            # ("Forum: Fitness", f"{self.base_url}/forum/fitness"),
            # ("Forum: Gesundheit", f"{self.base_url}/forum/gesundheit"),
        ]
        
        all_articles = {}
        
        for category_name, category_url in categories:
            articles = self.scrape_category(category_name, category_url)
            all_articles[category_name] = articles
        
        # Save overall summary
        self._save_overall_summary(all_articles)
        
        return all_articles
    
    def _save_overall_summary(self, all_articles: Dict):
        """Save overall scraping summary."""
        summary = {
            'scraped_at': datetime.now().isoformat(),
            'total_categories': len(all_articles),
            'total_articles': sum(len(articles) for articles in all_articles.values()),
            'categories': {
                cat: len(articles) for cat, articles in all_articles.items()
            }
        }
        
        summary_path = self.output_dir / "scraping_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\nScraping Complete!")
        logger.info(f"Total Categories: {summary['total_categories']}")
        logger.info(f"Total Articles: {summary['total_articles']}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"Docling Input: {self.output_dir / 'docling_input'}")


if __name__ == "__main__":
    # Run scraper with limited articles for testing
    scraper = StrunzContentScraper(max_articles=5)  # Limit to 5 articles per category for testing
    scraper.scrape_all()