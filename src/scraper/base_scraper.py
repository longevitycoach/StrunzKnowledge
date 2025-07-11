import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


class StrunzScraper:
    def __init__(self, base_url: str = "https://www.strunz.com", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; StrunzKnowledgeBot/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def _make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries and delay."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)
                return response
            except requests.RequestException as e:
                logger.warning(f"Request failed for {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * (attempt + 1))
        return None
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse German date formats."""
        date_patterns = [
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',     # DD Month YYYY
        ]
        
        months_de = {
            'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
            'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12
        }
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text.lower())
            if match:
                try:
                    if '.' in date_text:
                        day, month, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                    else:
                        day, month_name, year = match.groups()
                        month = months_de.get(month_name.lower())
                        if month:
                            return datetime(int(year), month, int(day))
                except ValueError:
                    pass
        return None
    
    def _extract_pagination_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract pagination links from the page."""
        pagination_links = []
        
        # Common pagination patterns
        pagination_selectors = [
            'a.pagination-link',
            'a[href*="page="]',
            'a[href*="seite="]',
            '.pagination a',
            '.pager a',
            'a.next',
            'a.weiter'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in pagination_links:
                        pagination_links.append(full_url)
        
        return pagination_links
    
    def scrape_news(self) -> List[Dict]:
        """Scrape news articles from the news section."""
        news_url = f"{self.base_url}/news.html"
        articles = []
        visited_urls = set()
        urls_to_visit = [news_url]
        
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue
                
            logger.info(f"Scraping news from: {current_url}")
            visited_urls.add(current_url)
            
            response = self._make_request(current_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract articles
            article_selectors = [
                'article',
                '.news-item',
                '.artikel',
                'div[class*="news"]',
                'div[class*="artikel"]'
            ]
            
            for selector in article_selectors:
                items = soup.select(selector)
                for item in items:
                    article = self._extract_article_data(item, current_url)
                    if article and article['content']:
                        articles.append(article)
            
            # Find pagination links
            pagination_links = self._extract_pagination_links(soup)
            for link in pagination_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
        
        logger.info(f"Scraped {len(articles)} news articles")
        return articles
    
    def scrape_forum(self, category: str) -> List[Dict]:
        """Scrape forum posts from a specific category."""
        forum_url = f"{self.base_url}/forum/{category}"
        posts = []
        visited_urls = set()
        urls_to_visit = [forum_url]
        
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue
                
            logger.info(f"Scraping forum {category} from: {current_url}")
            visited_urls.add(current_url)
            
            response = self._make_request(current_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract forum threads
            thread_selectors = [
                'a[href*="/forum/"][href*="/t/"]',
                '.forum-thread a',
                '.thread-title a',
                'h3 a[href*="forum"]'
            ]
            
            thread_urls = []
            for selector in thread_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in thread_urls:
                            thread_urls.append(full_url)
            
            # Scrape each thread
            for thread_url in thread_urls:
                if thread_url not in visited_urls:
                    thread_posts = self._scrape_forum_thread(thread_url)
                    posts.extend(thread_posts)
                    visited_urls.add(thread_url)
            
            # Find pagination links
            pagination_links = self._extract_pagination_links(soup)
            for link in pagination_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
        
        logger.info(f"Scraped {len(posts)} forum posts from {category}")
        return posts
    
    def _scrape_forum_thread(self, thread_url: str) -> List[Dict]:
        """Scrape all posts from a forum thread."""
        posts = []
        response = self._make_request(thread_url)
        if not response:
            return posts
            
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract posts
        post_selectors = [
            '.forum-post',
            '.post',
            'article.post',
            'div[class*="post-content"]'
        ]
        
        for selector in post_selectors:
            items = soup.select(selector)
            for item in items:
                post = self._extract_post_data(item, thread_url)
                if post and post['content']:
                    posts.append(post)
        
        return posts
    
    def _extract_article_data(self, element: BeautifulSoup, source_url: str) -> Dict:
        """Extract article data from HTML element."""
        article = {
            'title': '',
            'content': '',
            'date': None,
            'source_url': source_url,
            'type': 'article'
        }
        
        # Extract title
        title_selectors = ['h1', 'h2', 'h3', '.title', '.headline']
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
                break
        
        # Extract content
        content_selectors = ['.content', '.text', '.body', 'p']
        content_parts = []
        for selector in content_selectors:
            content_elems = element.select(selector)
            for elem in content_elems:
                text = elem.get_text(strip=True)
                if text and len(text) > 20:
                    content_parts.append(text)
        
        article['content'] = '\n\n'.join(content_parts)
        
        # Extract date
        date_selectors = ['.date', '.datum', 'time', '.timestamp']
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                article['date'] = self._parse_date(date_text)
                if article['date']:
                    break
        
        return article
    
    def _extract_post_data(self, element: BeautifulSoup, source_url: str) -> Dict:
        """Extract forum post data from HTML element."""
        post = {
            'title': '',
            'content': '',
            'date': None,
            'author': '',
            'source_url': source_url,
            'type': 'forum_post'
        }
        
        # Extract author
        author_selectors = ['.author', '.username', '.user', '.poster']
        for selector in author_selectors:
            author_elem = element.select_one(selector)
            if author_elem:
                post['author'] = author_elem.get_text(strip=True)
                break
        
        # Extract content
        content_selectors = ['.post-content', '.message', '.post-text', '.content']
        for selector in content_selectors:
            content_elem = element.select_one(selector)
            if content_elem:
                post['content'] = content_elem.get_text(strip=True)
                break
        
        # Extract date
        date_selectors = ['.post-date', '.timestamp', 'time', '.date']
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                post['date'] = self._parse_date(date_text)
                if post['date']:
                    break
        
        return post