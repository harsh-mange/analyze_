import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Stock Analyzer application."""
    
    # Default stock settings
    DEFAULT_STOCK_SYMBOL = os.getenv('DEFAULT_STOCK_SYMBOL', 'RELIANCE.NS')
    HISTORICAL_DAYS = int(os.getenv('HISTORICAL_DAYS', '60'))
    
    # API settings
    YAHOO_FINANCE_TIMEOUT = int(os.getenv('YAHOO_FINANCE_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Streamlit settings
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    STREAMLIT_SERVER_HEADLESS = os.getenv('STREAMLIT_SERVER_HEADLESS', 'true').lower() == 'true'
    STREAMLIT_BROWSER_GATHER_USAGE_STATS = os.getenv('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false').lower() == 'true'
    STREAMLIT_SERVER_ENABLE_CORS = os.getenv('STREAMLIT_SERVER_ENABLE_CORS', 'true').lower() == 'true'
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = os.getenv('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', 'true').lower() == 'true'
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cache settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
    
    # Security settings
    ENABLE_DEBUG = os.getenv('ENABLE_DEBUG', 'false').lower() == 'true'
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
    
    @classmethod
    def get_streamlit_config(cls):
        """Get Streamlit configuration as a dictionary."""
        return {
            'server.port': cls.STREAMLIT_SERVER_PORT,
            'server.address': cls.STREAMLIT_SERVER_ADDRESS,
            'server.headless': cls.STREAMLIT_SERVER_HEADLESS,
            'browser.gatherUsageStats': cls.STREAMLIT_BROWSER_GATHER_USAGE_STATS,
            'server.enableCORS': cls.STREAMLIT_SERVER_ENABLE_CORS,
            'server.enableXsrfProtection': cls.STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION,
        } 