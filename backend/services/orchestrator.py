"""
Contextual Orchestrator
Coordinates all services to gather, rank, and return contextual items
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.geocoding_service import GeocodingService
from services.weather_service import WeatherService
from services.news_service import NewsService
from services.ranking_service import RankingService
from models.item import SearchResult

logger = logging.getLogger(__name__)


class ContextualOrchestrator:
    """Orchestrates the gathering and ranking of contextual information"""

    def __init__(self):
        self.geocoding = GeocodingService()
        self.weather = WeatherService()
        self.news = NewsService()
        self.ranking = RankingService()

    def get_contextual_items(self, zipcode, date):
        """
        Main orchestration method

        Args:
            zipcode: USA zipcode (5 digits)
            date: Date string (YYYY-MM-DD)

        Returns:
            dict: SearchResult as dictionary
        """
        try:
            # Step 1: Geocode the zipcode
            logger.info(f"Geocoding zipcode: {zipcode}")
            location = self.geocoding.get_location(zipcode)

            if not location:
                return {
                    'status': 'error',
                    'error': 'Invalid zipcode or geocoding failed',
                    'query': {'zipcode': zipcode, 'date': date},
                    'results': []
                }

            # Step 2: Gather data from all sources in parallel
            logger.info(f"Gathering contextual data for {location.city}, {location.state_code}")
            all_items = self._gather_data_parallel(location, date)

            logger.info(f"Gathered {len(all_items)} total items")

            # Step 3: Rank items and get top 5
            top_items = self.ranking.rank_items(all_items, date)

            # Step 4: Format response
            result = SearchResult(
                status='success',
                query={
                    'zipcode': zipcode,
                    'date': date,
                    'location': f"{location.city}, {location.state_code}"
                },
                results=top_items,
                metadata={
                    'total_items_analyzed': len(all_items)
                }
            )

            return result.to_dict()

        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'query': {'zipcode': zipcode, 'date': date},
                'results': []
            }

    def _gather_data_parallel(self, location, date):
        """
        Gather data from all sources in parallel

        Args:
            location: Location object
            date: Date string

        Returns:
            List of all ContextualItems
        """
        all_items = []

        # Define tasks
        tasks = {
            'weather': lambda: self.weather.get_weather_items(location, date),
            'news': lambda: self.news.get_news_items(location, date)
        }

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_service = {
                executor.submit(task): name
                for name, task in tasks.items()
            }

            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    items = future.result()
                    logger.info(f"{service_name} returned {len(items)} items")
                    all_items.extend(items)
                except Exception as e:
                    logger.error(f"Error in {service_name}: {str(e)}")

        return all_items
