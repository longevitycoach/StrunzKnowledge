#!/usr/bin/env python3
"""
Optimized Forum Scraper - Production Ready
==========================================

Simplified forum scraper using the discovered ?limit=50 parameter to efficiently
extract all comments without JavaScript or complex pagination handling.

Status: PRODUCTION
Usage: Efficient forum scraping using direct URL parameters
Dependencies: requests, beautifulsoup4

Author: Matthias Buchhorn
Project: StrunzKnowledgeMCP
Last Updated: 2025-07-11
Features:
- Direct comment extraction using ?limit=50 parameter with &p=X pagination
- Minimal session handling for consistency
- Efficient pagination handling with &p=2, &p=3, etc.
- Complete comment extraction with automatic pagination detection
- Respectful rate limiting
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class OptimizedForumComment:
    """Represents a forum comment with essential data."""
    content: str
    author: str
    timestamp: Optional[str]
    post_number: int
    thread_url: str
    thread_title: str
    category: str


@dataclass
class OptimizedForumThread:
    """Represents a complete forum thread."""
    url: str
    title: str
    category: str
    total_comments: int
    comments: List[OptimizedForumComment]
    scraped_at: str


class OptimizedForumScraper:
    """Optimized forum scraper using direct URL parameters."""
    
    # Forum categories with correct URL mappings
    FORUM_CATEGORIES = {
        'fitness': 'fitness',
        'gesundheit': 'gesundheit', 
        'ernährung': 'ernaehrung',
        'bluttuning': 'bluttuning',
        'mental': 'mental',
        'infektion_prävention': 'infektion-und-praevention'
    }
    
    def __init__(self, 
                 base_url: str = "https://www.strunz.com",
                 delay: float = 1.5,
                 comment_limit: int = 50):
        """
        Initialize optimized forum scraper.
        
        Args:
            base_url: Base URL for strunz.com
            delay: Delay between requests (respectful scraping)
            comment_limit: Comment limit parameter (default 50, max allowed by server)
        """
        self.base_url = base_url
        self.delay = delay
        self.comment_limit = comment_limit
        
        # Setup session with minimal but effective headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1'
        })
        
        # Initialize session with main page visit (minimal session establishment)
        self._initialize_session()
        
        # Tracking
        self.scraped_threads: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Statistics
        self.stats = {
            'threads_discovered': 0,
            'threads_scraped': 0,
            'comments_extracted': 0,
            'total_requests': 0,
            'errors_encountered': 0
        }
        
        logger.info(f"Optimized forum scraper initialized with comment limit: {comment_limit}")
    
    def _initialize_session(self):
        """Initialize session with a simple main page visit."""
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            logger.debug("Session initialized with main page visit")
        except Exception as e:
            logger.warning(f"Session initialization failed (continuing anyway): {e}")
    
    def discover_threads_in_category(self, category_key: str, max_pages: Optional[int] = None) -> List[str]:
        """
        Discover thread URLs in a forum category.
        
        Args:
            category_key: Forum category key
            max_pages: Maximum pages to scan (None for unlimited)
            
        Returns:
            List of thread URLs
        """
        if category_key not in self.FORUM_CATEGORIES:
            logger.error(f"Unknown category: {category_key}")
            return []
        
        category_url_name = self.FORUM_CATEGORIES[category_key]
        base_category_url = f"{self.base_url}/forum/{category_url_name}"
        
        logger.info(f"🔍 Discovering threads in {category_key} ({category_url_name})")
        
        thread_urls = []
        page = 1
        consecutive_empty_pages = 0
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break
            
            if consecutive_empty_pages >= 3:
                logger.info("No new threads found in last 3 pages, stopping")
                break
            
            # Construct page URL
            page_url = base_category_url if page == 1 else f"{base_category_url}?p={page}"
            
            logger.info(f"📄 Scanning page {page}: {page_url}")
            
            try:
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()
                self.stats['total_requests'] += 1
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_threads = self._extract_thread_urls_from_page(soup, category_url_name)
                
                if page_threads:
                    thread_urls.extend(page_threads)
                    consecutive_empty_pages = 0
                    logger.info(f"✅ Found {len(page_threads)} threads on page {page}")
                else:
                    consecutive_empty_pages += 1
                    logger.warning(f"❌ No threads found on page {page}")
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scanning page {page}: {e}")
                self.stats['errors_encountered'] += 1
                consecutive_empty_pages += 1
        
        # Remove duplicates and clean URLs
        unique_threads = list(set(thread_urls))
        self.stats['threads_discovered'] = len(unique_threads)
        
        logger.info(f"🎯 Discovery complete: {len(unique_threads)} unique threads found")
        return unique_threads
    
    def _extract_thread_urls_from_page(self, soup: BeautifulSoup, category_url_name: str) -> List[str]:
        """Extract thread URLs from category page HTML."""
        thread_urls = []
        
        # Look for links that match forum thread patterns
        link_selectors = [
            f'a[href*="/forum/{category_url_name}/"]',
            'a[href*="/forum/"]'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and self._is_valid_thread_url(href, category_url_name):
                    # Build full URL
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    else:
                        full_url = urljoin(self.base_url, href)
                    
                    thread_urls.append(full_url)
        
        return thread_urls
    
    def _is_valid_thread_url(self, href: str, category_url_name: str) -> bool:
        """Validate if href is a legitimate thread URL."""
        if not href:
            return False
        
        # Must contain the category
        if f'/forum/{category_url_name}/' not in href:
            return False
        
        # Exclude pagination and category base URLs
        if '?p=' in href or '&p=' in href:
            return False
        
        # Must not end with just the category name
        if href.rstrip('/').endswith(f'/forum/{category_url_name}'):
            return False
        
        # Should have additional path components (thread identifier)
        path_parts = href.split('/')
        if len(path_parts) < 5:  # /forum/{category}/{thread-name}
            return False
        
        return True
    
    def scrape_thread_with_all_comments(self, thread_url: str) -> Optional[OptimizedForumThread]:
        """
        Scrape complete thread using ?limit=50 and &p=X for pagination.
        
        Args:
            thread_url: URL of forum thread
            
        Returns:
            OptimizedForumThread with all comments or None if failed
        """
        if thread_url in self.scraped_threads:
            logger.debug(f"Thread already scraped: {thread_url}")
            return None
        
        logger.info(f"📖 Scraping thread with all comments: {thread_url}")
        
        # Start with first page
        separator = '&' if '?' in thread_url else '?'
        first_page_url = f"{thread_url}{separator}limit={self.comment_limit}"
        
        all_comments = []
        thread_title = ""
        category = ""
        page = 1
        
        try:
            while True:
                # Construct page URL
                if page == 1:
                    current_url = first_page_url
                else:
                    current_url = f"{first_page_url}&p={page}"
                
                logger.debug(f"📄 Scraping page {page}: {current_url}")
                
                response = self.session.get(current_url, timeout=30)
                response.raise_for_status()
                self.stats['total_requests'] += 1
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract metadata from first page
                if page == 1:
                    thread_title = self._extract_thread_title(soup)
                    category = self._extract_category_from_url(thread_url)
                
                # Extract comments from current page
                page_comments = self._extract_all_comments(soup, thread_url, thread_title, category, page)
                
                if page_comments:
                    all_comments.extend(page_comments)
                    logger.debug(f"✅ Page {page}: {len(page_comments)} comments")
                    
                    # Check if we should continue to next page
                    if len(page_comments) < self.comment_limit:
                        # Less than limit means this is the last page
                        logger.debug(f"Last page reached (only {len(page_comments)} comments)")
                        break
                    
                    # Check for next page indicators
                    if not self._has_next_page(soup, page):
                        logger.debug("No next page indicator found")
                        break
                    
                    page += 1
                    time.sleep(self.delay * 0.5)  # Shorter delay between pages
                else:
                    logger.debug(f"No comments found on page {page}")
                    break
            
            if all_comments:
                thread = OptimizedForumThread(
                    url=thread_url,
                    title=thread_title,
                    category=category,
                    total_comments=len(all_comments),
                    comments=all_comments,
                    scraped_at=datetime.now().isoformat()
                )
                
                self.scraped_threads.add(thread_url)
                self.stats['threads_scraped'] += 1
                self.stats['comments_extracted'] += len(all_comments)
                
                logger.info(f"✅ Thread scraped: {thread_title[:50]}... ({len(all_comments)} comments from {page} pages)")
                return thread
            else:
                logger.warning(f"No comments found in thread: {thread_url}")
                self.failed_urls.add(thread_url)
                return None
                
        except Exception as e:
            logger.error(f"Failed to scrape thread {thread_url}: {e}")
            self.failed_urls.add(thread_url)
            self.stats['errors_encountered'] += 1
            return None
    
    def _extract_thread_title(self, soup: BeautifulSoup) -> str:
        """Extract thread title from page."""
        title_selectors = [
            'h1',
            'h2', 
            '.thread-title',
            '.post-title',
            '.page-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3 and 'strunz' not in title.lower():
                    return self._clean_text(title)
        
        return "Untitled Thread"
    
    def _extract_category_from_url(self, url: str) -> str:
        """Extract category from thread URL."""
        for category_key, category_url_name in self.FORUM_CATEGORIES.items():
            if f'/forum/{category_url_name}/' in url:
                return category_key
        return "unknown"
    
    def _has_next_page(self, soup: BeautifulSoup, current_page: int) -> bool:
        """Check if there's a next page available for pagination."""
        # Strategy 1: Look for pagination links
        next_page_selectors = [
            f'a[href*="&p={current_page + 1}"]',
            f'a[href*="?p={current_page + 1}"]', 
            'a[href*="p="][title*="next"]',
            'a[href*="p="][title*="weiter"]',
            '.pagination a[href*="p="]',
            '.pager a[href*="p="]'
        ]
        
        for selector in next_page_selectors:
            if soup.select(selector):
                logger.debug(f"Next page found via selector: {selector}")
                return True
        
        # Strategy 2: Look for page numbers higher than current
        all_page_links = soup.select('a[href*="p="]')
        for link in all_page_links:
            href = link.get('href', '')
            # Extract page number from URL
            page_match = re.search(r'[?&]p=(\d+)', href)
            if page_match:
                page_num = int(page_match.group(1))
                if page_num > current_page:
                    logger.debug(f"Found higher page number: {page_num}")
                    return True
        
        # Strategy 3: Check for "Load more" or similar buttons
        load_more_selectors = [
            '[class*="load-more"]',
            '[class*="show-more"]', 
            '[data-action="load-more"]',
            'button[onclick*="page"]'
        ]
        
        for selector in load_more_selectors:
            if soup.select(selector):
                logger.debug(f"Load more button found: {selector}")
                return True
        
        logger.debug("No next page indicators found")
        return False

    def _extract_all_comments(self, soup: BeautifulSoup, thread_url: str, thread_title: str, category: str, page_number: int = 1) -> List[OptimizedForumComment]:
        """Extract all comments from thread page (with limit parameter)."""
        comments = []
        
        # Enhanced comment selectors for forum structure
        comment_selectors = [
            '.post',
            '.forum-post', 
            'article',
            '.message',
            '.comment',
            '.reply',
            '[class*="post-"]',
            '[class*="comment-"]',
            '.content .post'
        ]
        
        comment_elements = []
        for selector in comment_selectors:
            elements = soup.select(selector)
            if elements:
                comment_elements = elements
                logger.debug(f"Found {len(elements)} comment elements with selector: {selector}")
                break
        
        if not comment_elements:
            # Fallback: look for any structured content
            comment_elements = soup.select('div[class], section[class], article')
            logger.debug(f"Fallback: found {len(comment_elements)} potential content elements")
        
        for i, comment_elem in enumerate(comment_elements):
            try:
                comment = self._extract_single_comment(
                    comment_elem, 
                    thread_url, 
                    thread_title, 
                    category, 
                    i + 1
                )
                
                if comment and comment.content:
                    comments.append(comment)
                    
            except Exception as e:
                logger.debug(f"Failed to extract comment {i + 1}: {e}")
                continue
        
        logger.info(f"Extracted {len(comments)} comments from thread")
        return comments
    
    def _extract_single_comment(self, comment_elem, thread_url: str, thread_title: str, category: str, post_number: int) -> Optional[OptimizedForumComment]:
        """Extract individual comment data."""
        try:
            # Extract content using multiple strategies
            content = ""
            
            # Strategy 1: Look for specific content containers
            content_selectors = [
                '.post-content',
                '.message',
                '.post-text', 
                '.content',
                '.post-body',
                '.comment-content'
            ]
            
            for selector in content_selectors:
                content_elem = comment_elem.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.select('script, style, .signature, .quote, .avatar'):
                        unwanted.decompose()
                    
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Strategy 2: Fallback to entire element content
            if not content:
                # Remove unwanted elements from entire comment
                for unwanted in comment_elem.select('script, style, .signature, .quote, .avatar, .meta'):
                    unwanted.decompose()
                
                content = comment_elem.get_text(separator='\n', strip=True)
            
            content = self._clean_text(content)
            
            # Skip if content is too short or contains only navigation text
            if not content or len(content) < 20:
                return None
            
            if self._is_navigation_content(content):
                return None
            
            # Extract author
            author = "Unknown Author"
            author_selectors = [
                '.author',
                '.username', 
                '.user',
                '.poster',
                '.post-author',
                '.by-author'
            ]
            
            for selector in author_selectors:
                author_elem = comment_elem.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text(strip=True)
                    if author_text and len(author_text) < 50:  # Reasonable author name length
                        author = self._clean_text(author_text)
                        break
            
            # Extract timestamp
            timestamp = None
            date_selectors = [
                '.post-date',
                '.timestamp',
                'time',
                '.date',
                '[class*="date"]',
                '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = comment_elem.select_one(selector)
                if date_elem:
                    # Try datetime attribute first
                    datetime_attr = date_elem.get('datetime')
                    if datetime_attr:
                        timestamp = datetime_attr
                        break
                    
                    # Fallback to text content
                    date_text = date_elem.get_text(strip=True)
                    if date_text and len(date_text) < 30:  # Reasonable date length
                        timestamp = date_text
                        break
            
            return OptimizedForumComment(
                content=content,
                author=author,
                timestamp=timestamp,
                post_number=post_number,
                thread_url=thread_url,
                thread_title=thread_title,
                category=category
            )
            
        except Exception as e:
            logger.debug(f"Failed to extract comment data: {e}")
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
            r'Teilen',
            r'Navigation',
            r'Menü',
            r'Startseite'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _is_navigation_content(self, content: str) -> bool:
        """Check if content is navigation/UI text rather than forum content."""
        navigation_indicators = [
            'anmelden',
            'registrieren', 
            'passwort vergessen',
            'navigation',
            'menü',
            'startseite',
            'impressum',
            'datenschutz',
            'cookie',
            'newsletter'
        ]
        
        content_lower = content.lower()
        navigation_count = sum(1 for indicator in navigation_indicators if indicator in content_lower)
        
        # If more than 2 navigation indicators and short content, likely navigation
        return navigation_count >= 2 and len(content) < 100
    
    def scrape_category_optimized(self, category_key: str, max_threads: Optional[int] = None) -> List[OptimizedForumThread]:
        """
        Scrape complete forum category using optimized approach.
        
        Args:
            category_key: Forum category to scrape
            max_threads: Maximum threads to scrape (None for unlimited)
            
        Returns:
            List of OptimizedForumThread objects
        """
        logger.info(f"🚀 Starting optimized category scraping: {category_key}")
        
        # Discover threads
        thread_urls = self.discover_threads_in_category(category_key)
        
        if not thread_urls:
            logger.warning(f"No threads discovered in {category_key}")
            return []
        
        if max_threads:
            thread_urls = thread_urls[:max_threads]
            logger.info(f"Limited to {max_threads} threads")
        
        # Scrape all threads efficiently
        scraped_threads = []
        
        for i, thread_url in enumerate(thread_urls, 1):
            logger.info(f"🔄 Scraping thread {i}/{len(thread_urls)}")
            
            thread = self.scrape_thread_with_all_comments(thread_url)
            if thread:
                scraped_threads.append(thread)
                logger.info(f"✅ Thread {i}: {thread.total_comments} comments")
            else:
                logger.warning(f"❌ Thread {i} failed")
            
            # Respectful delay
            time.sleep(self.delay)
        
        total_comments = sum(t.total_comments for t in scraped_threads)
        logger.info(f"🎯 Category scraping complete: {len(scraped_threads)} threads, {total_comments} comments")
        
        return scraped_threads
    
    def save_scraped_data(self, threads: List[OptimizedForumThread], category: str) -> Dict[str, str]:
        """Save scraped forum data to files."""
        if not threads:
            logger.warning("No threads to save")
            return {}
        
        # Create output directory
        output_dir = Path("data/scraped/optimized_forum")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to serializable format
        threads_data = []
        for thread in threads:
            thread_dict = asdict(thread)
            # Convert comments to dicts
            thread_dict['comments'] = [asdict(comment) for comment in thread.comments]
            threads_data.append(thread_dict)
        
        # Save JSON data
        json_file = output_dir / f"{category}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(threads_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Save summary
        summary = {
            'category': category,
            'timestamp': timestamp,
            'total_threads': len(threads),
            'total_comments': sum(t.total_comments for t in threads),
            'scraping_stats': self.get_statistics(),
            'threads_summary': [
                {
                    'title': t.title[:50],
                    'url': t.url,
                    'comments': t.total_comments
                } 
                for t in threads[:10]  # First 10 threads
            ]
        }
        
        summary_file = output_dir / f"{category}_{timestamp}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Data saved:")
        logger.info(f"   JSON: {json_file}")
        logger.info(f"   Summary: {summary_file}")
        
        return {
            'json_file': str(json_file),
            'summary_file': str(summary_file)
        }
    
    def get_statistics(self) -> Dict:
        """Get comprehensive scraping statistics."""
        return {
            **self.stats,
            'scraped_threads_count': len(self.scraped_threads),
            'failed_urls_count': len(self.failed_urls),
            'success_rate': (self.stats['threads_scraped'] / max(self.stats['threads_discovered'], 1)) * 100,
            'avg_comments_per_thread': self.stats['comments_extracted'] / max(self.stats['threads_scraped'], 1),
            'requests_per_thread': self.stats['total_requests'] / max(self.stats['threads_scraped'], 1)
        }
    
    def close(self):
        """Clean up session."""
        if self.session:
            self.session.close()
            logger.debug("Session closed")