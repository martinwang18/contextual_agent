#!/usr/bin/env python3
"""
Quick test to verify Open-Meteo historical weather API integration
"""

import requests
from datetime import datetime

def test_open_meteo():
    """Test Open-Meteo API directly"""
    print("=" * 60)
    print("Testing Open-Meteo Historical Weather API")
    print("=" * 60)

    # Test parameters
    latitude = 40.7484  # New York City
    longitude = -73.9967
    date = "2026-01-25"

    print(f"\n📍 Location: NYC ({latitude}, {longitude})")
    print(f"📅 Date: {date}")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': date,
        'end_date': date,
        'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean,weathercode,precipitation_sum',
        'temperature_unit': 'fahrenheit',
        'timezone': 'auto'
    }

    print(f"\n🌐 API URL: {url}")
    print(f"📦 Parameters: {params}")

    try:
        print(f"\n⏳ Fetching data...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Success! Status code: {response.status_code}")
        print(f"\n📊 Response data:")

        if 'daily' in data:
            daily = data['daily']
            print(f"  🌡️  High: {daily.get('temperature_2m_max', [None])[0]}°F")
            print(f"  🌡️  Low: {daily.get('temperature_2m_min', [None])[0]}°F")
            print(f"  🌡️  Mean: {daily.get('temperature_2m_mean', [None])[0]}°F")
            print(f"  ☁️  Weather code: {daily.get('weathercode', [None])[0]}")
            print(f"  💧 Precipitation: {daily.get('precipitation_sum', [None])[0]} mm")

            # Map weather code
            weather_code = daily.get('weathercode', [0])[0]
            weather_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                95: "Thunderstorm"
            }
            description = weather_codes.get(weather_code, "Unknown")
            print(f"  📝 Description: {description}")

            return True
        else:
            print(f"  ⚠️  No 'daily' data in response")
            print(f"  Response: {data}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n")
    success = test_open_meteo()
    print("\n" + "=" * 60)
    if success:
        print("✅ Open-Meteo API test passed!")
        print("💡 The integration is working correctly!")
    else:
        print("❌ Open-Meteo API test failed")
    print("=" * 60 + "\n")
