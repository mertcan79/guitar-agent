import logging
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests

from .base_scraper import BaseScraper
from ..config import config

logger = logging.getLogger(__name__)

class ReverbScraper(BaseScraper):
    """Scraper for Reverb.com guitar listings"""
    
    BASE_URL = "https://reverb.com/marketplace/electric-guitars"
    
    def __init__(self, headless: bool = True):
        super().__init__(
            cache_enabled=config.ENABLE_CACHE,
            cache_expiry_minutes=config.CACHE_EXPIRY_MINUTES
        )
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={config.USER_AGENT}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Reverb.com for guitars"""
        try:
            # Use simpler requests-based approach first
            return self._search_with_requests(search_params)
        except Exception as e:
            logger.warning(f"Requests-based search failed: {e}, falling back to Selenium")
            return self._search_with_selenium(search_params)
    
    def _search_with_requests(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Lighter weight search using requests and BeautifulSoup"""
        guitars = []
        
        # Build URL parameters
        params = {
            'price_min': search_params.get('min_price', config.DEFAULT_MIN_PRICE),
            'price_max': search_params.get('max_price', config.DEFAULT_MAX_PRICE),
        }
        
        # Add brand filter
        if search_params.get('brands') and isinstance(search_params['brands'], list) and search_params['brands']:
            params['make'] = search_params['brands'][0].lower()
        
        # Add search query
        if search_params.get('search_terms') and isinstance(search_params['search_terms'], list) and search_params['search_terms']:
            params['query'] = ' '.join(search_params['search_terms'])
        
        headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                timeout=config.SCRAPE_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listings = soup.find_all('div', attrs={'data-testid': 'listing-card'})
            if not listings:
                # Try alternative selectors
                listings = soup.find_all('article', class_='listing-card')
            
            max_results = search_params.get('max_results', config.MAX_SEARCH_RESULTS)
            
            for listing in listings[:max_results]:
                guitar_info = self._extract_guitar_info_from_soup(listing)
                if guitar_info:
                    guitars.append(guitar_info)
            
            logger.info(f"Found {len(guitars)} guitars using requests")
            
        except Exception as e:
            logger.error(f"Request-based search error: {e}")
            raise
        
        return guitars
    
    def _search_with_selenium(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback search using Selenium for dynamic content"""
        guitars = []
        
        try:
            self._init_driver()
            
            # Build URL with parameters
            url_params = []
            if search_params.get('min_price'):
                url_params.append(f"price_min={search_params['min_price']}")
            if search_params.get('max_price'):
                url_params.append(f"price_max={search_params['max_price']}")
            if search_params.get('brands') and isinstance(search_params['brands'], list) and search_params['brands']:
                brand = search_params['brands'][0].lower().replace(' ', '-')
                url_params.append(f"make={brand}")
            
            full_url = self.BASE_URL
            if url_params:
                full_url += "?" + "&".join(url_params)
            
            logger.info(f"Searching URL: {full_url}")
            
            self.driver.get(full_url)
            
            # Wait for listings to load
            wait = WebDriverWait(self.driver, config.SCRAPE_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="listing-card"], .listing-card')))
            
            # Scroll to load more results
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find listings
            listings = soup.find_all('div', attrs={'data-testid': 'listing-card'})
            if not listings:
                listings = soup.find_all('article', class_='listing-card')
            
            max_results = search_params.get('max_results', config.MAX_SEARCH_RESULTS)
            
            for listing in listings[:max_results]:
                guitar_info = self._extract_guitar_info_from_soup(listing)
                if guitar_info:
                    guitars.append(guitar_info)
            
            logger.info(f"Found {len(guitars)} guitars using Selenium")
            
        except Exception as e:
            logger.error(f"Selenium search error: {e}")
        finally:
            self._close_driver()
        
        return guitars
    
    def _extract_guitar_info_from_soup(self, listing) -> Optional[Dict[str, Any]]:
        """Extract guitar information from BeautifulSoup element"""
        try:
            # Extract title
            title = None
            title_elem = listing.find(['h3', 'h4'], class_=lambda x: x and 'title' in x.lower() if x else False)
            if not title_elem:
                title_elem = listing.find('a', attrs={'data-testid': 'listing-title'})
            if not title_elem:
                title_elem = listing.find('h3')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Extract price
            price = None
            price_elem = listing.find(['span', 'div'], attrs={'data-testid': 'listing-price'})
            if not price_elem:
                price_elem = listing.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower() if x else False)
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self.clean_price(price_text)
            
            # Extract condition
            condition = "Unknown"
            condition_elem = listing.find(['span', 'div'], class_=lambda x: x and 'condition' in x.lower() if x else False)
            if condition_elem:
                condition = condition_elem.get_text(strip=True)
            
            # Extract image URL
            image_url = None
            img_elem = listing.find('img')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
            
            # Extract link
            link = None
            link_elem = listing.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = f"https://reverb.com{link}"
            
            if title and price:
                return {
                    'title': title,
                    'price': price,
                    'condition': condition,
                    'image_url': image_url,
                    'link': link,
                    'source': 'Reverb'
                }
            
        except Exception as e:
            logger.error(f"Error extracting guitar info: {e}")
        
        return None
    
    def extract_guitar_info(self, element: Any) -> Optional[Dict[str, Any]]:
        """Required by base class - delegates to soup extraction"""
        return self._extract_guitar_info_from_soup(element)