"""
Configuration Management
Loads and manages application configuration from environment variables
"""

import os


class Config:
    """Application configuration"""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Server configuration
    PORT = int(os.getenv('PORT', 8080))
    HOST = os.getenv('HOST', '0.0.0.0')

    # API Keys
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    GEOCODING_API_KEY = os.getenv('GEOCODING_API_KEY', '')
    EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN', '')

    # Cache configuration
    CACHE_WEATHER_TIMEOUT = int(os.getenv('CACHE_WEATHER_TIMEOUT', 3600))
    CACHE_NEWS_TIMEOUT = int(os.getenv('CACHE_NEWS_TIMEOUT', 1800))
    CACHE_GEOCODING_TIMEOUT = int(os.getenv('CACHE_GEOCODING_TIMEOUT', 86400))
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'

    # Feature flags
    ENABLE_WEATHER = os.getenv('ENABLE_WEATHER', 'True').lower() == 'true'
    ENABLE_NEWS = os.getenv('ENABLE_NEWS', 'True').lower() == 'true'
    ENABLE_EVENTS = os.getenv('ENABLE_EVENTS', 'False').lower() == 'true'

    # API settings
    NEWS_MAX_RESULTS = int(os.getenv('NEWS_MAX_RESULTS', 20))
    NEWS_LANGUAGE = os.getenv('NEWS_LANGUAGE', 'en')
    WEATHER_UNITS = os.getenv('WEATHER_UNITS', 'imperial')

    @staticmethod
    def validate():
        """Validate that required configuration is present"""
        warnings = []

        if not Config.WEATHER_API_KEY:
            warnings.append("⚠️  WEATHER_API_KEY not set - weather features will not work")

        if not Config.NEWS_API_KEY:
            warnings.append("⚠️  NEWS_API_KEY not set - news features will not work")

        if not Config.GEOCODING_API_KEY:
            warnings.append("⚠️  GEOCODING_API_KEY not set - location features will not work")

        if warnings:
            print("\n" + "="*60)
            print("Configuration Warnings:")
            for warning in warnings:
                print(f"  {warning}")
            print("="*60 + "\n")

        return len(warnings) == 0
