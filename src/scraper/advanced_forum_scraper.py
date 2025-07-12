#!/usr/bin/env python3
"""
Advanced Forum Scraper - Production Ready
========================================

Solves technical challenges with dynamic content, enhanced session handling,
and complete comment extraction via pagination. Follows "Beitrag" links and
extracts all "Kommentar" content through pagination crawling.

Status: PRODUCTION
Usage: Complete forum scraping with dynamic content and comment pagination
Dependencies: selenium, requests, beautifulsoup4

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
Last Updated: 2025-07-11
Features:
- Enhanced session handling with cookie persistence
- Dynamic content loading with JavaScript execution
- Complete comment pagination crawling
- CSRF token handling
- Respectful rate limiting
- Comprehensive error recovery
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import logging
import re
import json
import pickle
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ForumComment:
    """Represents a single forum comment."""
    id: str
    content: str
    author: str
    author_id: Optional[str]
    timestamp: Optional[datetime]
    post_number: int
    thread_url: str
    page_number: int
    like_count: int = 0
    reply_to: Optional[str] = None
    user_metadata: Optional[Dict] = None


@dataclass
class ForumThread:
    """Represents a complete forum thread with all comments."""
    url: str
    title: str
    category: str
    author: str
    created_date: Optional[datetime]
    total_pages: int
    total_comments: int
    comments: List[ForumComment]
    metadata: Dict


class SessionManager:
    """Manages persistent sessions with cookie handling and CSRF protection."""
    
    def __init__(self, base_url: str = "https://www.strunz.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.session_file = Path("data/session_cache.pkl")
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        })
    
    def initialize_session(self) -> bool:
        """Initialize session with proper cookies and CSRF token."""
        try:
            # Load existing session if available
            if self._load_session():
                logger.info("Loaded existing session from cache")
                if self._validate_session():
                    return True
                else:
                    logger.info("Cached session invalid, creating new session")
            
            # Create new session
            logger.info("Initializing new session")
            
            # Step 1: Visit main page to establish session
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Step 2: Visit forum page to get forum-specific cookies
            forum_url = f"{self.base_url}/forum/"
            response = self.session.get(forum_url, timeout=30)
            response.raise_for_status()
            
            # Step 3: Extract CSRF token if present
            soup = BeautifulSoup(response.content, 'html.parser')
            self._extract_csrf_token(soup)
            
            # Step 4: Save session
            self._save_session()
            
            logger.info("Session initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def _extract_csrf_token(self, soup: BeautifulSoup):
        """Extract CSRF token from page."""
        # Look for form_key or csrf token
        csrf_input = soup.find('input', {'name': 'form_key'})
        if csrf_input:
            self.csrf_token = csrf_input.get('value')
            logger.debug(f"Extracted CSRF token: {self.csrf_token[:10]}...")
        
        # Also check meta tags
        csrf_meta = soup.find('meta', {'name': 'csrf-token'}) or soup.find('meta', {'name': '_token'})
        if csrf_meta and not self.csrf_token:
            self.csrf_token = csrf_meta.get('content')
            logger.debug(f"Extracted CSRF token from meta: {self.csrf_token[:10]}...")
    
    def _save_session(self):
        """Save session cookies and state to file."""
        try:
            session_data = {
                'cookies': requests.utils.dict_from_cookiejar(self.session.cookies),
                'csrf_token': self.csrf_token,
                'timestamp': datetime.now().isoformat()
            }
            
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.session_file, 'wb') as f:
                pickle.dump(session_data, f)
            
            logger.debug("Session saved to cache")
            
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")
    
    def _load_session(self) -> bool:
        """Load session from cache file."""
        try:
            if not self.session_file.exists():
                return False
            
            with open(self.session_file, 'rb') as f:
                session_data = pickle.load(f)
            
            # Check if session is not too old (24 hours)
            timestamp = datetime.fromisoformat(session_data['timestamp'])
            if datetime.now() - timestamp > timedelta(hours=24):
                logger.debug("Cached session too old")
                return False
            
            # Restore cookies
            cookie_dict = session_data['cookies']
            requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie_dict)
            
            # Restore CSRF token
            self.csrf_token = session_data.get('csrf_token')
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return False
    
    def _validate_session(self) -> bool:
        """Validate that the session is still working."""
        try:
            # Test with a simple forum request
            test_url = f"{self.base_url}/forum/"
            response = self.session.get(test_url, timeout=15)
            
            # Check if we get redirected to login or get forbidden
            if response.status_code == 200 and 'login' not in response.url.lower():
                logger.debug("Session validation successful")
                return True
            else:
                logger.debug("Session validation failed")
                return False
                
        except Exception as e:
            logger.warning(f"Session validation error: {e}")
            return False
    
    def get_session(self) -> requests.Session:
        """Get the configured session."""
        return self.session
    
    def get_csrf_token(self) -> Optional[str]:
        """Get the current CSRF token."""
        return self.csrf_token


class DynamicContentHandler:
    """Handles JavaScript-rendered content and dynamic loading."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.driver = None
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver for dynamic content."""
        if self.driver:
            return self.driver
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add session cookies to browser
        chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Transfer session cookies to driver
            self._transfer_session_cookies()
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Dynamic content handler initialized")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def _transfer_session_cookies(self):
        """Transfer session cookies to WebDriver."""
        try:
            # Visit base URL first to set domain
            self.driver.get(self.session_manager.base_url)
            
            # Add all session cookies
            session = self.session_manager.get_session()
            for cookie in session.cookies:
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain or '.strunz.com',
                    'path': cookie.path or '/',
                    'secure': cookie.secure or False
                }
                
                try:
                    self.driver.add_cookie(cookie_dict)
                except Exception as e:
                    logger.debug(f"Could not add cookie {cookie.name}: {e}")
            
            logger.debug("Session cookies transferred to WebDriver")
            
        except Exception as e:
            logger.warning(f"Failed to transfer session cookies: {e}")
    
    def load_page_with_javascript(self, url: str, wait_for_selector: str = None) -> BeautifulSoup:
        """Load page with JavaScript execution and wait for content."""
        driver = self._setup_driver()
        
        try:
            logger.debug(f"Loading page with JavaScript: {url}")
            driver.get(url)
            
            # Wait for basic page structure
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for specific content if selector provided
            if wait_for_selector:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for selector: {wait_for_selector}")
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Execute any pending JavaScript
            driver.execute_script("return document.readyState") == "complete"
            
            # Get final page source
            html = driver.page_source
            return BeautifulSoup(html, 'html.parser')
            
        except Exception as e:
            logger.error(f"Failed to load page with JavaScript: {e}")
            raise
    
    def close(self):
        """Clean up WebDriver resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.debug("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")


