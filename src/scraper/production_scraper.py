#!/usr/bin/env python3
"""
Production-ready StrunzKnowledge scraper with unlimited content extraction.
Implements complete pagination crawling for all forum categories and news.
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

from typing import List, Dict, Optional, Set, Tuple
import time
import logging
import signal
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
import re
import json
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScrapingStats:
    """Statistics for scraping session."""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_pages_visited: int = 0
    total_articles_found: int = 0
    total_articles_saved: int = 0
    total_forum_posts_found: int = 0
    total_forum_posts_saved: int = 0
    categories_completed: int = 0
    categories_failed: int = 0
    errors_encountered: int = 0
    
    @property
    def duration(self) -> str:
        if self.end_time:
            return str(self.end_time - self.start_time)
        return str(datetime.now() - self.start_time)


class ProductionStrunzScraper:
    """Production-ready scraper with unlimited crawling capabilities."""
    
    # All forum categories with correct URL patterns
    FORUM_CATEGORIES = {
        'fitness': 'fitness',
        'gesundheit': 'gesundheit', 
        'ernährung': 'ernaehrung',  # URL encoding fix
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'  # Full category name
    }
    
    def __init__(self, 
                 base_url: str = "https://www.strunz.com",
                 delay: float = 1.5,
                 use_selenium: bool = True,
                 max_pages_per_category: Optional[int] = None,
                 min_content_score: float = 0.4):
        """
        Initialize production scraper.
        
        Args:
            base_url: Base URL for strunz.com
            delay: Delay between requests in seconds
            use_selenium: Whether to use Selenium for JS-heavy content
            max_pages_per_category: Maximum pages per category (None = unlimited)
            min_content_score: Minimum quality score for content inclusion
        """
        self.base_url = base_url
        self.delay = delay
        self.use_selenium = use_selenium
        self.max_pages_per_category = max_pages_per_category
        self.min_content_score = min_content_score
        
        # Statistics tracking
        self.stats = ScrapingStats(start_time=datetime.now())
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
        })
        
        # Selenium driver
        self.driver = None
        
        # Interrupt handling
        self.interrupted = False
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Visited URLs tracking to avoid duplicates
        self.visited_urls: Set[str] = set()
        
        logger.info(f"Production scraper initialized - Max pages per category: {max_pages_per_category or 'Unlimited'}")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        logger.info("Interrupt signal received. Finishing current operation...")
        self.interrupted = True
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with production-optimized settings."""
        if self.driver:
            return self.driver
            
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver initialized successfully")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            raise
    
    def _close_driver(self):
        """Close WebDriver safely."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Chrome WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
    
    def _make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries and exponential backoff."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)
                return response
            except requests.RequestException as e:
                wait_time = self.delay * (2 ** attempt)
                logger.warning(f"Request failed for {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    logger.info(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    self.stats.errors_encountered += 1
        return None
    
    def _get_page_content(self, url: str, wait_for_selector: str = None) -> Optional[BeautifulSoup]:
        """Get page content using Selenium or requests based on configuration."""
        if self.interrupted:
            return None
            
        if self.use_selenium:
            try:
                driver = self._setup_driver()
                logger.debug(f"Loading page with Selenium: {url}")
                driver.get(url)
                
                if wait_for_selector:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                    )
                else:
                    time.sleep(3)  # Allow page to load
                
                html = driver.page_source
                return BeautifulSoup(html, 'lxml')
                
            except (TimeoutException, WebDriverException) as e:
                logger.warning(f"Selenium failed for {url}: {e}")
                # Fallback to requests
                response = self._make_request(url)
                if response:
                    return BeautifulSoup(response.content, 'lxml')
            except Exception as e:
                logger.error(f"Unexpected error with Selenium for {url}: {e}")
                self.stats.errors_encountered += 1
        else:
            response = self._make_request(url)
            if response:
                return BeautifulSoup(response.content, 'lxml')
        
        return None
    
    def _extract_pagination_urls(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all pagination URLs from current page."""
        pagination_urls = []
        
        # Multiple pagination patterns
        pagination_selectors = [
            'a[href*="?p="]',  # Standard pagination
            'a[href*="&p="]',  # Alternative pagination  
            '.pagination a',
            '.pager a',
            'a.next',
            'a[title*="Seite"]',  # German "Page"
            'a[title*="weiter"]', # German "next"
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Handle relative URLs
                    full_url = urljoin(current_url, href)
                    
                    # Extract page number to avoid infinite loops
                    parsed = urlparse(full_url)
                    query_params = parse_qs(parsed.query)
                    
                    if 'p' in query_params:
                        try:
                            page_num = int(query_params['p'][0])
                            if page_num > 1 and full_url not in pagination_urls:
                                pagination_urls.append(full_url)
                        except (ValueError, IndexError):
                            continue
        
        return sorted(list(set(pagination_urls)))  # Remove duplicates and sort
    
    def _discover_all_pages(self, base_url: str, max_pages: Optional[int] = None) -> List[str]:
        """Discover all paginated URLs for a category."""
        logger.info(f"Discovering pagination for: {base_url}")
        
        all_urls = [base_url]
        discovered_pages = set([base_url])
        
        # Get first page to discover pagination
        soup = self._get_page_content(base_url)
        if not soup:
            logger.warning(f"Could not load base URL: {base_url}")
            return all_urls
        
        # Extract pagination links
        pagination_urls = self._extract_pagination_urls(soup, base_url)
        
        if pagination_urls:
            logger.info(f"Found {len(pagination_urls)} pagination links")
            
            # If max_pages is set, limit discovery
            if max_pages:
                # Parse page numbers and take only up to max_pages
                page_numbers = []
                for url in pagination_urls:
                    parsed = urlparse(url)
                    query_params = parse_qs(parsed.query)
                    if 'p' in query_params:
                        try:
                            page_num = int(query_params['p'][0])
                            page_numbers.append((page_num, url))
                        except (ValueError, IndexError):
                            continue
                
                # Sort by page number and take up to max_pages
                page_numbers.sort()
                limited_urls = [url for page_num, url in page_numbers[:max_pages-1]]  # -1 because we already have base
                all_urls.extend(limited_urls)
            else:
                # Add all discovered pages
                all_urls.extend(pagination_urls)
        
        logger.info(f"Total pages to scrape: {len(all_urls)}")
        return all_urls
    
    def scrape_news_complete(self) -> List[Dict]:
        """Scrape all news articles with complete pagination."""
        logger.info("Starting complete news scraping...")
        
        news_base_url = f"{self.base_url}/news.html"
        all_articles = []
        
        # Discover all news pages
        news_pages = self._discover_all_pages(news_base_url, self.max_pages_per_category)
        
        for page_url in news_pages:
            if self.interrupted:
                logger.info("Scraping interrupted during news extraction")
                break
                
            logger.info(f"Scraping news page: {page_url}")
            self.stats.total_pages_visited += 1
            
            soup = self._get_page_content(page_url)
            if not soup:
                continue
            
            # Extract article links
            article_links = self._extract_news_article_links(soup)
            self.stats.total_articles_found += len(article_links)
            
            # Scrape each article
            for article_url in article_links:
                if self.interrupted:
                    break
                    
                if article_url in self.visited_urls:
                    continue
                    
                article = self._scrape_single_article(article_url)
                if article and self._meets_quality_threshold(article):
                    all_articles.append(article)
                    self.stats.total_articles_saved += 1
                    logger.info(f"Saved article: {article.get('title', 'Untitled')[:50]}...")
                
                self.visited_urls.add(article_url)
        
        logger.info(f"Completed news scraping: {len(all_articles)} articles")
        return all_articles
    
    def scrape_forum_complete(self, category_key: str) -> List[Dict]:
        """Scrape complete forum category with all pagination."""
        if category_key not in self.FORUM_CATEGORIES:
            logger.error(f"Unknown forum category: {category_key}")
            return []
        
        category_url_name = self.FORUM_CATEGORIES[category_key]
        forum_base_url = f"{self.base_url}/forum/{category_url_name}"
        
        logger.info(f"Starting complete forum scraping for {category_key} ({category_url_name})")
        
        all_posts = []
        
        # Discover all forum pages
        forum_pages = self._discover_all_pages(forum_base_url, self.max_pages_per_category)
        
        for page_url in forum_pages:
            if self.interrupted:
                logger.info(f"Scraping interrupted during {category_key} forum extraction")
                break
                
            logger.info(f"Scraping forum page: {page_url}")
            self.stats.total_pages_visited += 1
            
            soup = self._get_page_content(page_url, wait_for_selector="a[href*='/forum/']")
            if not soup:
                continue
            
            # Extract thread links
            thread_links = self._extract_forum_thread_links(soup, category_url_name)
            
            # Scrape each thread
            for thread_url in thread_links:
                if self.interrupted:
                    break
                    
                if thread_url in self.visited_urls:
                    continue
                
                thread_posts = self._scrape_forum_thread(thread_url, category_key)
                
                # Filter posts by quality
                quality_posts = [post for post in thread_posts if self._meets_quality_threshold(post)]
                all_posts.extend(quality_posts)
                
                self.stats.total_forum_posts_found += len(thread_posts)
                self.stats.total_forum_posts_saved += len(quality_posts)
                
                if quality_posts:
                    logger.info(f"Saved {len(quality_posts)} posts from thread: {thread_url}")
                
                self.visited_urls.add(thread_url)
        
        logger.info(f"Completed forum scraping for {category_key}: {len(all_posts)} posts")
        return all_posts
    
    def _extract_news_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract news article links from news listing page."""
        article_links = []
        
        # Multiple selectors for news articles
        link_selectors = [
            'a[href*="/news/"]',
            'a[href$=".html"]',
            '.news-item a',
            '.article-link',
            'h1 a', 'h2 a', 'h3 a',
            '.post-title a',
            '.entry-title a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/news/' in href and href.endswith('.html'):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in article_links:
                        article_links.append(full_url)
        
        return article_links
    
    def _extract_forum_thread_links(self, soup: BeautifulSoup, category_name: str) -> List[str]:
        """Extract forum thread links from forum listing page."""
        thread_links = []
        
        # Forum-specific selectors
        thread_selectors = [
            f'a[href*="/forum/{category_name}/"]',
            'a[href*="/forum/"][href*="/t/"]',  # Traditional forum pattern
            '.forum-thread a',
            '.thread-title a',
            'h3 a[href*="forum"]',
            '.post-title a[href*="forum"]'
        ]
        
        for selector in thread_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and f'/forum/{category_name}/' in href:
                    full_url = urljoin(self.base_url, href)
                    # Avoid pagination URLs and self-references
                    if '?p=' not in full_url and full_url.rstrip('/') != f"{self.base_url}/forum/{category_name}":
                        if full_url not in thread_links:
                            thread_links.append(full_url)
        
        return thread_links
    
    def _scrape_single_article(self, article_url: str) -> Optional[Dict]:
        """Scrape a single news article."""
        soup = self._get_page_content(article_url)
        if not soup:
            return None
        
        article = {
            'title': '',
            'content': '',
            'date': None,
            'author': '',
            'source_url': article_url,
            'type': 'news_article',
            'category': 'news',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract title
        title_selectors = ['h1', 'title', '.article-title', '.news-title', '.post-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    article['title'] = self._clean_text(title)
                    break
        
        # Extract content with enhanced selectors
        content_selectors = [
            '.post-content',
            '.article-content', 
            '.news-content',
            '.content',
            '.post-text',
            '.entry-content',
            'main article',
            '.main-content'
        ]
        
        best_content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select('script, style, .ads, .advertisement, .social-share, nav'):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                content = self._clean_text(content)
                
                if len(content) > len(best_content):
                    best_content = content
        
        article['content'] = best_content
        
        # Extract additional metadata
        self._extract_metadata(soup, article)
        
        return article if article['content'] and article['title'] else None
    
    def _scrape_forum_thread(self, thread_url: str, category: str) -> List[Dict]:
        """Scrape all posts from a forum thread."""
        soup = self._get_page_content(thread_url, wait_for_selector=".post, .forum-post, article")
        if not soup:
            return []
        
        posts = []
        
        # Find post containers
        post_selectors = ['.post', '.forum-post', 'article', '.message', '.comment', '.reply']
        
        post_elements = []
        for selector in post_selectors:
            elements = soup.select(selector)
            if elements:
                post_elements = elements
                break
        
        thread_title = self._extract_thread_title(soup)
        
        for i, post_elem in enumerate(post_elements):
            post = {
                'title': thread_title if i == 0 else '',
                'content': '',
                'date': None,
                'author': '',
                'source_url': thread_url,
                'type': 'forum_post',
                'category': f'forum_{category}',
                'post_number': i + 1,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract post content and metadata
            self._extract_post_content(post_elem, post)
            
            if post['content']:
                posts.append(post)
        
        return posts
    
    def _extract_thread_title(self, soup: BeautifulSoup) -> str:
        """Extract thread title from forum page."""
        title_selectors = ['h1', 'h2', '.thread-title', '.post-title', '.page-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return self._clean_text(title_elem.get_text(strip=True))
        return ""
    
    def _extract_post_content(self, post_elem: BeautifulSoup, post: Dict):
        """Extract content and metadata from a forum post element."""
        # Extract author
        author_selectors = ['.author', '.username', '.user', '.poster', '.post-author']
        for selector in author_selectors:
            author_elem = post_elem.select_one(selector)
            if author_elem:
                post['author'] = self._clean_text(author_elem.get_text(strip=True))
                break
        
        # Extract content
        content_selectors = ['.post-content', '.message', '.post-text', '.content', '.post-body']
        for selector in content_selectors:
            content_elem = post_elem.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select('script, style, .signature, .quote'):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                post['content'] = self._clean_text(content)
                break
        
        # Extract date
        self._extract_metadata(post_elem, post)
    
    def _extract_metadata(self, soup: BeautifulSoup, item: Dict):
        """Extract metadata (date, author) from page."""
        # Extract date
        date_selectors = ['.date', '.post-date', '.timestamp', 'time', '.meta .date']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                if not date_text and date_elem.get('datetime'):
                    date_text = date_elem.get('datetime')
                
                if date_text:
                    item['date'] = self._parse_date(date_text)
                    if item['date']:
                        break
        
        # Extract author if not already set
        if not item.get('author'):
            author_selectors = ['.author', '.post-author', '.by-author', 'span[class*="author"]']
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    if author:
                        item['author'] = self._clean_text(author)
                        break
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie[s]?\s+akzeptieren',
            r'Datenschutz[erklärung]*',
            r'Impressum',
            r'Newsletter\s+abonnieren',
            r'Jetzt\s+registrieren',
            r'Anmelden',
            r'© \d{4}',
            r'Alle Rechte vorbehalten',
            r'Weiterlesen\s*[>»]*',
            r'Kommentare?\s*\(\d+\)',
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Fix encoding issues
        text = text.replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã¼', 'ü')
        text = text.replace('Ã„', 'Ä').replace('Ã–', 'Ö').replace('Ãœ', 'Ü')
        text = text.replace('ÃŸ', 'ß')
        
        return text.strip()
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parse German date formats and return ISO format."""
        if not date_text:
            return None
            
        date_patterns = [
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',     # DD Month YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',     # YYYY-MM-DD
        ]
        
        months_de = {
            'januar': 1, 'februar': 2, 'märz': 3, 'april': 4,
            'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12,
            'jan': 1, 'feb': 2, 'mär': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'dez': 12
        }
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text.lower())
            if match:
                try:
                    if '.' in date_text:
                        day, month, year = match.groups()
                        date_obj = datetime(int(year), int(month), int(day))
                    elif '-' in date_text:
                        year, month, day = match.groups()
                        date_obj = datetime(int(year), int(month), int(day))
                    else:
                        day, month_name, year = match.groups()
                        month = months_de.get(month_name.lower())
                        if month:
                            date_obj = datetime(int(year), month, int(day))
                        else:
                            continue
                    return date_obj.isoformat()
                except ValueError:
                    continue
        return None
    
    def _meets_quality_threshold(self, item: Dict) -> bool:
        """Check if content meets minimum quality threshold."""
        content = item.get('content', '')
        if not content:
            return False
        
        # Basic quality checks
        word_count = len(content.split())
        char_count = len(content)
        
        # Minimum thresholds
        if word_count < 20 or char_count < 100:
            return False
        
        # Health/nutrition relevance check
        health_keywords = [
            'gesundheit', 'ernährung', 'fitness', 'vitamin', 'mineral', 'protein',
            'training', 'körper', 'bewegung', 'prävention', 'therapie', 'studien',
            'forschung', 'wissenschaft', 'medizin', 'arzt', 'patient', 'behandlung',
            'omega', 'fettsäuren', 'entzündung', 'immunsystem', 'blut', 'stoffwechsel',
            'hormone', 'zellen', 'mitochondrien', 'antioxidantien', 'aminosäure',
            'krankheit', 'heilung', 'regeneration', 'leistung', 'energie', 'muskeln'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in health_keywords if keyword in content_lower)
        
        # Quality score calculation
        score = 0.0
        
        # Word count score
        if word_count >= 100:
            score += 0.3
        elif word_count >= 50:
            score += 0.2
        elif word_count >= 30:
            score += 0.1
        
        # Health relevance score
        if keyword_count >= 3:
            score += 0.4
        elif keyword_count >= 2:
            score += 0.3
        elif keyword_count >= 1:
            score += 0.2
        
        # Structure score
        if any(indicator in content_lower for indicator in ['http', 'www.', ':', '?', '!']):
            score += 0.1
        
        return score >= self.min_content_score
    
    def run_complete_scraping(self) -> Dict:
        """Run complete unlimited scraping of all categories."""
        logger.info("Starting COMPLETE UNLIMITED SCRAPING")
        logger.info(f"Max pages per category: {self.max_pages_per_category or 'UNLIMITED'}")
        logger.info(f"Forum categories: {list(self.FORUM_CATEGORIES.keys())}")
        
        results = {
            'news': [],
            'forums': {}
        }
        
        try:
            # Scrape news (unlimited)
            if not self.interrupted:
                logger.info("=== SCRAPING NEWS (UNLIMITED) ===")
                results['news'] = self.scrape_news_complete()
            
            # Scrape all forum categories (unlimited)
            for category_key in self.FORUM_CATEGORIES.keys():
                if self.interrupted:
                    logger.info("Scraping interrupted. Stopping...")
                    break
                
                logger.info(f"=== SCRAPING FORUM: {category_key.upper()} (UNLIMITED) ===")
                try:
                    results['forums'][category_key] = self.scrape_forum_complete(category_key)
                    self.stats.categories_completed += 1
                except Exception as e:
                    logger.error(f"Failed to scrape forum {category_key}: {e}")
                    self.stats.categories_failed += 1
                    self.stats.errors_encountered += 1
                    results['forums'][category_key] = []
        
        except Exception as e:
            logger.error(f"Critical error during scraping: {e}")
            self.stats.errors_encountered += 1
        
        finally:
            self.stats.end_time = datetime.now()
            self._close_driver()
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive scraping statistics."""
        return {
            'start_time': self.stats.start_time.isoformat(),
            'end_time': self.stats.end_time.isoformat() if self.stats.end_time else None,
            'duration': self.stats.duration,
            'total_pages_visited': self.stats.total_pages_visited,
            'total_articles_found': self.stats.total_articles_found,
            'total_articles_saved': self.stats.total_articles_saved,
            'total_forum_posts_found': self.stats.total_forum_posts_found,
            'total_forum_posts_saved': self.stats.total_forum_posts_saved,
            'categories_completed': self.stats.categories_completed,
            'categories_failed': self.stats.categories_failed,
            'errors_encountered': self.stats.errors_encountered,
            'interrupted': self.interrupted,
            'unique_urls_visited': len(self.visited_urls)
        }
    
    def close(self):
        """Clean up resources."""
        self._close_driver()
        if self.session:
            self.session.close()