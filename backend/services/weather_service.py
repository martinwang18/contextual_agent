"""
Weather Service
Fetches weather data and alerts from OpenWeatherMap API
"""

import requests
import os
import logging
from datetime import datetime, timedelta
from models.item import ContextualItem
from utils.cache import cache

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data and alerts"""

    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.open_meteo_url = "https://archive-api.open-meteo.com/v1/archive"
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
            logger.info(f"Weather cache hit for {location.city} on date {date}")
            return [ContextualItem(**item) for item in cached]

        logger.info(f"Weather cache miss for {location.city} on date {date}, fetching new data")

        # If no API key, return mock data
        if not self.api_key:
            logger.warning("No WEATHER_API_KEY set, using mock data")
            items = self._get_mock_weather(location, date)
        else:
            try:
                # Parse the requested date
                request_date = datetime.strptime(date, '%Y-%m-%d').date()
                today = datetime.now().date()
                days_diff = (request_date - today).days

                logger.info(f"Weather service: requested_date={date}, today={today}, days_diff={days_diff}")

                # Determine which API to use based on date
                if days_diff == 0:
                    # Today: get current weather
                    logger.info(f"Fetching current weather for today")
                    weather_data = self._fetch_current_weather(location)
                    if weather_data:
                        items.extend(self._parse_weather_data(weather_data, location, date))
                elif days_diff > 0 and days_diff <= 5:
                    # Future (1-5 days): get forecast
                    logger.info(f"Fetching weather forecast for {days_diff} days ahead")
                    forecast_data = self._fetch_weather_forecast(location, days_diff)
                    if forecast_data:
                        items.extend(self._parse_forecast_data(forecast_data, location, date, days_diff))
                    else:
                        # Fallback to current if forecast fails
                        logger.warning(f"Forecast fetch failed, falling back to current weather")
                        weather_data = self._fetch_current_weather(location)
                        if weather_data:
                            items.extend(self._parse_weather_data(weather_data, location, date, is_forecast=True))
                else:
                    # Past: try to get historical data, or far future: use current weather with note
                    if days_diff < 0:
                        # Past date - try historical API
                        logger.info(f"Date is in the past, attempting to fetch historical weather")
                        historical_data = self._fetch_historical_weather(location, date)
                        if historical_data:
                            items.extend(self._parse_historical_data(historical_data, location, date))
                        else:
                            # Fallback to current weather if historical API fails
                            logger.warning(f"Historical API failed, falling back to current weather")
                            weather_data = self._fetch_current_weather(location)
                            if weather_data:
                                items.extend(self._parse_weather_data(weather_data, location, date, is_historical=True))
                    else:
                        # Far future: use current weather with note
                        logger.info(f"Date is far in the future, using current weather with note")
                        weather_data = self._fetch_current_weather(location)
                        if weather_data:
                            items.extend(self._parse_weather_data(weather_data, location, date, is_historical=True))

                # Get weather alerts (if available)
                alerts = self._fetch_weather_alerts(location)
                if alerts:
                    items.extend(alerts)

            except Exception as e:
                logger.error(f"Weather service error: {str(e)}")
                items = self._get_mock_weather(location, date)

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

    def _fetch_weather_forecast(self, location, days_ahead):
        """Fetch weather forecast from API"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.api_key,
                'units': self.units,
                'cnt': 40  # Get 5 days of 3-hour forecasts
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather forecast API error: {str(e)}")
            return None

    def _fetch_historical_weather(self, location, date):
        """Fetch historical weather from Open-Meteo API (free, no API key required)"""
        try:
            url = self.open_meteo_url
            params = {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'start_date': date,
                'end_date': date,
                'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean,weathercode,precipitation_sum',
                'temperature_unit': 'fahrenheit',
                'timezone': 'auto'
            }

            logger.info(f"Fetching historical weather from Open-Meteo for {date}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Open-Meteo historical weather API error: {str(e)}")
            return None

    def _fetch_weather_alerts(self, location):
        """Fetch weather alerts (requires One Call API)"""
        # Note: One Call API 3.0 requires subscription
        # For MVP, we'll skip this or use mock data
        return []

    def _parse_weather_data(self, data, location, date, is_forecast=False, is_historical=False):
        """Parse weather API response into ContextualItems"""
        items = []

        try:
            # Main weather condition
            weather = data.get('weather', [{}])[0]
            main = data.get('main', {})

            temp = main.get('temp', 0)
            feels_like = main.get('feels_like', 0)
            description = weather.get('description', 'unknown')

            # Add context based on date type
            date_context = ""
            if is_historical:
                date_context = " (Current weather shown - historical data not available)"
            elif is_forecast:
                date_context = " (Forecast unavailable - showing current weather)"

            # Create weather item
            item = ContextualItem(
                title=f"Weather in {location.city}{date_context}",
                description=f"{description.capitalize()}, {int(temp)}°F (feels like {int(feels_like)}°F)",
                category='weather',
                source='OpenWeatherMap',
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'temperature': temp,
                    'feels_like': feels_like,
                    'humidity': main.get('humidity'),
                    'condition': weather.get('main'),
                    'requested_date': date
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

    def _parse_forecast_data(self, data, location, date, days_ahead):
        """Parse forecast API response for a specific date"""
        items = []

        try:
            forecast_list = data.get('list', [])
            if not forecast_list:
                return items

            # Find forecasts for the target day
            # Each forecast is 3 hours apart, so we look for forecasts around noon
            target_forecasts = []
            for forecast in forecast_list:
                forecast_dt = datetime.fromtimestamp(forecast.get('dt', 0))
                forecast_date = forecast_dt.date()
                request_date = datetime.strptime(date, '%Y-%m-%d').date()

                if forecast_date == request_date:
                    target_forecasts.append(forecast)

            if target_forecasts:
                # Use midday forecast (closest to noon) or average
                midday_forecast = None
                for fc in target_forecasts:
                    fc_time = datetime.fromtimestamp(fc.get('dt', 0))
                    if 11 <= fc_time.hour <= 14:  # Between 11 AM and 2 PM
                        midday_forecast = fc
                        break

                if not midday_forecast:
                    midday_forecast = target_forecasts[len(target_forecasts)//2]

                weather = midday_forecast.get('weather', [{}])[0]
                main = midday_forecast.get('main', {})

                temp = main.get('temp', 0)
                feels_like = main.get('feels_like', 0)
                description = weather.get('description', 'unknown')

                item = ContextualItem(
                    title=f"Weather Forecast for {location.city}",
                    description=f"{description.capitalize()}, {int(temp)}°F (feels like {int(feels_like)}°F) - {days_ahead} day{'s' if days_ahead > 1 else ''} ahead",
                    category='weather',
                    source='OpenWeatherMap Forecast',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={
                        'temperature': temp,
                        'feels_like': feels_like,
                        'humidity': main.get('humidity'),
                        'condition': weather.get('main'),
                        'requested_date': date,
                        'is_forecast': True,
                        'days_ahead': days_ahead
                    }
                )
                items.append(item)

                # Check for extreme temperatures in forecast
                if temp > 95:
                    extreme_item = ContextualItem(
                        title=f"Forecasted Extreme Heat - {int(temp)}°F",
                        description=f"High temperature expected in {location.city}. Plan for heat safety measures.",
                        category='weather_alert',
                        source='OpenWeatherMap Forecast',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={'severity': 'high', 'temperature': temp, 'is_forecast': True}
                    )
                    items.append(extreme_item)
                elif temp < 32:
                    extreme_item = ContextualItem(
                        title=f"Forecasted Freezing Temperature - {int(temp)}°F",
                        description=f"Below freezing temperature expected in {location.city}. Prepare for cold weather.",
                        category='weather_alert',
                        source='OpenWeatherMap Forecast',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={'severity': 'medium', 'temperature': temp, 'is_forecast': True}
                    )
                    items.append(extreme_item)

        except Exception as e:
            logger.error(f"Error parsing forecast data: {str(e)}")

        return items

    def _parse_historical_data(self, data, location, date):
        """Parse historical weather API response from Open-Meteo API"""
        items = []

        try:
            # Open-Meteo returns daily data arrays
            daily = data.get('daily', {})

            if not daily or not daily.get('time'):
                logger.warning("No historical data found in Open-Meteo response")
                return items

            # Get the first (and only) day's data
            temp_max = daily.get('temperature_2m_max', [0])[0]
            temp_min = daily.get('temperature_2m_min', [0])[0]
            temp_mean = daily.get('temperature_2m_mean', [0])[0]
            weather_code = daily.get('weathercode', [0])[0]
            precipitation = daily.get('precipitation_sum', [0])[0]

            # Map weather code to description
            description = self._get_weather_description(weather_code)

            # Create historical weather item
            item = ContextualItem(
                title=f"Historical Weather in {location.city}",
                description=f"{description}, High: {int(temp_max)}°F, Low: {int(temp_min)}°F on {date}",
                category='weather',
                source='Open-Meteo',
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'temperature': temp_mean,
                    'temperature_max': temp_max,
                    'temperature_min': temp_min,
                    'precipitation': precipitation,
                    'weather_code': weather_code,
                    'condition': description,
                    'requested_date': date,
                    'is_historical': True
                }
            )
            items.append(item)

            # Check for extreme temperatures in historical data
            if temp_max > 95:
                extreme_item = ContextualItem(
                    title=f"Extreme Heat on {date} - {int(temp_max)}°F",
                    description=f"Very high temperature was recorded in {location.city} on this date.",
                    category='weather_alert',
                    source='Open-Meteo',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={'severity': 'high', 'temperature': temp_max, 'is_historical': True}
                )
                items.append(extreme_item)
            elif temp_min < 32:
                extreme_item = ContextualItem(
                    title=f"Freezing Temperature on {date} - {int(temp_min)}°F",
                    description=f"Below freezing temperature was recorded in {location.city} on this date.",
                    category='weather_alert',
                    source='Open-Meteo',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={'severity': 'medium', 'temperature': temp_min, 'is_historical': True}
                )
                items.append(extreme_item)

        except Exception as e:
            logger.error(f"Error parsing Open-Meteo historical data: {str(e)}")

        return items

    def _get_weather_description(self, code):
        """Map Open-Meteo weather code to description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")

    def _get_mock_weather(self, location, date=None):
        """Return mock weather data for testing"""
        date_note = f" for {date}" if date else ""
        return [
            ContextualItem(
                title=f"Weather in {location.city}{date_note}",
                description="Partly cloudy, 72°F (feels like 70°F) - Mock data",
                category='weather',
                source='OpenWeatherMap (Mock)',
                timestamp=datetime.utcnow().isoformat(),
                metadata={
                    'temperature': 72,
                    'feels_like': 70,
                    'condition': 'Clouds',
                    'requested_date': date
                }
            )
        ]
