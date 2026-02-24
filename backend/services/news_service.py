"""
News Service
Fetches news articles from NewsAPI
"""

import requests
import os
import logging
from datetime import datetime, timedelta
from models.item import ContextualItem
from utils.cache import cache

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching news articles"""

    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        self.max_results = int(os.getenv('NEWS_MAX_RESULTS', 20))
        self.language = os.getenv('NEWS_LANGUAGE', 'en')
        self.cache_ttl = int(os.getenv('CACHE_NEWS_TIMEOUT', 1800))

    def get_news_items(self, location, date):
        """
        Get news-related contextual items

        Args:
            location: Location object
            date: Date string (YYYY-MM-DD)

        Returns:
            List of ContextualItem objects
        """
        items = []

        # Check cache
        cache_key = f"news:{location.city}:{date}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"News cache hit for {location.city}")
            return [ContextualItem(**item) for item in cached]

        # If no API key, return mock data
        if not self.api_key:
            logger.warning("No NEWS_API_KEY set, using mock data")
            items = self._get_mock_news(location)
        else:
            try:
                # Get local news
                local_news = self._fetch_local_news(location, date)
                if local_news:
                    items.extend(local_news)

                # Get top headlines (global/national)
                headlines = self._fetch_top_headlines(date)
                if headlines:
                    items.extend(headlines[:3])  # Limit to top 3

            except Exception as e:
                logger.error(f"News service error: {str(e)}")
                items = self._get_mock_news(location)

        # Cache the results
        if items:
            cache.set(cache_key, [item.to_dict() for item in items], self.cache_ttl)

        return items

    def _fetch_local_news(self, location, date):
        """Fetch local news for the location"""
        try:
            url = f"{self.base_url}/everything"

            # Search for city-related news
            query = f"{location.city} OR {location.state}"

            params = {
                'q': query,
                'from': date,
                'to': date,
                'sortBy': 'relevancy',
                'language': self.language,
                'pageSize': 10,
                'apiKey': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_news_articles(data.get('articles', []), 'local_news')

        except requests.exceptions.RequestException as e:
            logger.error(f"Local news API error: {str(e)}")
            return []

    def _fetch_top_headlines(self, date):
        """Fetch top national/global headlines"""
        try:
            url = f"{self.base_url}/top-headlines"

            params = {
                'country': 'us',
                'pageSize': 5,
                'apiKey': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_news_articles(data.get('articles', []), 'global_news')

        except requests.exceptions.RequestException as e:
            logger.error(f"Headlines API error: {str(e)}")
            return []

    def _parse_news_articles(self, articles, category):
        """Parse news articles into ContextualItems"""
        items = []

        for article in articles:
            try:
                title = article.get('title', 'No title')
                description = article.get('description', '')

                # Skip if no meaningful content
                if not description or description == '[Removed]':
                    continue

                # Truncate long descriptions
                if len(description) > 200:
                    description = description[:197] + '...'

                item = ContextualItem(
                    title=title,
                    description=description,
                    category=category,
                    source=article.get('source', {}).get('name', 'Unknown'),
                    timestamp=article.get('publishedAt', datetime.utcnow().isoformat()),
                    metadata={
                        'url': article.get('url'),
                        'author': article.get('author')
                    }
                )
                items.append(item)

            except Exception as e:
                logger.error(f"Error parsing article: {str(e)}")
                continue

        return items

    def _get_mock_news(self, location):
        """Return mock news data for testing"""
        return [
            ContextualItem(
                title=f"Local Event in {location.city}",
                description=f"Community gathering scheduled in downtown {location.city}. Expected attendance over 500 people.",
                category='local_news',
                source='Local News (Mock)',
                timestamp=datetime.utcnow().isoformat(),
                metadata={}
            ),
            ContextualItem(
                title="National Technology Conference",
                description="Annual tech conference brings innovation leaders together to discuss future trends.",
                category='global_news',
                source='Tech News (Mock)',
                timestamp=datetime.utcnow().isoformat(),
                metadata={}
            )
        ]
