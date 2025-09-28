import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_KEY', '')
    
    # Model Configuration
    LLM_MODEL = "gpt-4"
    FAST_LLM_MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.3
    MAX_TOKENS = 2000
    
    # Scraping Configuration
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    SCRAPE_TIMEOUT = 10
    MAX_RETRIES = 3
    
    # Search Configuration
    DEFAULT_MIN_PRICE = 300
    DEFAULT_MAX_PRICE = 2000
    MAX_SEARCH_RESULTS = 30
    
    # Cache Configuration
    ENABLE_CACHE = True
    CACHE_EXPIRY_MINUTES = 15
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_KEY not found in environment variables")
        return True

config = Config()