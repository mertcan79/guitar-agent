from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all guitar website scrapers"""
    
    def __init__(self, cache_enabled: bool = True, cache_expiry_minutes: int = 15):
        self.cache = {}
        self.cache_enabled = cache_enabled
        self.cache_expiry = timedelta(minutes=cache_expiry_minutes)
    
    @abstractmethod
    def search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for guitars based on parameters"""
        pass
    
    @abstractmethod
    def extract_guitar_info(self, element: Any) -> Optional[Dict[str, Any]]:
        """Extract guitar information from a page element"""
        pass
    
    def _get_cache_key(self, params: Dict[str, Any]) -> str:
        """Generate cache key from search parameters"""
        # Convert lists to tuples to make them hashable
        hashable_params = {}
        for key, value in params.items():
            if isinstance(value, list):
                hashable_params[key] = tuple(value)
            else:
                hashable_params[key] = value
        
        items = sorted(hashable_params.items())
        return f"{self.__class__.__name__}_{hash(tuple(items))}"
    
    def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Get results from cache if still valid"""
        if not self.cache_enabled:
            return None
        
        if key in self.cache:
            cached_time, cached_data = self.cache[key]
            if datetime.now() - cached_time < self.cache_expiry:
                logger.info(f"Cache hit for key: {key}")
                return cached_data
            else:
                del self.cache[key]
        return None
    
    def _save_to_cache(self, key: str, data: List[Dict[str, Any]]):
        """Save results to cache"""
        if self.cache_enabled:
            self.cache[key] = (datetime.now(), data)
            logger.info(f"Cached results for key: {key}")
    
    def search_with_cache(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search with caching support"""
        cache_key = self._get_cache_key(search_params)
        
        # Try to get from cache
        cached_results = self._get_from_cache(cache_key)
        if cached_results is not None:
            return cached_results
        
        # Perform actual search
        results = self.search(search_params)
        
        # Save to cache
        self._save_to_cache(cache_key, results)
        
        return results
    
    @staticmethod
    def clean_price(price_text: str) -> Optional[float]:
        """Convert price text to float"""
        if not price_text:
            return None
        
        import re
        price_text = price_text.replace('$', '').replace(',', '')
        match = re.search(r'[\d.]+', price_text)
        
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None