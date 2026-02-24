"""
Geocoding Service
Converts USA zipcodes to geographic coordinates and location information
"""

import requests
import os
import logging
from models.item import Location
from utils.cache import cache

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for converting zipcodes to geographic data"""

    def __init__(self):
        self.api_key = os.getenv('GEOCODING_API_KEY', '')
        self.base_url = "https://app.zipcodebase.com/api/v1"
        self.cache_ttl = int(os.getenv('CACHE_GEOCODING_TIMEOUT', 86400))

    def get_location(self, zipcode):
        """
        Convert zipcode to location information

        Args:
            zipcode: 5-digit USA zipcode

        Returns:
            Location object or None if failed
        """
        # Check cache first
        cache_key = f"geocoding:{zipcode}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Geocoding cache hit for {zipcode}")
            return Location(**cached)

        # If no API key, return mock data for testing
        if not self.api_key:
            logger.warning("No GEOCODING_API_KEY set, using mock data")
            return self._get_mock_location(zipcode)

        try:
            # Call Zipcodebase API
            url = f"{self.base_url}/search"
            params = {
                'apikey': self.api_key,
                'codes': zipcode,
                'country': 'US'
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            # Parse response
            if 'results' in data and zipcode in data['results']:
                result = data['results'][zipcode][0]

                location = Location(
                    zipcode=zipcode,
                    city=result.get('city', ''),
                    state=result.get('state', ''),
                    state_code=result.get('state_code', ''),
                    latitude=float(result.get('latitude', 0)),
                    longitude=float(result.get('longitude', 0))
                )

                # Cache the result
                cache.set(cache_key, location.to_dict(), self.cache_ttl)

                logger.info(f"Geocoded {zipcode} to {location.city}, {location.state_code}")
                return location
            else:
                logger.error(f"Invalid zipcode: {zipcode}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding API error: {str(e)}")
            return self._get_mock_location(zipcode)
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None

    def _get_mock_location(self, zipcode):
        """
        Return mock location data for testing

        Args:
            zipcode: Zipcode to mock

        Returns:
            Mock Location object
        """
        # Common test zipcodes
        mock_data = {
            '10001': {'city': 'New York', 'state': 'New York', 'state_code': 'NY', 'lat': 40.7506, 'lon': -73.9971},
            '90210': {'city': 'Beverly Hills', 'state': 'California', 'state_code': 'CA', 'lat': 34.0901, 'lon': -118.4065},
            '60601': {'city': 'Chicago', 'state': 'Illinois', 'state_code': 'IL', 'lat': 41.8857, 'lon': -87.6179},
            '02101': {'city': 'Boston', 'state': 'Massachusetts', 'state_code': 'MA', 'lat': 42.3708, 'lon': -71.0267},
            '98101': {'city': 'Seattle', 'state': 'Washington', 'state_code': 'WA', 'lat': 47.6101, 'lon': -122.3421}
        }

        if zipcode in mock_data:
            data = mock_data[zipcode]
            return Location(
                zipcode=zipcode,
                city=data['city'],
                state=data['state'],
                state_code=data['state_code'],
                latitude=data['lat'],
                longitude=data['lon']
            )

        # Default mock for unknown zipcodes
        return Location(
            zipcode=zipcode,
            city='Test City',
            state='Test State',
            state_code='TS',
            latitude=40.7128,
            longitude=-74.0060
        )
