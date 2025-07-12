import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContentQuality:
    """Content quality scoring metrics."""
    score: float
    word_count: int
    char_count: int
    has_links: bool
    has_structure: bool
    is_meaningful: bool
    language_quality: float


class ImprovedStrunzScraper:
    """Enhanced scraper with JavaScript support and content quality filtering."""
    
    def __init__(self, base_url: str = "https://www.strunz.com", delay: float = 1.0, use_selenium: bool = True):
        self.base_url = base_url
        self.delay = delay
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.driver = None
        
        # Content quality thresholds
        self.min_content_score = 0.6
        self.min_word_count = 50
        self.min_char_count = 200
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with optimal settings."""
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
        chrome_options.add_argument('--disable-javascript-harmony-shipping')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        return self.driver
    
    def _close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
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
    
    def _get_page_content(self, url: str, wait_for_selector: str = None) -> Optional[BeautifulSoup]:
        """Get page content using Selenium or requests."""
        if self.use_selenium:
            try:
                driver = self._setup_driver()
                driver.get(url)
                
                if wait_for_selector:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                    )
                else:
                    time.sleep(3)  # Wait for general page load
                
                html = driver.page_source
                return BeautifulSoup(html, 'lxml')
            except Exception as e:
                logger.error(f"Selenium failed for {url}: {e}")
                # Fallback to requests
                response = self._make_request(url)
                if response:
                    return BeautifulSoup(response.content, 'lxml')
        else:
            response = self._make_request(url)
            if response:
                return BeautifulSoup(response.content, 'lxml')
        
        return None
    
    def _assess_content_quality(self, content: str, title: str = "") -> ContentQuality:
        """Assess the quality of scraped content."""
        if not content:
            return ContentQuality(0.0, 0, 0, False, False, False, 0.0)
        
        # Basic metrics
        word_count = len(content.split())
        char_count = len(content)
        
        # Structure indicators
        has_links = 'http' in content or 'www.' in content
        has_structure = any(indicator in content.lower() for indicator in [
            'absatz', 'kapitel', 'punkt', 'erstens', 'zweitens', 'außerdem', 
            'darüber hinaus', 'zusammenfassung', 'fazit'
        ])
        
        # Content meaningfulness (health/nutrition focused)
        meaningful_indicators = [
            'gesundheit', 'ernährung', 'fitness', 'vitamin', 'mineral', 'protein',
            'training', 'körper', 'bewegung', 'prävention', 'therapie', 'studien',
            'forschung', 'wissenschaft', 'medizin', 'arzt', 'patient', 'behandlung',
            'omega', 'fettsäuren', 'entzündung', 'immunsystem', 'blut', 'stoffwechsel',
            'hormone', 'zellen', 'mitochondrien', 'antioxidantien', 'aminosäure',
            'krankheit', 'heilung', 'regeneration', 'leistung', 'energie', 'muskeln',
            'knochen', 'gelenke', 'herz', 'kreislauf', 'diabetes', 'blutdruck'
        ]
        
        meaningful_count = sum(1 for indicator in meaningful_indicators 
                             if indicator in content.lower())
        is_meaningful = meaningful_count >= 2  # Lowered threshold
        
        # Language quality (German-specific)
        german_indicators = ['der', 'die', 'das', 'und', 'oder', 'aber', 'mit', 'für', 'von', 'zu']
        german_score = sum(1 for indicator in german_indicators 
                          if f' {indicator} ' in content.lower()) / len(german_indicators)
        
        # Calculate overall score
        score = 0.0
        
        # Word count score (0-0.25)
        if word_count >= 150:
            score += 0.25
        elif word_count >= 80:
            score += 0.20
        elif word_count >= 40:
            score += 0.15
        elif word_count >= 20:
            score += 0.10
        
        # Character count score (0-0.15)
        if char_count >= 800:
            score += 0.15
        elif char_count >= 400:
            score += 0.10
        elif char_count >= 200:
            score += 0.05
        
        # Structure score (0-0.15)
        if has_structure:
            score += 0.15
        elif has_links:
            score += 0.10
        
        # Meaningfulness score (0-0.35) - increased weight for health content
        if meaningful_count >= 5:
            score += 0.35
        elif meaningful_count >= 3:
            score += 0.25
        elif meaningful_count >= 2:
            score += 0.20
        elif meaningful_count >= 1:
            score += 0.10
        
        # Language quality score (0-0.10)
        score += german_score * 0.10
        
        return ContentQuality(
            score=min(score, 1.0),
            word_count=word_count,
            char_count=char_count,
            has_links=has_links,
            has_structure=has_structure,
            is_meaningful=is_meaningful,
            language_quality=german_score
        )
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
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
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Fix common encoding issues
        content = content.replace('ä', 'ä').replace('ö', 'ö').replace('ü', 'ü')
        content = content.replace('Ä', 'Ä').replace('Ö', 'Ö').replace('Ü', 'Ü')
        content = content.replace('ß', 'ß')
        
        # Remove excessive line breaks
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse German date formats with improved accuracy."""
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
                    pass
        return None
    
    def scrape_news(self) -> List[Dict]:
        """Scrape news articles with improved extraction."""
        news_url = f"{self.base_url}/news.html"
        articles = []
        visited_urls = set()
        
        logger.info(f"Starting news scraping from: {news_url}")
        
        soup = self._get_page_content(news_url)
        if not soup:
            logger.error("Failed to load news page")
            return articles
        
        # Find article links using improved selectors
        article_links = []
        link_selectors = [
            'a[href*="/news/"]',
            'a[href$=".html"]',
            '.news-item a',
            '.article-link',
            'h1 a', 'h2 a', 'h3 a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and '/news/' in href and href.endswith('.html'):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in article_links:
                        article_links.append(full_url)
        
        logger.info(f"Found {len(article_links)} article links")
        
        # Scrape each article
        for i, article_url in enumerate(article_links, 1):
            if article_url in visited_urls:
                continue
                
            logger.info(f"Scraping article {i}/{len(article_links)}: {article_url}")
            visited_urls.add(article_url)
            
            article_soup = self._get_page_content(article_url)
            if not article_soup:
                continue
            
            article = self._extract_enhanced_article(article_soup, article_url)
            if article:
                quality = self._assess_content_quality(article['content'], article['title'])
                article['quality_score'] = quality.score
                article['word_count'] = quality.word_count
                
                if quality.score >= self.min_content_score:
                    articles.append(article)
                    logger.info(f"Added article: {article['title'][:50]}... (quality: {quality.score:.2f})")
                else:
                    logger.debug(f"Filtered low-quality article: {article['title'][:50]}... (quality: {quality.score:.2f})")
        
        logger.info(f"Scraped {len(articles)} high-quality news articles")
        return articles
    
    def scrape_forum(self, category: str) -> List[Dict]:
        """Scrape forum posts with Selenium for JavaScript content."""
        forum_url = f"{self.base_url}/forum/{category}/"
        posts = []
        
        logger.info(f"Starting forum scraping for category: {category}")
        
        soup = self._get_page_content(forum_url, wait_for_selector="a[href*='/forum/']")
        if not soup:
            logger.error(f"Failed to load forum page: {forum_url}")
            return posts
        
        # Find thread links using improved patterns
        thread_links = []
        thread_selectors = [
            f'a[href*="/forum/{category}/"]',
            f'a[href^="/forum/{category}/"]',
            'a[href*="/forum/"][href*="/t/"]',  # Traditional forum pattern
            '.forum-thread a',
            '.thread-title a',
            'h3 a[href*="forum"]'
        ]
        
        for selector in thread_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and f'/forum/{category}/' in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in thread_links and full_url != forum_url:
                        thread_links.append(full_url)
        
        logger.info(f"Found {len(thread_links)} thread links for {category}")
        
        # Scrape each thread
        for i, thread_url in enumerate(thread_links, 1):
            logger.info(f"Scraping thread {i}/{len(thread_links)}: {thread_url}")
            
            thread_soup = self._get_page_content(thread_url, wait_for_selector=".post, .forum-post, article")
            if not thread_soup:
                continue
            
            thread_posts = self._extract_forum_posts(thread_soup, thread_url, category)
            for post in thread_posts:
                quality = self._assess_content_quality(post['content'], post.get('title', ''))
                post['quality_score'] = quality.score
                post['word_count'] = quality.word_count
                
                if quality.score >= self.min_content_score:
                    posts.append(post)
                    logger.info(f"Added forum post: {post.get('title', 'Untitled')[:50]}... (quality: {quality.score:.2f})")
        
        logger.info(f"Scraped {len(posts)} high-quality forum posts from {category}")
        return posts
    
    def _extract_enhanced_article(self, soup: BeautifulSoup, source_url: str) -> Optional[Dict]:
        """Extract article data with enhanced content extraction."""
        article = {
            'title': '',
            'content': '',
            'date': None,
            'author': '',
            'source_url': source_url,
            'type': 'news_article',
            'category': 'news'
        }
        
        # Extract title with multiple strategies
        title_selectors = [
            'h1',
            'title',
            '.article-title',
            '.news-title',
            '.post-title',
            'h2.title',
            '.headline h1',
            '.content h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    article['title'] = self._clean_content(title)
                    break
        
        # Extract content with priority-based selection
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
                for unwanted in content_elem.select('script, style, .ads, .advertisement, .social-share'):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                content = self._clean_content(content)
                
                if len(content) > len(best_content):
                    best_content = content
        
        article['content'] = best_content
        
        # Extract author
        author_selectors = [
            '.author',
            '.post-author',
            '.by-author',
            'span[class*="author"]',
            '.meta .author'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                if author:
                    article['author'] = self._clean_content(author)
                    break
        
        # Extract date
        date_selectors = [
            '.date',
            '.post-date',
            '.publication-date',
            'time',
            '.timestamp',
            '.meta .date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                if not date_text and date_elem.get('datetime'):
                    date_text = date_elem.get('datetime')
                
                if date_text:
                    article['date'] = self._parse_date(date_text)
                    if article['date']:
                        break
        
        return article if article['content'] and article['title'] else None
    
    def _extract_forum_posts(self, soup: BeautifulSoup, source_url: str, category: str) -> List[Dict]:
        """Extract forum posts with enhanced content extraction."""
        posts = []
        
        # Find post containers
        post_selectors = [
            '.post',
            '.forum-post',
            'article',
            '.message',
            '.comment',
            '.reply'
        ]
        
        post_elements = []
        for selector in post_selectors:
            elements = soup.select(selector)
            if elements:
                post_elements = elements
                break
        
        for i, post_elem in enumerate(post_elements):
            post = {
                'title': '',
                'content': '',
                'date': None,
                'author': '',
                'source_url': source_url,
                'type': 'forum_post',
                'category': f'forum_{category}',
                'post_number': i + 1
            }
            
            # Extract title (often the thread title for first post)
            if i == 0:  # First post often has the thread title
                title_selectors = ['h1', 'h2', '.thread-title', '.post-title']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        post['title'] = self._clean_content(title_elem.get_text(strip=True))
                        break
            
            # Extract author
            author_selectors = ['.author', '.username', '.user', '.poster', '.post-author']
            for selector in author_selectors:
                author_elem = post_elem.select_one(selector)
                if author_elem:
                    post['author'] = self._clean_content(author_elem.get_text(strip=True))
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
                    post['content'] = self._clean_content(content)
                    break
            
            # Extract date
            date_selectors = ['.post-date', '.timestamp', 'time', '.date', '.posted-on']
            for selector in date_selectors:
                date_elem = post_elem.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if not date_text and date_elem.get('datetime'):
                        date_text = date_elem.get('datetime')
                    
                    if date_text:
                        post['date'] = self._parse_date(date_text)
                        if post['date']:
                            break
            
            if post['content']:
                posts.append(post)
        
        return posts
    
    def close(self):
        """Clean up resources."""
        self._close_driver()