class AdvancedForumScraper:
    """Advanced forum scraper with complete comment pagination and dynamic content handling."""
    
    # Forum categories with metadata
    FORUM_CATEGORIES = {
        'fitness': {'url_name': 'fitness', 'display_name': 'Fitness'},
        'gesundheit': {'url_name': 'gesundheit', 'display_name': 'Gesundheit'},
        'ernährung': {'url_name': 'ernaehrung', 'display_name': 'Ernährung'},
        'bluttuning': {'url_name': 'bluttuning', 'display_name': 'Bluttuning'},
        'mental': {'url_name': 'mental', 'display_name': 'Mental'},
        'infektion_prävention': {'url_name': 'infektion-und-praevention', 'display_name': 'Infektion & Prävention'}
    }
    
    def __init__(self, base_url: str = "https://www.strunz.com", delay: float = 2.0):
        """
        Initialize advanced forum scraper.
        
        Args:
            base_url: Base URL for strunz.com
            delay: Delay between requests for respectful scraping
        """
        self.base_url = base_url
        self.delay = delay
        
        # Initialize components
        self.session_manager = SessionManager(base_url)
        self.content_handler = DynamicContentHandler(self.session_manager)
        
        # Tracking
        self.scraped_threads: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Statistics
        self.stats = {
            'threads_discovered': 0,
            'threads_scraped': 0,
            'comments_extracted': 0,
            'pages_processed': 0,
            'errors_encountered': 0
        }
        
        logger.info("Advanced forum scraper initialized")
    
    def initialize(self) -> bool:
        """Initialize scraper with session setup."""
        logger.info("🔧 Initializing advanced forum scraper")
        
        if not self.session_manager.initialize_session():
            logger.error("Failed to initialize session")
            return False
        
        logger.info("✅ Scraper initialization complete")
        return True
    
    def discover_all_threads(self, category_key: str, max_pages: Optional[int] = None) -> List[str]:
        """
        Discover all forum threads in a category with enhanced detection.
        
        Args:
            category_key: Forum category to discover
            max_pages: Maximum pages to scan (None for unlimited)
            
        Returns:
            List of thread URLs
        """
        if category_key not in self.FORUM_CATEGORIES:
            logger.error(f"Unknown category: {category_key}")
            return []
        
        category_info = self.FORUM_CATEGORIES[category_key]
        base_url = f"{self.base_url}/forum/{category_info['url_name']}"
        
        logger.info(f"🔍 Discovering threads in {category_info['display_name']}")
        
        thread_urls = []
        page = 1
        consecutive_failures = 0
        
        while True:
            if max_pages and page > max_pages:
                break
            
            if consecutive_failures >= 3:
                logger.warning("Too many consecutive failures, stopping discovery")
                break
            
            # Construct page URL
            page_url = base_url if page == 1 else f"{base_url}?p={page}"
            
            logger.info(f"📄 Scanning page {page}: {page_url}")
            
            try:
                # Use dynamic content handler for better thread detection
                soup = self.content_handler.load_page_with_javascript(
                    page_url, 
                    wait_for_selector="a[href*='/forum/']"
                )
                
                page_threads = self._extract_thread_urls_from_page(soup, category_info['url_name'])
                
                if page_threads:
                    thread_urls.extend(page_threads)
                    consecutive_failures = 0
                    logger.info(f"✅ Found {len(page_threads)} threads on page {page}")
                else:
                    consecutive_failures += 1
                    logger.warning(f"❌ No threads found on page {page}")
                
                # Check for next page
                if not self._has_next_page(soup):
                    logger.info("No more pages available")
                    break
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error discovering threads on page {page}: {e}")
                consecutive_failures += 1
                self.stats['errors_encountered'] += 1
        
        unique_threads = list(set(thread_urls))  # Remove duplicates
        self.stats['threads_discovered'] = len(unique_threads)
        
        logger.info(f"🎯 Discovery complete: {len(unique_threads)} unique threads found")
        return unique_threads
    
    def _extract_thread_urls_from_page(self, soup: BeautifulSoup, category_url_name: str) -> List[str]:
        """Extract thread URLs from forum category page."""
        thread_urls = []
        
        # Enhanced selectors for thread detection
        thread_selectors = [
            f'a[href*="/forum/{category_url_name}/"]',
            f'a[href^="/forum/{category_url_name}/"]',
            'a[href*="/forum/"][href*="/t/"]',
            '.forum-thread a',
            '.thread-title a',
            '.topic-title a',
            'h3 a[href*="forum"]',
            '.post-title a[href*="forum"]'
        ]
        
        for selector in thread_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Build full URL
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = urljoin(self.base_url, href)
                    
                    # Validate thread URL
                    if self._is_valid_thread_url(full_url, category_url_name):
                        thread_urls.append(full_url)
        
        return thread_urls
    
    def _is_valid_thread_url(self, url: str, category_url_name: str) -> bool:
        """Validate if URL is a legitimate thread URL."""
        if not url or '?p=' in url or '&p=' in url:
            return False
        
        if f'/forum/{category_url_name}/' not in url:
            return False
        
        # Should not end with just category name
        if url.rstrip('/').endswith(f'/forum/{category_url_name}'):
            return False
        
        return True
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there's a next page available."""
        # Look for pagination indicators
        next_selectors = [
            'a[title*="next"]',
            'a[title*="weiter"]',
            'a.next',
            'a[href*="?p="]'
        ]
        
        for selector in next_selectors:
            if soup.select(selector):
                return True
        
        return False
    
    def scrape_complete_thread(self, thread_url: str) -> Optional[ForumThread]:
        """
        Scrape complete thread with all comments through pagination.
        
        Args:
            thread_url: URL of the forum thread
            
        Returns:
            ForumThread object with all comments or None if failed
        """
        if thread_url in self.scraped_threads:
            logger.debug(f"Thread already scraped: {thread_url}")
            return None
        
        logger.info(f"📖 Scraping complete thread: {thread_url}")
        
        try:
            # Load first page to get thread metadata
            soup = self.content_handler.load_page_with_javascript(
                thread_url,
                wait_for_selector=".post, .comment, article"
            )
            
            # Extract thread metadata
            thread_title = self._extract_thread_title(soup)
            thread_author = self._extract_thread_author(soup)
            total_pages = self._extract_total_pages(soup)
            
            logger.info(f"Thread: {thread_title[:50]}... ({total_pages} pages)")
            
            # Initialize thread object
            thread = ForumThread(
                url=thread_url,
                title=thread_title,
                category=self._extract_category_from_url(thread_url),
                author=thread_author,
                created_date=None,
                total_pages=total_pages,
                total_comments=0,
                comments=[],
                metadata={}
            )
            
            # Scrape all pages
            for page in range(1, total_pages + 1):
                page_url = thread_url if page == 1 else f"{thread_url}?p={page}"
                
                logger.info(f"📄 Scraping page {page}/{total_pages}")
                
                page_comments = self._scrape_comments_from_page(page_url, page)
                thread.comments.extend(page_comments)
                
                self.stats['pages_processed'] += 1
                time.sleep(self.delay)  # Respectful delay
            
            thread.total_comments = len(thread.comments)
            self.stats['comments_extracted'] += len(thread.comments)
            self.stats['threads_scraped'] += 1
            
            self.scraped_threads.add(thread_url)
            
            logger.info(f"✅ Thread complete: {thread.total_comments} comments extracted")
            return thread
            
        except Exception as e:
            logger.error(f"Failed to scrape thread {thread_url}: {e}")
            self.failed_urls.add(thread_url)
            self.stats['errors_encountered'] += 1
            return None
    
    def _extract_thread_title(self, soup: BeautifulSoup) -> str:
        """Extract thread title from page."""
        title_selectors = ['h1', 'h2', '.thread-title', '.post-title', '.page-title', 'title']
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    return self._clean_text(title)
        
        return "Untitled Thread"
    
    def _extract_thread_author(self, soup: BeautifulSoup) -> str:
        """Extract thread author from first post."""
        author_selectors = ['.author', '.username', '.user', '.poster', '.post-author']
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                if author:
                    return self._clean_text(author)
        
        return "Unknown Author"
    
    def _extract_total_pages(self, soup: BeautifulSoup) -> int:
        """Extract total number of pages from pagination."""
        # Look for pagination indicators
        pagination_selectors = [
            '.pagination',
            '.pager',
            '.page-numbers',
            '[class*="pagination"]'
        ]
        
        for selector in pagination_selectors:
            pagination_elem = soup.select_one(selector)
            if pagination_elem:
                # Find highest page number
                page_links = pagination_elem.select('a[href*="?p="]')
                max_page = 1
                
                for link in page_links:
                    href = link.get('href', '')
                    match = re.search(r'[?&]p=(\d+)', href)
                    if match:
                        page_num = int(match.group(1))
                        max_page = max(max_page, page_num)
                
                return max_page
        
        return 1  # Default to single page
    
    def _extract_category_from_url(self, url: str) -> str:
        """Extract category from thread URL."""
        for category_key, category_info in self.FORUM_CATEGORIES.items():
            if f"/forum/{category_info['url_name']}/" in url:
                return category_key
        return "unknown"
    
    def _scrape_comments_from_page(self, page_url: str, page_number: int) -> List[ForumComment]:
        """Scrape all comments from a single page."""
        try:
            soup = self.content_handler.load_page_with_javascript(
                page_url,
                wait_for_selector=".post, .comment, article"
            )
            
            comments = []
            
            # Enhanced comment selectors
            comment_selectors = [
                '.post',
                '.forum-post',
                'article',
                '.message',
                '.comment',
                '.reply',
                '[class*="post"]',
                '[class*="comment"]'
            ]
            
            comment_elements = []
            for selector in comment_selectors:
                elements = soup.select(selector)
                if elements:
                    comment_elements = elements
                    break
            
            for i, comment_elem in enumerate(comment_elements):
                comment = self._extract_single_comment(comment_elem, page_url, page_number, i + 1)
                if comment and comment.content:
                    comments.append(comment)
            
            logger.debug(f"Extracted {len(comments)} comments from page {page_number}")
            return comments
            
        except Exception as e:
            logger.error(f"Failed to scrape comments from page {page_url}: {e}")
            return []
    
    def _extract_single_comment(self, comment_elem, page_url: str, page_number: int, comment_index: int) -> Optional[ForumComment]:
        """Extract data from a single comment element."""
        try:
            # Extract content
            content_selectors = ['.post-content', '.message', '.post-text', '.content', '.post-body']
            content = ""
            
            for selector in content_selectors:
                content_elem = comment_elem.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .signature, .quote'):
                        unwanted.decompose()
                    
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            if not content:
                content = comment_elem.get_text(separator='\n', strip=True)
            
            content = self._clean_text(content)
            
            if not content or len(content) < 10:  # Skip very short content
                return None
            
            # Extract author
            author = ""
            author_selectors = ['.author', '.username', '.user', '.poster', '.post-author']
            for selector in author_selectors:
                author_elem = comment_elem.select_one(selector)
                if author_elem:
                    author = self._clean_text(author_elem.get_text(strip=True))
                    break
            
            # Extract author ID if available
            author_id = None
            author_link = comment_elem.select_one('a[href*="/user/view/uid/"]')
            if author_link:
                href = author_link.get('href', '')
                match = re.search(r'/uid/(\d+)', href)
                if match:
                    author_id = match.group(1)
            
            # Extract timestamp
            timestamp = None
            date_selectors = ['.post-date', '.timestamp', 'time', '.date']
            for selector in date_selectors:
                date_elem = comment_elem.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    timestamp = self._parse_german_date(date_text)
                    if timestamp:
                        break
            
            # Extract like count if available
            like_count = 0
            like_elem = comment_elem.select_one('[class*="like"], [class*="vote"]')
            if like_elem:
                like_text = like_elem.get_text(strip=True)
                numbers = re.findall(r'\d+', like_text)
                if numbers:
                    like_count = int(numbers[0])
            
            # Generate unique comment ID
            comment_id = f"{page_number}_{comment_index}_{hash(content[:50])}"
            
            return ForumComment(
                id=comment_id,
                content=content,
                author=author,
                author_id=author_id,
                timestamp=timestamp,
                post_number=comment_index,
                thread_url=page_url,
                page_number=page_number,
                like_count=like_count,
                reply_to=None,  # Could be enhanced to detect reply relationships
                user_metadata=None
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract comment {comment_index}: {e}")
            return None
    
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
            r'Zitieren',
            r'Antworten',
            r'Gefällt mir',
            r'Teilen'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _parse_german_date(self, date_text: str) -> Optional[datetime]:
        """Parse German date formats."""
        if not date_text:
            return None
        
        # Common German date patterns
        patterns = [
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
        
        for pattern in patterns:
            match = re.search(pattern, date_text.lower())
            if match:
                try:
                    if '.' in date_text:
                        day, month, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                    elif '-' in date_text:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day))
                    else:
                        day, month_name, year = match.groups()
                        month = months_de.get(month_name.lower())
                        if month:
                            return datetime(int(year), month, int(day))
                except ValueError:
                    continue
        
        return None
    
    def scrape_category_complete(self, category_key: str, max_threads: Optional[int] = None) -> List[ForumThread]:
        """
        Scrape complete forum category with all threads and comments.
        
        Args:
            category_key: Forum category to scrape
            max_threads: Maximum threads to scrape (None for unlimited)
            
        Returns:
            List of complete ForumThread objects
        """
        logger.info(f"🚀 Starting complete category scraping: {category_key}")
        
        if not self.initialize():
            logger.error("Failed to initialize scraper")
            return []
        
        # Discover all threads
        thread_urls = self.discover_all_threads(category_key)
        
        if not thread_urls:
            logger.warning(f"No threads discovered in {category_key}")
            return []
        
        if max_threads:
            thread_urls = thread_urls[:max_threads]
            logger.info(f"Limited to {max_threads} threads")
        
        # Scrape all threads
        scraped_threads = []
        
        for i, thread_url in enumerate(thread_urls, 1):
            logger.info(f"🔄 Scraping thread {i}/{len(thread_urls)}")
            
            thread = self.scrape_complete_thread(thread_url)
            if thread:
                scraped_threads.append(thread)
                logger.info(f"✅ Thread {i} complete: {thread.total_comments} comments")
            else:
                logger.warning(f"❌ Thread {i} failed")
            
            # Respectful delay between threads
            time.sleep(self.delay)
        
        logger.info(f"🎯 Category scraping complete: {len(scraped_threads)} threads with {sum(t.total_comments for t in scraped_threads)} total comments")
        
        return scraped_threads
    
    def get_statistics(self) -> Dict:
        """Get comprehensive scraping statistics."""
        return {
            **self.stats,
            'scraped_threads': len(self.scraped_threads),
            'failed_urls': len(self.failed_urls),
            'success_rate': (self.stats['threads_scraped'] / max(self.stats['threads_discovered'], 1)) * 100
        }
    
    def close(self):
        """Clean up all resources."""
        self.content_handler.close()
        logger.info("Advanced forum scraper closed")