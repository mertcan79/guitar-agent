"""
Mock guitar data for demonstration when live scraping is blocked
"""

from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper
import random

class MockGuitarScraper(BaseScraper):
    """Mock scraper that provides realistic guitar data for testing"""
    
    # Realistic guitar database for different brands and price ranges
    MOCK_GUITARS = {
        "fender": [
            {
                "title": "Fender Player Stratocaster - 3-Color Sunburst",
                "price": 899,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--Dt8zTpyh--/f_auto,t_large/v1234/fender-player-strat.jpg",
                "link": "https://reverb.com/item/12345-fender-player-stratocaster",
                "source": "Reverb"
            },
            {
                "title": "Fender American Professional II Stratocaster - Miami Blue",
                "price": 1699,
                "condition": "Mint",
                "image_url": "https://images.reverb.com/image/upload/s--abc123--/f_auto,t_large/v5678/fender-am-pro-ii.jpg",
                "link": "https://reverb.com/item/23456-fender-american-pro-ii",
                "source": "Reverb"
            },
            {
                "title": "Fender Player Telecaster - Butterscotch Blonde",
                "price": 849,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--def456--/f_auto,t_large/v9101/fender-tele.jpg",
                "link": "https://reverb.com/item/34567-fender-player-telecaster",
                "source": "Reverb"
            },
            {
                "title": "Fender Vintera '60s Stratocaster - Olympic White",
                "price": 1149,
                "condition": "Very Good",
                "image_url": "https://images.reverb.com/image/upload/s--ghi789--/f_auto,t_large/v1112/fender-vintera.jpg",
                "link": "https://reverb.com/item/45678-fender-vintera-60s",
                "source": "Reverb"
            },
            {
                "title": "Fender American Ultra Stratocaster - Texas Tea",
                "price": 2199,
                "condition": "Mint",
                "image_url": "https://images.reverb.com/image/upload/s--jkl012--/f_auto,t_large/v1314/fender-ultra.jpg",
                "link": "https://reverb.com/item/56789-fender-american-ultra",
                "source": "Reverb"
            }
        ],
        "gibson": [
            {
                "title": "Gibson Les Paul Standard 50s - Heritage Cherry Sunburst",
                "price": 2699,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--mno345--/f_auto,t_large/v1516/gibson-lp-std.jpg",
                "link": "https://reverb.com/item/67890-gibson-les-paul-standard",
                "source": "Reverb"
            },
            {
                "title": "Gibson Les Paul Studio - Ebony",
                "price": 1599,
                "condition": "Very Good",
                "image_url": "https://images.reverb.com/image/upload/s--pqr678--/f_auto,t_large/v1718/gibson-studio.jpg",
                "link": "https://reverb.com/item/78901-gibson-les-paul-studio",
                "source": "Reverb"
            },
            {
                "title": "Gibson SG Standard - Cherry Red",
                "price": 1899,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--stu901--/f_auto,t_large/v1920/gibson-sg.jpg",
                "link": "https://reverb.com/item/89012-gibson-sg-standard",
                "source": "Reverb"
            }
        ],
        "epiphone": [
            {
                "title": "Epiphone Les Paul Standard 50s - Heritage Cherry Sunburst",
                "price": 649,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--vwx234--/f_auto,t_large/v2122/epi-lp-std.jpg",
                "link": "https://reverb.com/item/90123-epiphone-les-paul-standard",
                "source": "Reverb"
            },
            {
                "title": "Epiphone Casino - Natural",
                "price": 849,
                "condition": "Very Good",
                "image_url": "https://images.reverb.com/image/upload/s--yz567--/f_auto,t_large/v2324/epi-casino.jpg",
                "link": "https://reverb.com/item/01234-epiphone-casino",
                "source": "Reverb"
            }
        ],
        "prs": [
            {
                "title": "PRS SE Custom 24 - Vintage Sunburst",
                "price": 929,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--abc890--/f_auto,t_large/v2526/prs-se-24.jpg",
                "link": "https://reverb.com/item/12345-prs-se-custom-24",
                "source": "Reverb"
            },
            {
                "title": "PRS S2 Custom 24 - Frost Blue Metallic",
                "price": 1599,
                "condition": "Mint",
                "image_url": "https://images.reverb.com/image/upload/s--def123--/f_auto,t_large/v2728/prs-s2.jpg",
                "link": "https://reverb.com/item/23456-prs-s2-custom-24",
                "source": "Reverb"
            }
        ],
        "ibanez": [
            {
                "title": "Ibanez RG550 - Desert Sun Yellow",
                "price": 1099,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--ghi456--/f_auto,t_large/v2930/ibanez-rg550.jpg",
                "link": "https://reverb.com/item/34567-ibanez-rg550",
                "source": "Reverb"
            },
            {
                "title": "Ibanez RG7321 7-String - Black",
                "price": 1599,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--metal123--/f_auto,t_large/v4567/ibanez-rg7321.jpg",
                "link": "https://reverb.com/item/56789-ibanez-rg7321",
                "source": "Reverb"
            },
            {
                "title": "Ibanez Artcore AS73 - Tobacco Brown",
                "price": 449,
                "condition": "Very Good",
                "image_url": "https://images.reverb.com/image/upload/s--jkl789--/f_auto,t_large/v3132/ibanez-as73.jpg",
                "link": "https://reverb.com/item/45678-ibanez-artcore-as73",
                "source": "Reverb"
            }
        ],
        "schecter": [
            {
                "title": "Schecter Hellraiser C-1 - Satin Black",
                "price": 1749,
                "condition": "Mint",
                "image_url": "https://images.reverb.com/image/upload/s--schecter01--/f_auto,t_large/v5678/schecter-hellraiser.jpg",
                "link": "https://reverb.com/item/78901-schecter-hellraiser-c1",
                "source": "Reverb"
            },
            {
                "title": "Schecter Omen Extreme-6 FR - See Thru Black Cherry",
                "price": 1299,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--schecter02--/f_auto,t_large/v6789/schecter-omen.jpg",
                "link": "https://reverb.com/item/89012-schecter-omen-extreme",
                "source": "Reverb"
            }
        ],
        "esp": [
            {
                "title": "ESP LTD EC-1000 - Black",
                "price": 1799,
                "condition": "Excellent",
                "image_url": "https://images.reverb.com/image/upload/s--esp001--/f_auto,t_large/v7890/esp-ec1000.jpg",
                "link": "https://reverb.com/p/esp-ltd-ec-1000-black",
                "source": "Reverb"
            },
            {
                "title": "ESP LTD MH-1000 Floyd Rose - Violet Andromeda",
                "price": 900,
                "condition": "Mint",
                "image_url": "https://images.reverb.com/image/upload/s--esp002--/f_auto,t_large/v8901/esp-mh1000.jpg",
                "link": "https://www.espguitars.com/products/22751-mh-1000",
                "source": "ESP Guitars"
            }
        ]
    }
    
    def __init__(self):
        super().__init__(cache_enabled=False)  # No caching needed for mock data
    
    def search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return mock guitar data based on search parameters"""
        
        min_price = search_params.get('min_price', 0)
        max_price = search_params.get('max_price', 10000)
        brands = search_params.get('brands', [])
        max_results = search_params.get('max_results', 20)
        
        # Collect guitars from specified brands
        available_guitars = []
        
        if brands:
            for brand in brands:
                brand_lower = brand.lower()
                if brand_lower in self.MOCK_GUITARS:
                    available_guitars.extend(self.MOCK_GUITARS[brand_lower])
        else:
            # If no brands specified, include all guitars
            for brand_guitars in self.MOCK_GUITARS.values():
                available_guitars.extend(brand_guitars)
        
        # Filter by price
        filtered_guitars = [
            guitar for guitar in available_guitars
            if min_price <= guitar['price'] <= max_price
        ]
        
        # Add some price variation to simulate market conditions
        for guitar in filtered_guitars:
            # Add ±5% price variation to simulate real market
            variation = random.uniform(0.95, 1.05)
            guitar['price'] = round(guitar['price'] * variation)
        
        # Shuffle and limit results
        random.shuffle(filtered_guitars)
        return filtered_guitars[:max_results]
    
    def extract_guitar_info(self, element: Any) -> Optional[Dict[str, Any]]:
        """Not used in mock implementation"""
        return None