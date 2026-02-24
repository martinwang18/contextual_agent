"""
Weather Service
Fetches weather data and alerts from OpenWeatherMap API
"""

import requests
import os
import logging
from datetime import datetime
from models.item import ContextualItem
from utils.cache import cache

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data and alerts"""

    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.units = os.getenv('WEATHER_UNITS', 'imperial')
        self.cache_ttl = int(os.getenv('CACHE_WEATHER_TIMEOUT', 3600))

    def get_weather_items(self, location, date):
        """
        Get weather-related contextual items

        Args:
            location: Location object with coordinates
            date: Date string (YYYY-MM-DD)

        Returns:
            List of ContextualItem objects
        """
        items = []

        # Check cache
        cache_key = f"weather:{location.zipcode}:{date}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Weather cache hit for {location.city}")
            return [ContextualItem(**item) for item in cached]

        # If no API key, return mock data
        if not self.api_key:
            logger.warning("No WEATHER_API_KEY set, using mock data")
            items = self._get_mock_weather(location)
        else:
            try:
                # Get current weather
                weather_data = self._fetch_current_weather(location)
                if weather_data:
                    items.extend(self._parse_weather_data(weather_data, location))

                # Get weather alerts (if available)
                alerts = self._fetch_weather_alerts(location)
                if alerts:
                    items.extend(alerts)

            except Exception as e:
                logger.error(f"Weather service error: {str(e)}")
                items = self._get_mock_weather(location)

        # Cache the results
        if items:
            cache.set(cache_key, [item.to_dict() for item in items], self.cache_ttl)

        return items

    def _fetch_current_weather(self, location):
        """Fetch current weather from API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.api_key,
                'units': self.units
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {str(e)}")
            return None

    def _fetch_weather_alerts(self, location):
        """Fetch weather alerts (requires One Call API)"""
        # Note: One Call API 3.0 requires subscription
        # For MVP, we'll skip this or use mock data
        return []

    def _parse_weather_data(self, data, location):
        """Parse weather API response into ContextualItems"""
        items = []

        try:
            # Main weather condition
            weather = data.get('weather', [{}])[0]
            main = data.get('main', {})

            temp = main.get('temp', 0)
            feels_like = main.get('feels_like', 0)
            description = weather.get('description', 'unknown')

            # Create weather item
            item = ContextualItem(
                title=f"Weather in {location.city}",
                description=f"{description.capitalize()}, {int(temp)}°F (feels like {int(feels_like)}°F)",
                category='weather',
                source='OpenWeatherMap',
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'temperature': temp,
                    'feels_like': feels_like,
                    'humidity': main.get('humidity'),
                    'condition': weather.get('main')
                }
            )
            items.append(item)

            # Check for extreme temperatures
            if temp > 95:
                extreme_item = ContextualItem(
                    title=f"Extreme Heat Warning - {int(temp)}°F",
                    description=f"Very high temperature in {location.city}. Stay hydrated and avoid prolonged sun exposure.",
                    category='weather_alert',
                    source='OpenWeatherMap',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={'severity': 'high', 'temperature': temp}
                )
                items.append(extreme_item)
            elif temp < 32:
                extreme_item = ContextualItem(
                    title=f"Freezing Temperature - {int(temp)}°F",
                    description=f"Below freezing temperature in {location.city}. Dress warmly and watch for ice.",
                    category='weather_alert',
                    source='OpenWeatherMap',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={'severity': 'medium', 'temperature': temp}
                )
                items.append(extreme_item)

        except Exception as e:
            logger.error(f"Error parsing weather data: {str(e)}")

        return items

    def _get_mock_weather(self, location):
        """Return mock weather data for testing"""
        return [
            ContextualItem(
                title=f"Weather in {location.city}",
                description="Partly cloudy, 72°F (feels like 70°F)",
                category='weather',
                source='OpenWeatherMap (Mock)',
                timestamp=datetime.utcnow().isoformat(),
                metadata={'temperature': 72, 'feels_like': 70, 'condition': 'Clouds'}
            )
        ]
