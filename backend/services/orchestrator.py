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
from services.holidays_service import HolidaysService
from models.item import SearchResult

logger = logging.getLogger(__name__)


class ContextualOrchestrator:
    """Orchestrates the gathering and ranking of contextual information"""

    def __init__(self):
        self.geocoding = GeocodingService()
        self.weather = WeatherService()
        self.news = NewsService()
        self.holidays = HolidaysService()
        self.ranking = RankingService()

    def get_contextual_items(self, zipcode, date):
        """
        Main orchestration method

        Args:
            zipcode: USA zipcode (5 digits)
            date: Date string (YYYY-MM-DD)

        Returns:
            dict: SearchResult as dictionary with categorized results
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

            # Step 3: Rank items and get top 5 (backward compatibility)
            top_items = self.ranking.rank_items(all_items, date)

            # Step 4: Categorize items for granular view
            categorized = self._categorize_items(all_items, date)
            logger.info(f"Categorized data keys: {list(categorized.keys())}")
            logger.info(f"Weather: {len(categorized['weather'])}, Local: {len(categorized['local_news'])}, National: {len(categorized['national_news'])}")

            # Step 5: Format response
            result = SearchResult(
                status='success',
                query={
                    'zipcode': zipcode,
                    'date': date,
                    'location': f"{location.city}, {location.state_code}"
                },
                results=top_items,
                metadata={
                    'total_items_analyzed': len(all_items),
                    'categorized': categorized  # Add categorized view
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

    def _categorize_items(self, items, query_date=None):
        """
        Categorize and rank items by type

        Args:
            items: List of all ContextualItems
            query_date: Date string for relevance scoring

        Returns:
            dict: Categorized and ranked items
        """
        logger.info(f"Categorizing {len(items)} items")

        # Separate items by category
        weather_items = []
        local_news = []
        national_news = []
        holidays = []

        for item in items:
            # Score each item
            item.score = self.ranking._calculate_score(item, query_date)

            if item.category in ['weather', 'weather_alert', 'severe_weather']:
                weather_items.append(item)
            elif item.category in ['local_news', 'local_event']:
                local_news.append(item)
            elif item.category in ['global_news', 'regional_news']:
                national_news.append(item)
            elif item.category in ['holiday', 'event']:
                holidays.append(item)

        # Sort each category by score
        weather_items.sort(key=lambda x: x.score, reverse=True)
        local_news.sort(key=lambda x: x.score, reverse=True)
        national_news.sort(key=lambda x: x.score, reverse=True)
        holidays.sort(key=lambda x: x.score, reverse=True)

        # Return categorized results
        return {
            'holidays': [item.to_dict() for item in holidays],
            'weather': [item.to_dict() for item in weather_items],
            'local_news': [item.to_dict() for item in local_news[:10]],  # Top 10
            'national_news': [item.to_dict() for item in national_news[:10]]  # Top 10
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

        # Get holidays first (fast, no API call)
        holiday_items = self.holidays.get_holidays(date, location)

        # Define tasks for parallel execution
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

        # Add holiday items
        all_items.extend(holiday_items)
        if holiday_items:
            logger.info(f"holidays returned {len(holiday_items)} items")

        return all_items
