#!/usr/bin/env python3
"""
Test script to manually test weather service with specific date
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('config/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from services.weather_service import WeatherService
from services.geocoding_service import GeocodingService

def test_weather_date():
    """Test weather service with specific date"""
    print("=" * 60)
    print("Testing Weather Service with Date: 2/14/2026 (PAST - Historical)")
    print("=" * 60)

    # Initialize services
    geocoding = GeocodingService()
    weather = WeatherService()

    # Test parameters
    zipcode = "10001"
    date = "2026-02-14"  # February 14, 2026 - Valentine's Day (past)

    print(f"\n1. Geocoding zipcode: {zipcode}")
    location = geocoding.get_location(zipcode)
    print(f"   Location: {location.city}, {location.state}")
    print(f"   Coordinates: {location.latitude}, {location.longitude}")

    print(f"\n2. Testing weather service for date: {date}")

    # Calculate days difference
    request_date = datetime.strptime(date, '%Y-%m-%d').date()
    today = datetime.now().date()
    days_diff = (request_date - today).days

    print(f"   Today: {today}")
    print(f"   Requested: {request_date}")
    print(f"   Days difference: {days_diff}")

    if days_diff < 0:
        print(f"   ⚠️  This is a PAST date ({abs(days_diff)} days ago)")
        print(f"   Expected: Current weather with historical note")
    elif days_diff == 0:
        print(f"   ✓ This is TODAY")
        print(f"   Expected: Current weather")
    elif days_diff > 0 and days_diff <= 5:
        print(f"   ✓ This is a FUTURE date ({days_diff} days ahead)")
        print(f"   Expected: Weather forecast")
    else:
        print(f"   ⚠️  This is FAR FUTURE ({days_diff} days ahead)")
        print(f"   Expected: Current weather with note")

    print(f"\n3. Fetching weather data...")
    try:
        weather_items = weather.get_weather_items(location, date)

        print(f"   ✓ Got {len(weather_items)} weather items")

        for idx, item in enumerate(weather_items):
            print(f"\n   Item {idx + 1}:")
            print(f"     Title: {item.title}")
            print(f"     Description: {item.description}")
            print(f"     Category: {item.category}")
            print(f"     Source: {item.source}")

            if item.metadata:
                print(f"     Metadata:")
                print(f"       - Temperature: {item.metadata.get('temperature')}°F")
                print(f"       - Requested date: {item.metadata.get('requested_date')}")
                print(f"       - Is forecast: {item.metadata.get('is_forecast', False)}")
                print(f"       - Days ahead: {item.metadata.get('days_ahead', 'N/A')}")

        return True

    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    success = test_weather_date()
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed!")
    else:
        print("❌ Test failed")
    print("=" * 60 + "\n")
